# Orange Pi 5 Max - Local LLM with RAG System Setup

Complete setup of local Large Language Models (LLMs) with Retrieval-Augmented Generation (RAG) and REST API on Orange Pi 5 Max 16GB.

## 🚀 Quick Start

TBD

## 🎯 Features

### Hardware Optimized
- Optimized for Orange Pi 5 Max (16GB RAM)
- Rockchip RK3588 ARM64 architecture support
- Memory-efficient model recommendations
- CPU-optimized inference

### LLM Support
- Ollama integration for easy model management
- Multiple model options (Phi-3, Mistral, Llama, etc.)
- Quantized models (Q4, Q5, Q8) for memory efficiency

### RAG Capabilities
- Document loading (TXT, PDF, DOCX)
- Text chunking and embedding generation
- Vector storage (ChromaDB)
- Semantic search and retrieval
- Context-aware response generation

### REST API
- FastAPI-based REST API
- Endpoints for chat, document management, and model handling
- Easy integration with other applications

## 🔧 System Requirements

- Orange Pi 5 Max with 10GB or 16GB RAM
- Ubuntu OS (ARM64) - **Not installed yet? See [host-system-setup.md](docs/host-system-setup.md)**
- Python 3.12 or higher
- 20GB+ free disk space (for models)
- Internet connection (for initial setup)

## 📦 Installation

TBD

## 🎮 Usage

TBD

## 📚 Recommended Models

### Small Models (2-4GB RAM, Fast)
- `phi3:mini` - Best for quick responses and low memory usage
- `llama3.2:3b` - Balanced performance and quality

### Medium Models (5-8GB RAM, Better Quality)
- `mistral:7b-instruct-q4_0` - High-quality responses
- `llama3.1:8b-instruct-q4_0` - Latest capabilities

### Specialized
- `codellama:7b-instruct` - Code generation
- `mistral-nemo:12b-instruct-q4_0` - Advanced tasks (8-10GB)

## 📊 Expected Performance

| Model           | RAM Usage | Tokens/sec | Quality   |
| --------------- | --------- | ---------- | --------- |
| Phi-3 Mini      | 2-3GB     | 15-25      | Good      |
| Llama 3.2 3B    | 2-3GB     | 12-20      | Good      |
| Mistral 7B Q4   | 5-6GB     | 8-15       | Very Good |
| Llama 3.1 8B Q4 | 6-7GB     | 6-12       | Very Good |

*Performance may vary based on context length and system load.*

## 🛠️ Troubleshooting

TBD

## 📖 Documentation

TBD

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Resources

TBD

**Note**: This setup is specifically optimized for Orange Pi 5 Max with 16GB RAM running ARM64 architecture. Performance and compatibility may vary on other systems.