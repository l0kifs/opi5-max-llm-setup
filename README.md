# Orange Pi 5 Max LLM Setup

This guide provides instructions for setting up Large Language Models (LLM) on the Orange Pi 5 Max using [RKNN-LLM](https://github.com/airockchip/rknn-llm) from Rockchip.

## Overview

The RKLLM software stack enables quick deployment of AI models to Rockchip chips. It consists of:

- **RKLLM-Toolkit**: Software development kit for model conversion and quantization on PC (x86 Linux)
- **RKLLM Runtime**: C/C++ programming interfaces for deploying RKLLM models on Rockchip NPU platform
- **RKNPU Kernel Driver**: Interacts with NPU hardware (included in Rockchip kernel)

## Supported Platform

- Orange Pi 5 Max (RK3588 based)
- Linux OS (Ubuntu/Debian recommended)
- Rockchip kernel 5.10 or 6.1

## Supported Models

- LLAMA models
- TinyLLAMA models
- Qwen2/Qwen2.5/Qwen3
- Phi2/Phi3
- ChatGLM3-6B
- Gemma2/Gemma3/Gemma3n
- InternLM2 models
- MiniCPM3/MiniCPM4
- TeleChat2
- Qwen2-VL/Qwen3-VL (Multimodal)
- MiniCPM-V-2_6 (Multimodal)
- DeepSeek-R1-Distill
- Janus-Pro-1B
- InternVL2-1B/InternVL3-1B
- SmolVLM
- RWKV7

## Quick Start

### Prerequisites

- Python 3.9, 3.10, 3.11, or 3.12
- Linux operating system on Orange Pi 5 Max

### Installation

1. Clone the official RKNN-LLM repository:

```bash
git clone https://github.com/airockchip/rknn-llm.git
cd rknn-llm
```

2. Download pre-converted models and demos:
   - Models and demos available at [rkllm_model_zoo](https://console.box.lenovo.com/l/l0tXb8) (fetch code: `rkllm`)
   - SDK available at [RKLLM_SDK](https://console.zbox.filez.com/l/RJJDmB) (fetch code: `rkllm`)

### Running a Model (Quick Demo)

1. Push the demo files to your Orange Pi 5 Max:

```bash
adb push ./demo_Linux_aarch64 /data
adb push model.rkllm /data/demo_Linux_aarch64
```

2. Connect to the board and run:

```bash
adb shell
cd /data/demo_Linux_aarch64
export LD_LIBRARY_PATH=./lib

# Run the demo
# Usage: ./llm_demo <model_path> <max_new_tokens> <max_context_length>
./llm_demo /path/to/your/model.rkllm 2048 4096
```

### Performance Optimization

For optimal performance, run the frequency-fixing script before inference:

```bash
# Clone the repository first
cd rknn-llm/scripts

# Run the appropriate script for RK3588
sudo bash fix_freq_rk3588.sh
```

To view performance logs during inference:

```bash
export RKLLM_LOG_LEVEL=1
```

## Server Demo (OpenAI-compatible API)

You can run an OpenAI-compatible API server on your Orange Pi 5 Max:

### Flask Server

```bash
cd rknn-llm/examples/rkllm_server_demo

# Build and run
./build_rkllm_server_flask.sh --workshop /data --model_path /data/model.rkllm --platform rk3588
```

### Gradio Server (Web UI)

```bash
cd rknn-llm/examples/rkllm_server_demo

# Build and run
./build_rkllm_server_gradio.sh --workshop /data --model_path /data/model.rkllm --platform rk3588
```

Access the web interface at `http://<board-ip>:8080/`

## Model Conversion (Advanced)

To convert your own models, you need a Linux PC (x86) with RKLLM-Toolkit installed:

1. Install RKLLM-Toolkit:

```bash
cd rknn-llm/rkllm-toolkit/packages

# Install dependencies
pip install -r requirements.txt

# Install toolkit (choose your Python version)
pip install rkllm_toolkit-1.2.3-cp310-cp310-linux_x86_64.whl  # For Python 3.10
```

2. Convert a model (example with DeepSeek-R1-Distill-Qwen-1.5B):

```bash
cd rknn-llm/examples/rkllm_api_demo/export

# Generate quantization data
# Download the model from https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B
python generate_data_quant.py -m /path/to/DeepSeek-R1-Distill-Qwen-1.5B

# Export to RKLLM format
python export_rkllm.py
```

> **Note**: For Python 3.12, set `export BUILD_CUDA_EXT=0` before installing packages.

## Troubleshooting

### libomp.so not found

If you encounter this error, locate `libomp.so` in your cross-compilation toolchain and copy it to the same directory as `librkllmrt.so`.

### Model hallucinating or producing garbage output

This may indicate quantization issues. Try using pre-converted models from the official model zoo or adjust quantization parameters.

## Resources

- [Official RKNN-LLM Repository](https://github.com/airockchip/rknn-llm)
- [RKNN-Toolkit2 (for other AI models)](https://github.com/airockchip/rknn-toolkit2)
- [Performance Benchmarks](https://github.com/airockchip/rknn-llm/blob/main/benchmark.md)
- [Model Zoo](https://console.box.lenovo.com/l/l0tXb8) (fetch code: `rkllm`)

## License

This documentation is licensed under the MIT License. See [LICENSE](LICENSE) for details.

The RKNN-LLM software is subject to its own [license terms](https://github.com/airockchip/rknn-llm/blob/main/LICENSE).