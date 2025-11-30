# Orange Pi 5 Max - Local LLM with RAG System Setup

Complete setup of local Large Language Models (LLMs) with Retrieval-Augmented Generation (RAG) and REST API on Orange Pi 5 Max 16GB.

## 🚀 Quick Start

### NPU-Accelerated Setup (Recommended)

For best performance on Orange Pi 5 Max, use the NPU-accelerated RKLLM backend which provides 2-3x faster inference:

```bash
# Clone the repository
git clone https://github.com/l0kifs/opi5-max-llm-setup.git
cd opi5-max-llm-setup

# Run the setup script with RKLLM (NPU) support
bash scripts/setup.sh --rkllm
```

See the [NPU Setup Guide](docs/npu-setup.md) for detailed instructions on downloading pre-converted models from the RKLLM Model Zoo.

### Alternative: Ollama Setup (Easier, but Slower)

If you prefer a simpler setup without NPU acceleration:

```bash
# Clone the repository
git clone https://github.com/l0kifs/opi5-max-llm-setup.git
cd opi5-max-llm-setup

# Run the setup script with Ollama
bash scripts/setup.sh --ollama
```

### Manual Setup (NPU-Accelerated)

```bash
# 1. Clone the official rknn-llm repository
git clone https://github.com/airockchip/rknn-llm.git

# 2. Download pre-converted models from RKLLM Model Zoo
# Visit: https://console.box.lenovo.com/l/l0tXb8 (fetch code: rkllm)

# 3. Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# 4. Clone and setup project
git clone https://github.com/l0kifs/opi5-max-llm-setup.git
cd opi5-max-llm-setup

# 5. Install dependencies
uv sync

# 6. Copy environment configuration
cp .env.example .env
# Edit .env to use RKLLM backend

# 7. Start the API server
uv run opi5-server
```

The API will be available at `http://localhost:8000` with documentation at `http://localhost:8000/docs`.

## 🎯 Features

### Hardware Optimized
- Optimized for Orange Pi 5 Max (16GB RAM)
- Rockchip RK3588 ARM64 architecture support
- Memory-efficient model recommendations
- **NPU acceleration via RKLLM (recommended, 2-3x faster)**
- CPU-optimized inference with Ollama (alternative)

### LLM Support
- **RKLLM integration for NPU-accelerated inference (recommended)**
- Ollama integration for easy model management (alternative)
- Multiple model options (Qwen, Phi-3, Llama, Mistral, etc.)
- Quantized models (w8a8) for memory efficiency
- Hot-swappable models

### RAG Capabilities
- Document loading (TXT, PDF, DOCX)
- Intelligent text chunking with configurable overlap
- Local embedding generation (sentence-transformers)
- Vector storage with ChromaDB
- Semantic search and retrieval
- Context-aware response generation

### REST API
- FastAPI-based REST API with OpenAPI documentation
- Endpoints for chat, document management, and RAG queries
- File upload support with validation
- Health checks and model information
- Easy integration with other applications

## 🔧 System Requirements

- **Hardware**: Orange Pi 5 Max with 8GB or 16GB RAM
- **OS**: Ubuntu 24.04 (ARM64) - See [host-system-setup.md](docs/host-system-setup.md)
- **Python**: 3.12 or higher
- **Storage**: 20GB+ free disk space (for models and data)
- **Network**: Internet connection (for initial setup)

## 📦 Installation

### Prerequisites

1. **Ubuntu 24.04 for RK3588** - Use Joshua Riek's customized Ubuntu image:
   - Download from: https://github.com/Joshua-Riek/ubuntu-rockchip
   - This image includes the latest NPU drivers
   - See [host-system-setup.md](docs/host-system-setup.md) for detailed instructions

2. **Update your system**:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential git curl python3 python3-pip python3-venv
```

### Installation Steps

#### Option A: RKLLM Setup (Recommended for Best Performance)

1. **Clone RKLLM repository**:
```bash
git clone https://github.com/airockchip/rknn-llm.git
```

2. **Download pre-converted models**:
   - Visit: https://console.box.lenovo.com/l/l0tXb8
   - Fetch code: `rkllm`
   - Download models and demos for your use case

3. **Install UV** (modern Python package manager):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart terminal
```

4. **Clone and setup project**:
```bash
git clone https://github.com/l0kifs/opi5-max-llm-setup.git
cd opi5-max-llm-setup
uv sync
```

5. **Configure environment**:
```bash
cp .env.example .env
# Edit .env to configure RKLLM backend
```

#### Option B: Ollama Setup (Easier, but Slower)

1. **Install Ollama**:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

2. **Pull a model**:
```bash
# For 16GB RAM - recommended
ollama pull qwen2.5:3b

# Alternative models
ollama pull phi3:mini      # Good for coding
ollama pull llama3.2:3b    # Good all-rounder
ollama pull gemma2:2b      # Very fast
```

3. **Install UV** (modern Python package manager):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart terminal
```

4. **Clone and setup project**:
```bash
git clone https://github.com/l0kifs/opi5-max-llm-setup.git
cd opi5-max-llm-setup
uv sync
```

5. **Configure environment**:
```bash
cp .env.example .env
# Edit .env to customize settings
```

## 🎮 Usage

### Starting the Server

```bash
# Using the CLI command
uv run opi5-server

# Or using uvicorn directly
uv run uvicorn opi5_max_llm_setup.api.server:app --host 0.0.0.0 --port 8000

# For development with auto-reload
uv run uvicorn opi5_max_llm_setup.api.server:app --host 0.0.0.0 --port 8000 --reload
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/docs` | GET | OpenAPI documentation |
| `/api/v1/health` | GET | Health check |
| `/api/v1/query` | POST | Query RAG pipeline |
| `/api/v1/chat` | POST | Direct LLM chat |
| `/api/v1/documents/upload` | POST | Upload document |
| `/api/v1/documents/search` | POST | Search documents |
| `/api/v1/documents` | DELETE | Clear all documents |
| `/api/v1/stats` | GET | Pipeline statistics |
| `/api/v1/models` | GET | List available models |

### Example API Usage

**Upload a document:**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@/path/to/document.pdf"
```

**Query the RAG pipeline:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

**Direct chat with LLM:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum computing in simple terms"}'
```

**Search similar documents:**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "k": 5}'
```

### Python Client Example

```python
import httpx

# Upload a document
with open("document.pdf", "rb") as f:
    response = httpx.post(
        "http://localhost:8000/api/v1/documents/upload",
        files={"file": f}
    )
    print(response.json())

# Query the RAG pipeline
response = httpx.post(
    "http://localhost:8000/api/v1/query",
    json={"question": "What are the main points?"}
)
print(response.json()["answer"])
```

## 📚 Recommended Models

### RKLLM Models (NPU-Accelerated, Recommended)

Download pre-converted models from [RKLLM Model Zoo](https://console.box.lenovo.com/l/l0tXb8) (fetch code: `rkllm`).

| Model | Size | Dtype | Best For | Tokens/sec |
|-------|------|-------|----------|------------|
| Qwen2 0.5B | 0.5B | w8a8 | Very fast, basic tasks | 42.6 |
| TinyLLAMA 1.1B | 1.1B | w8a8 | Fast responses | 24.5 |
| Qwen2.5 1.5B | 1.5B | w8a8 | General tasks | 16.3 |
| InternLM2 1.8B | 1.8B | w8a8 | Research models | 15.6 |
| Gemma2 2B | 2B | w8a8 | Good quality | 9.8 |
| Phi3 3.8B | 3.8B | w8a8 | Coding, reasoning | 7.5 |
| MiniCPM3 4B | 4B | w8a8 | Efficient models | 6.0 |
| ChatGLM3 6B | 6B | w8a8 | Chinese + English | 4.9 |

### Ollama Models (Alternative, CPU-Based)

#### Small Models (2-4GB RAM, Fast)
| Model | Command | Best For |
|-------|---------|----------|
| `qwen2.5:3b` | `ollama pull qwen2.5:3b` | General tasks, fast |
| `phi3:mini` | `ollama pull phi3:mini` | Coding, reasoning |
| `gemma2:2b` | `ollama pull gemma2:2b` | Very fast responses |
| `llama3.2:3b` | `ollama pull llama3.2:3b` | Good all-rounder |

#### Medium Models (5-8GB RAM, Better Quality)
| Model | Command | Best For |
|-------|---------|----------|
| `mistral:7b-instruct-q4_0` | `ollama pull mistral:7b-instruct-q4_0` | High-quality responses |
| `llama3.1:8b-instruct-q4_0` | `ollama pull llama3.1:8b-instruct-q4_0` | Latest capabilities |
| `qwen2.5:7b-instruct-q4_0` | `ollama pull qwen2.5:7b-instruct-q4_0` | Multilingual |

#### Specialized Models
| Model | Command | Best For |
|-------|---------|----------|
| `codellama:7b-instruct` | `ollama pull codellama:7b-instruct` | Code generation |
| `deepseek-r1:1.5b` | `ollama pull deepseek-r1:1.5b` | Reasoning tasks |

## 📊 Expected Performance

### RKLLM (NPU) Performance (Recommended)

Official benchmark results on RK3588 (from rknn-llm documentation):

| Model | Size | Dtype | TTFT(ms) | Tokens/s | Memory(MB) |
|-------|------|-------|----------|----------|------------|
| Qwen2 | 0.5B | w8a8 | 144 | 42.6 | 654 |
| TinyLLAMA | 1.1B | w8a8 | 239 | 24.5 | 1085 |
| Qwen2.5 | 1.5B | w8a8 | 412 | 16.3 | 1659 |
| InternLM2 | 1.8B | w8a8 | 374 | 15.6 | 1766 |
| Gemma2 | 2B | w8a8 | 680 | 9.8 | 2765 |
| Phi3 | 3.8B | w8a8 | 1022 | 7.5 | 3748 |
| MiniCPM3 | 4B | w8a8 | 1386 | 6.0 | 4340 |
| ChatGLM3 | 6B | w8a8 | 1395 | 4.9 | 5976 |

*TTFT = Time To First Token. Performance tested with Seqlen=128, New_tokens=64.*

### Ollama (CPU) Performance

| Model | RAM Usage | Tokens/sec | Quality |
|-------|-----------|------------|---------|
| Qwen 2.5 3B | 2-3GB | 15-25 | Good |
| Phi-3 Mini | 2-3GB | 15-25 | Good |
| Llama 3.2 3B | 2-3GB | 12-20 | Good |
| Gemma 2 2B | 2GB | 20-30 | Good |
| Mistral 7B Q4 | 5-6GB | 8-15 | Very Good |
| Llama 3.1 8B Q4 | 6-7GB | 6-12 | Very Good |

*Performance varies based on context length and system load.*

## ⚡ NPU Acceleration (Recommended)

For best performance on Orange Pi 5 Max, use the RK3588's NPU with RKLLM. See the [NPU Setup Guide](docs/npu-setup.md) for complete instructions.

**Why use RKLLM (NPU)?**
- **2-3x faster inference** compared to CPU-only Ollama
- **Lower memory usage** with w8a8 quantization
- **Better power efficiency** for edge deployment
- **Official support** from Rockchip via airockchip/rknn-llm

**Quick Start:**
```bash
# Clone RKLLM repository
git clone https://github.com/airockchip/rknn-llm.git

# Download models from RKLLM Model Zoo
# Visit: https://console.box.lenovo.com/l/l0tXb8 (fetch code: rkllm)
```

## 🔄 Alternative: Ollama (CPU-Based)

If you prefer a simpler setup or need models not available in RKLLM format:

- Easier initial setup with more available models
- Good for testing and development
- Works on any system without NPU drivers

See [Ollama Documentation](https://ollama.com/) for details.

## 🛠️ Configuration

All settings can be configured via environment variables or the `.env` file:

```bash
# LLM Settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b

# Embedding Settings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu

# RAG Settings
CHUNK_SIZE=500
CHUNK_OVERLAP=50
RETRIEVAL_K=3

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

See `.env.example` for all available options.

## 🛠️ Troubleshooting

### Ollama Not Running
```bash
# Check status
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Or with systemd
sudo systemctl start ollama
```

### Out of Memory
- Use smaller models (3B instead of 7B)
- Reduce `OLLAMA_NUM_PARALLEL` to 1
- Reduce `RETRIEVAL_K` for smaller context
- Close other applications

### Slow Inference
- Enable performance governor: `sudo cpupower frequency-set -g performance`
- Use quantized models (Q4, Q5)
- Consider NPU acceleration (see [NPU Setup](docs/npu-setup.md))

### Import Errors
```bash
# Reinstall dependencies
uv sync --reinstall
```

## 📖 Documentation

- [Host System Setup](docs/host-system-setup.md) - Ubuntu installation guide
- [Hardware Specifications](docs/hardware-specifications.md) - Orange Pi 5 Max specs
- [NPU Setup Guide](docs/npu-setup.md) - NPU acceleration setup

## 🧪 Development

```bash
# Install dev dependencies
uv sync --group dev

# Run tests
uv run pytest

# Run linting
uv run ruff check src tests
uv run ruff format src tests

# Type checking
uv run mypy src tests
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Resources

- [Ollama Documentation](https://ollama.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Joshua Riek's Ubuntu Rockchip](https://github.com/Joshua-Riek/ubuntu-rockchip)
- [RKLLM (NPU)](https://github.com/airockchip/rknn-llm)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Note**: This setup is specifically optimized for Orange Pi 5 Max with 16GB RAM running ARM64 architecture. Performance and compatibility may vary on other systems.

## Unsloth Consideration

Unsloth is an excellent tool for fine-tuning LLMs with reduced memory and faster training. However, **Unsloth is not suitable for Orange Pi 5 Max** because:

1. **CUDA Requirement**: Unsloth's optimizations rely on NVIDIA CUDA, which is not available on ARM64 devices with Mali GPUs
2. **Training vs Inference**: Unsloth is for training/fine-tuning, not inference - the Orange Pi is better suited for running pre-trained models
3. **Resource Constraints**: LLM fine-tuning requires significantly more resources than inference

**Recommendation**: Use the Orange Pi 5 Max for inference with Ollama or NPU-accelerated RKLLM. For fine-tuning, use a machine with an NVIDIA GPU, then deploy the fine-tuned model to your Orange Pi.