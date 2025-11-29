#!/bin/bash
# =============================================================================
# Orange Pi 5 Max - Local LLM with RAG System Setup Script
# =============================================================================
# This script sets up a complete local LLM environment with RAG capabilities
# on Orange Pi 5 Max (16GB RAM recommended)
# =============================================================================

set -e

# Configuration - can be overridden by environment variables
REPO_URL="${REPO_URL:-https://github.com/l0kifs/opi5-max-llm-setup.git}"
DEFAULT_MODEL="${DEFAULT_MODEL:-qwen2.5:3b}"
PROJECT_DIR="${PROJECT_DIR:-${HOME}/opi5-max-llm-setup}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Check if running on ARM64
check_architecture() {
    print_header "Checking System Architecture"
    
    ARCH=$(uname -m)
    if [[ "$ARCH" != "aarch64" ]]; then
        print_warn "This script is designed for ARM64 (aarch64) architecture."
        print_warn "Current architecture: $ARCH"
        read -p "Continue anyway? (y/N): " confirm
        if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
            exit 1
        fi
    else
        print_msg "Architecture: $ARCH ✓"
    fi
}

# Check available RAM
check_ram() {
    print_header "Checking Available RAM"
    
    TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
    print_msg "Total RAM: ${TOTAL_RAM}GB"
    
    if [[ $TOTAL_RAM -lt 8 ]]; then
        print_warn "Less than 8GB RAM detected. Some models may not run properly."
    elif [[ $TOTAL_RAM -lt 16 ]]; then
        print_msg "8-16GB RAM detected. Use smaller models (3B-7B) for best results."
    else
        print_msg "16GB+ RAM detected. Full model support available. ✓"
    fi
}

# Update system packages
update_system() {
    print_header "Updating System Packages"
    
    sudo apt update
    sudo apt upgrade -y
    
    print_msg "System updated ✓"
}

# Install system dependencies
install_dependencies() {
    print_header "Installing System Dependencies"
    
    sudo apt install -y \
        build-essential \
        git \
        curl \
        wget \
        htop \
        python3 \
        python3-pip \
        python3-venv
    
    print_msg "Dependencies installed ✓"
}

# Install UV (Python package manager)
install_uv() {
    print_header "Installing UV Package Manager"
    
    if command -v uv &> /dev/null; then
        print_msg "UV is already installed"
        uv --version
    else
        curl -LsSf https://astral.sh/uv/install.sh | sh
        
        # Add to PATH for current session
        export PATH="$HOME/.local/bin:$PATH"
        
        print_msg "UV installed ✓"
    fi
}

# Install Ollama
install_ollama() {
    print_header "Installing Ollama"
    
    if command -v ollama &> /dev/null; then
        print_msg "Ollama is already installed"
        ollama --version
    else
        curl -fsSL https://ollama.com/install.sh | sh
        print_msg "Ollama installed ✓"
    fi
    
    # Start Ollama service
    print_msg "Starting Ollama service..."
    
    # Check if systemd is available
    if command -v systemctl &> /dev/null; then
        sudo systemctl enable ollama || true
        sudo systemctl start ollama || true
    else
        # Start Ollama in background if systemd not available
        ollama serve &> /dev/null &
    fi
    
    # Wait for Ollama to start
    sleep 5
    
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_msg "Ollama is running ✓"
    else
        print_warn "Ollama may not be running. Check with: ollama serve"
    fi
}

# Pull recommended model
pull_model() {
    print_header "Pulling Recommended Model"
    
    print_msg "Pulling $DEFAULT_MODEL (this may take several minutes)..."
    
    if ollama pull "$DEFAULT_MODEL"; then
        print_msg "Model $DEFAULT_MODEL pulled successfully ✓"
    else
        print_warn "Failed to pull model. You can try manually with: ollama pull $DEFAULT_MODEL"
    fi
}

# Setup project directory
setup_project() {
    print_header "Setting Up Project"
    
    if [[ -d "$PROJECT_DIR" ]]; then
        print_msg "Project directory already exists: $PROJECT_DIR"
    else
        # If we're running from the repo, copy it
        if [[ -f "pyproject.toml" ]]; then
            cp -r . "$PROJECT_DIR"
        else
            print_msg "Creating project directory: $PROJECT_DIR"
            mkdir -p "$PROJECT_DIR"
            cd "$PROJECT_DIR"
            
            print_msg "Cloning repository from $REPO_URL..."
            git clone "$REPO_URL" .
        fi
    fi
    
    cd "$PROJECT_DIR"
    
    # Create data directories
    mkdir -p data/chroma_db data/uploads
    
    # Copy environment template if .env doesn't exist
    if [[ ! -f ".env" ]] && [[ -f ".env.example" ]]; then
        cp .env.example .env
        print_msg "Created .env from template"
    fi
    
    print_msg "Project directory ready: $PROJECT_DIR ✓"
}

# Install Python dependencies
install_python_deps() {
    print_header "Installing Python Dependencies"
    
    cd "$PROJECT_DIR"
    
    # Install dependencies with UV
    print_msg "Installing Python packages (this may take several minutes)..."
    
    # Use UV to create virtual environment and install dependencies
    uv sync
    
    print_msg "Python dependencies installed ✓"
}

# Print completion message
print_completion() {
    print_header "Setup Complete!"
    
    echo -e "
${GREEN}Your Orange Pi 5 Max LLM setup is complete!${NC}

${BLUE}Project Location:${NC} ${PROJECT_DIR}

${BLUE}To start the API server:${NC}
  cd ${PROJECT_DIR}
  source .venv/bin/activate  # or: source \$(uv python find)/bin/activate
  uv run opi5-server

${BLUE}Or using uvicorn directly:${NC}
  uv run uvicorn opi5_max_llm_setup.api.server:app --host 0.0.0.0 --port 8000

${BLUE}API Endpoints:${NC}
  - API Docs:  http://localhost:8000/docs
  - Health:    http://localhost:8000/api/v1/health
  - Upload:    POST http://localhost:8000/api/v1/documents/upload
  - Query:     POST http://localhost:8000/api/v1/query
  - Chat:      POST http://localhost:8000/api/v1/chat

${BLUE}Ollama Commands:${NC}
  - List models:   ollama list
  - Pull model:    ollama pull <model_name>
  - Run chat:      ollama run $DEFAULT_MODEL

${BLUE}Recommended Models for 16GB RAM:${NC}
  - qwen2.5:3b       (fast, efficient)
  - phi3:mini        (good for coding)
  - llama3.2:3b      (good all-rounder)
  - mistral:7b-q4_0  (high quality)

${YELLOW}Note:${NC} For NPU acceleration, see docs/npu-setup.md

${GREEN}Happy coding!${NC}
"
}

# Main execution
main() {
    print_header "Orange Pi 5 Max - LLM Setup Script"
    
    echo "This script will:"
    echo "  1. Check system requirements"
    echo "  2. Update system packages"
    echo "  3. Install dependencies (UV, Ollama)"
    echo "  4. Setup the RAG project"
    echo "  5. Install Python packages"
    echo "  6. Pull recommended LLM model"
    echo ""
    
    read -p "Continue? (Y/n): " confirm
    if [[ "$confirm" == "n" || "$confirm" == "N" ]]; then
        echo "Setup cancelled."
        exit 0
    fi
    
    check_architecture
    check_ram
    update_system
    install_dependencies
    install_uv
    install_ollama
    setup_project
    install_python_deps
    pull_model
    print_completion
}

# Run main function
main "$@"
