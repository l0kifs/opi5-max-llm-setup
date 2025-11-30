## Plan: Fix All Identified Project Issues (Updated)

Fix critical bugs preventing RKLLM backend usage, improve exception handling in API routes, and enhance test robustness by mocking external dependencies.

### Key Discovery: RKLLama

[RKLLama](https://github.com/NotPunchnox/rkllama) is an Ollama-compatible server that runs LLMs on the RK3588 NPU. Since it implements the same API as Ollama (`/api/chat`, `/api/generate`, `/api/tags`, `/api/embed`, etc.), we can **reuse `langchain_ollama.OllamaLLM`** directly with minimal changes. This dramatically simplifies NPU integration.

**Key Facts (Verified from RKLLama v0.0.51 docs):**
- Default port: **8080** (not 11434 like Ollama)
- Docker image: `ghcr.io/notpunchnox/rkllama:main`
- Requires **privileged mode** for NPU access (simplest approach)
- Model format: `.rkllm` files (not GGUF)
- Simplified model naming: `qwen2.5:3b`, `llama3:7b`, etc.

### Steps

1. **Refactor `RKLLMClient` to use RKLLama server** in [`rkllm_client.py`](src/opi5_max_llm_setup/llm/rkllm_client.py)
   - Remove the ctypes/C++ integration approach
   - Implement `RKLLMClient` as an HTTP client connecting to RKLLama server (reuse pattern from `OllamaClient`)
   - Add `rkllm_base_url` setting (default: `http://localhost:8080`)
   - Add `rkllm_model` setting (default: `qwen2.5:3b`)
   - **Key simplification**: Since RKLLama is Ollama-compatible, the client can use identical HTTP calls
   - Update `is_available()` to ping RKLLama server at `/api/tags`
   - Remove model path/lib path settings (no longer needed)

2. **Simplify LangChain integration for RKLLM** - NO custom wrapper needed!
   - **Key insight**: Since RKLLama implements Ollama API, we can use `langchain_ollama.OllamaLLM` directly:
     ```python
     from langchain_ollama import OllamaLLM
     
     rkllm_llm = OllamaLLM(
         model=settings.rkllm_model,
         base_url=settings.rkllm_base_url,  # http://localhost:8080
     )
     ```
   - Delete the planned `rkllm_langchain.py` file - not needed!
   - Update `llm/__init__.py` exports if needed

3. **Update RAG pipeline for backend selection** in [`rag_pipeline.py`](src/opi5_max_llm_setup/rag/rag_pipeline.py)
   - Add `llm` property that returns LangChain-compatible LLM based on `settings.llm_backend`
   - For RKLLM: return `OllamaLLM` with `rkllm_base_url`
   - For Ollama: return existing `OllamaLLM` with `ollama_base_url`
   - Update `rag_chain` property to use the new `llm` property
   - Update `get_stats()` to report correct backend status

4. **Update settings** in [`settings.py`](src/opi5_max_llm_setup/config/settings.py)
   - Remove `rkllm_model_path` and `rkllm_lib_path`
   - Add:
     ```python
     rkllm_base_url: str = "http://localhost:8080"
     rkllm_model: str = "qwen2.5:3b"
     ```
   - Add `@lru_cache` decorator to `get_settings()` function

5. **Update docker-compose.yml** for RKLLama support
   - Add `rkllama` service using `ghcr.io/notpunchnox/rkllama:main` image
   - Use `privileged: true` for NPU access (simplest, recommended approach)
   - Add volume for RKLLama models: `./models:/opt/rkllama/models`
   - Expose port 8080 (RKLLama default)
   - Update `rag-api` service environment:
     - `OLLAMA_BASE_URL=http://ollama:11434`
     - `RKLLM_BASE_URL=http://rkllama:8080`
   - Add Docker Compose profiles for flexibility:
     - `--profile cpu` starts Ollama only
     - `--profile npu` starts RKLLama only
     - Default (no profile) starts both

6. **Add missing exception handling** in [`routes.py`](src/opi5_max_llm_setup/api/routes.py)
   - Catch `httpx.HTTPStatusError` and `httpx.RequestError` for HTTP errors
   - Note: Don't import `ollama.ResponseError` - we use `httpx` directly
   - Add proper error responses for `chat_with_llm`, `list_models`, `get_model_info` endpoints

7. **Fix chat endpoint test** in [`test_api.py`](tests/test_api.py)
   - Mock `OllamaClient` and `RKLLMClient` to avoid external dependencies
   - Use `unittest.mock.patch` to return controlled responses
   - Test both success and error response structures

8. **Remove unnecessary `.env.example` copy** in [`Dockerfile`](Dockerfile)
   - Delete the `COPY .env.example .env.example` line if present
   - Users should mount their own `.env` file at runtime

9. **Update documentation**
   - Update [`npu-setup.md`](docs/npu-setup.md) to document RKLLama Docker setup
   - Update [`.env.example`](.env.example) with new settings:
     ```env
     RKLLM_BASE_URL=http://localhost:8080
     RKLLM_MODEL=qwen2.5:3b
     ```
   - Update [`README.md`](README.md) quick start with Docker Compose profiles:
     - `docker compose --profile cpu up` for Ollama (CPU)
     - `docker compose --profile npu up` for RKLLama (NPU)
   - Note that `.rkllm` models must be downloaded/converted separately

### Architecture Simplification Summary

**Before (Original Plan):**
```
RKLLMClient (ctypes) → RKLLMLangChain (custom BaseLLM) → RAG Pipeline
```

**After (Simplified with RKLLama):**
```
RKLLMClient (HTTP) → OllamaLLM (langchain_ollama) → RAG Pipeline
```

Since RKLLama is Ollama API-compatible, we eliminate the need for:
- ❌ Custom C++/ctypes integration
- ❌ Custom LangChain `BaseLLM` wrapper (`rkllm_langchain.py`)
- ❌ Complex NPU device management

### Out of Scope (Future Issues)

1. **Integration test suite**: Add `pytest.mark.integration` marker for tests requiring external services (Ollama, RKLLama). Configure to skip by default, run in CI with services.

2. **Model conversion**: Document how to convert GGUF models to `.rkllm` format using RKLLama's converter tools.

3. **Performance benchmarking**: Compare CPU (Ollama) vs NPU (RKLLama) inference speeds.
