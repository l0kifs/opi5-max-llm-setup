# NPU Setup Guide for Orange Pi 5 Max

This guide covers setting up NPU-accelerated LLM inference on the Orange Pi 5 Max using the RK3588's 6 TOPS Neural Processing Unit.

## Overview

The RK3588 SoC includes a dedicated NPU capable of 6 TOPS (Trillion Operations Per Second) of AI inference. For LLMs, this can provide significant performance improvements over CPU-only inference.

### NPU vs Ollama

| Approach | Pros | Cons |
|----------|------|------|
| **Ollama (CPU)** | Easy setup, many models | Slower inference |
| **NPU (RKLLM)** | Faster inference | Requires model conversion, fewer models |

**Recommendation**: Start with Ollama for ease of use. Consider NPU if you need faster inference for specific models.

## Option A: Official RKLLM SDK (Recommended for NPU)

The official RKLLM SDK from Rockchip provides comprehensive NPU-accelerated LLM support for RK3588 devices.

### Prerequisites

- Ubuntu 24.04 with Joshua Riek's kernel (includes NPU drivers)
- At least 8GB RAM (16GB recommended)
- Internet connection for initial setup
- Python 3.9, 3.10, 3.11, or 3.12

### Installation

```bash
# Clone the official rknn-llm repository
git clone https://github.com/airockchip/rknn-llm.git
cd rknn-llm

# The repository contains:
# - rkllm-runtime/  : Runtime libraries for Linux/Android
# - rkllm-toolkit/  : Model conversion toolkit (for x86_64 PC)
# - examples/       : Demo applications
# - scripts/        : Performance tuning scripts
```

### Download Pre-converted Models

Pre-converted RKLLM models are available from the official RKLLM Model Zoo:

```bash
# Download models from the official RKLLM Model Zoo
# URL: https://console.box.lenovo.com/l/l0tXb8
# Fetch code: rkllm

# The model zoo includes:
# - quickstart/ directory with demo executables
# - Pre-converted .rkllm models for various LLMs
```

### Supported Models

| Model | Model Size | Notes |
|-------|------------|-------|
| Qwen2/Qwen2.5/Qwen3 | 0.5B - 7B+ | General purpose, multilingual |
| TinyLlama | 1.1B | Very fast, basic tasks |
| Phi2/Phi3 | 2B - 3.8B | Good for coding |
| Gemma2/Gemma3/Gemma3n | 2B | Good quality |
| ChatGLM3 | 6B | Chinese + English |
| InternLM2 | 1.8B | Research models |
| MiniCPM3/MiniCPM4 | 0.5B - 4B | Efficient models |
| DeepSeek-R1-Distill | Various | Reasoning tasks |
| Qwen2-VL/Qwen3-VL | 2B - 3B | Vision-language models |
| MiniCPM-V-2_6 | - | Vision-language model |

### Running Models

```bash
# Push demo and model to device
adb push ./demo_Linux_aarch64 /data
adb push model.rkllm /data/demo_Linux_aarch64

# Enter the device and set up environment
adb shell
cd /data/demo_Linux_aarch64
export LD_LIBRARY_PATH=./lib

# Run the demo
./demo model.rkllm
```

### Web UI (Optional)

For a graphical interface:

```bash
# Clone Gradio WebUI
git clone https://github.com/c0zaut/RKLLM-Gradio.git
cd RKLLM-Gradio

# Install dependencies
pip install -r requirements.txt

# Run the UI
python app.py
```

## Option B: Custom Model Conversion

If your desired model isn't available pre-converted, you can convert it yourself.

### Important Notes

- **Model conversion must be done on x86_64 Linux**, not on the Orange Pi
- The Orange Pi is used only for inference

### Using Docker for Conversion

```bash
# On your x86_64 Linux PC
# Download the RKLLM-Toolkit from the official SDK
# URL: https://console.zbox.filez.com/l/RJJDmB
# Fetch code: rkllm

# Install the toolkit package
pip install rkllm-toolkit/packages/rkllm_toolkit-1.2.x-cpXX-cpXX-linux_x86_64.whl
```

### Conversion Steps

1. **Prepare the model** (on x86_64 PC):
   ```python
   from rkllm.api import RKLLM
   
   # Load and convert model
   llm = RKLLM()
   llm.load_huggingface(model_path='path/to/model')
   llm.build(
       do_quantization=True,
       quantized_dtype='w8a8',
       target_platform='rk3588'
   )
   llm.export_rkllm('model.rkllm')
   ```

2. **Transfer to Orange Pi**:
   ```bash
   scp model.rkllm orange@orangepi-ip:~/models/
   ```

3. **Run on Orange Pi**:
   ```bash
   rkllm ~/models/model.rkllm
   ```

## Troubleshooting

### NPU Not Detected

```bash
# Check if NPU driver is loaded
dmesg | grep -i npu

# Check NPU device
ls /dev/rknpu*

# If missing, ensure you're using the correct kernel
uname -r
# Should show a Rockchip-compatible kernel
```

### Out of Memory

- Use smaller models or more aggressive quantization
- Close other applications
- Consider using swap (not recommended for performance)

### Model Loading Fails

- Ensure the model was converted for RK3588
- Check model file integrity
- Verify you have enough RAM for the model

## Performance Comparison

Official benchmark results on RK3588 (from rknn-llm documentation):

| Model | Model Size | Dtype | TTFT(ms) | Tokens/s | Memory(MB) |
|-------|------------|-------|----------|----------|------------|
| Qwen2 | 0.5B | w8a8 | 144 | 42.6 | 654 |
| TinyLLAMA | 1.1B | w8a8 | 239 | 24.5 | 1085 |
| Qwen2.5 | 1.5B | w8a8 | 412 | 16.3 | 1659 |
| InternLM2 | 1.8B | w8a8 | 374 | 15.6 | 1766 |
| Gemma2 | 2B | w8a8 | 680 | 9.8 | 2765 |
| Phi3 | 3.8B | w8a8 | 1022 | 7.5 | 3748 |
| MiniCPM3 | 4B | w8a8 | 1386 | 6.0 | 4340 |
| ChatGLM3 | 6B | w8a8 | 1395 | 4.9 | 5976 |

*TTFT = Time To First Token. Performance tested with Seqlen=128, New_tokens=64.*

*Actual performance may vary based on prompt length and system load.*

## Resources

- [RKLLM GitHub (Official)](https://github.com/airockchip/rknn-llm)
- [RKLLM SDK Download](https://console.zbox.filez.com/l/RJJDmB) (Fetch code: rkllm)
- [RKLLM Model Zoo](https://console.box.lenovo.com/l/l0tXb8) (Fetch code: rkllm)
- [RKLLM-Gradio WebUI](https://github.com/c0zaut/RKLLM-Gradio)

## Integration with This Project

The RAG pipeline in this project uses Ollama by default, which works well for most use cases. If you want to use NPU-accelerated inference:

1. Run your RKLLM model server separately
2. Configure this project to use an OpenAI-compatible API endpoint
3. Or modify the LLM client to use RKLLM Python bindings directly

For most users, Ollama provides a good balance of ease-of-use and performance.
