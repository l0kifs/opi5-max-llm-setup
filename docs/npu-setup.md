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

## Option A: ezrknn-llm (Recommended for NPU)

ezrknn-llm simplifies NPU-accelerated LLM setup on RK3588 devices.

### Prerequisites

- Ubuntu 24.04 with Joshua Riek's kernel (includes NPU drivers)
- At least 8GB RAM (16GB recommended)
- Internet connection for initial setup

### Installation

```bash
# Clone ezrknn-llm repository
git clone https://github.com/Pelochus/ezrknn-llm.git
cd ezrknn-llm

# Run installation script
sudo bash install.sh
```

### Download Pre-converted Models

Pre-converted RKLLM models are available on Hugging Face:

```bash
# Install git-lfs if not present
sudo apt install git-lfs

# Clone model repository (example: TinyLlama)
git clone https://huggingface.co/Pelochus/ezrkllm-collection

# If download fails, try:
GIT_LFS_SKIP_SMUDGE=1 git clone https://huggingface.co/Pelochus/ezrkllm-collection
cd ezrkllm-collection
git lfs pull
```

### Available Pre-converted Models

| Model | Size | RAM Required | Notes |
|-------|------|--------------|-------|
| TinyLlama 1.1B | ~1GB | 2-3GB | Very fast, basic tasks |
| Phi-2 | ~2.5GB | 4-5GB | Good for coding |
| Phi-3 Mini | ~3GB | 5-6GB | Balanced performance |
| Gemma 2B | ~2GB | 3-4GB | Good quality |
| Qwen 1.5 7B | ~7GB | 12-14GB | High quality |

### Running Models

```bash
# Navigate to model directory
cd /path/to/model

# Run the model
rkllm your-model.rkllm

# Example with TinyLlama
rkllm TinyLlama-1.1B-Chat-v1.0-rk3588-w8a8-opt-0-hybrid-ratio-0.0.rkllm
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
docker run -it pelochus/ezrkllm-toolkit:latest bash

# Inside the container:
# 1. Download your model from Hugging Face
# 2. Convert using RKLLM toolkit
# 3. Copy the .rkllm file to your Orange Pi
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

Typical inference speeds on Orange Pi 5 Max 16GB:

| Model | Method | Tokens/sec |
|-------|--------|------------|
| TinyLlama 1.1B | NPU | 25-35 |
| TinyLlama 1.1B | Ollama (CPU) | 10-15 |
| Phi-3 Mini | NPU | 15-25 |
| Phi-3 Mini | Ollama (CPU) | 6-10 |
| Qwen 7B | NPU | 8-12 |
| Qwen 7B | Ollama (CPU) | 3-6 |

*Actual performance may vary based on prompt length and system load.*

## Resources

- [ezrknn-llm GitHub](https://github.com/Pelochus/ezrknn-llm)
- [RKLLM Toolkit Documentation](https://github.com/airockchip/rknn-llm)
- [Pre-converted Models (Hugging Face)](https://huggingface.co/Pelochus/ezrkllm-collection)
- [RKLLM-Gradio WebUI](https://github.com/c0zaut/RKLLM-Gradio)

## Integration with This Project

The RAG pipeline in this project uses Ollama by default, which works well for most use cases. If you want to use NPU-accelerated inference:

1. Run your RKLLM model server separately
2. Configure this project to use an OpenAI-compatible API endpoint
3. Or modify the LLM client to use RKLLM Python bindings directly

For most users, Ollama provides a good balance of ease-of-use and performance.
