"""API routes for RAG and LLM services."""

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from loguru import logger

from opi5_max_llm_setup.api.models import (
    ChatRequest,
    ChatResponse,
    DocumentUploadResponse,
    HealthResponse,
    ModelInfo,
    ModelsResponse,
    QueryRequest,
    QueryResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
    StatsResponse,
)
from opi5_max_llm_setup.config.settings import LLMBackend, get_settings
from opi5_max_llm_setup.llm.ollama_client import LLMNotInitializedError, OllamaClient
from opi5_max_llm_setup.llm.rkllm_client import RKLLMClient, RKLLMNotAvailableError
from opi5_max_llm_setup.rag.rag_pipeline import RAGPipeline

router = APIRouter()


@lru_cache
def get_rag_pipeline() -> RAGPipeline:
    """Get or create RAG pipeline instance (cached)."""
    return RAGPipeline()


@lru_cache
def get_ollama() -> OllamaClient:
    """Get or create Ollama client instance (cached)."""
    return OllamaClient()


@lru_cache
def get_rkllm() -> RKLLMClient:
    """Get or create RKLLM client instance (cached)."""
    return RKLLMClient()


# Type aliases for dependency injection
RAGPipelineDep = Annotated[RAGPipeline, Depends(get_rag_pipeline)]
OllamaClientDep = Annotated[OllamaClient, Depends(get_ollama)]
RKLLMClientDep = Annotated[RKLLMClient, Depends(get_rkllm)]


def get_llm_availability() -> tuple[str, bool]:
    """Get LLM backend type and availability.

    Returns:
        Tuple of (backend_name, is_available)
    """
    settings = get_settings()
    backend = settings.llm_backend

    if backend == LLMBackend.RKLLM:
        rkllm = get_rkllm()
        return (backend.value, rkllm.is_available())
    else:
        ollama = get_ollama()
        return (backend.value, ollama.is_available())


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    """Check API health and LLM backend availability."""
    settings = get_settings()
    backend, available = get_llm_availability()
    return HealthResponse(
        status="healthy",
        llm_backend=backend,
        llm_available=available,
        version=settings.app_version,
    )


@router.post("/query", response_model=QueryResponse, tags=["RAG"])
def query_documents(
    request: QueryRequest,
    pipeline: RAGPipelineDep,
) -> QueryResponse:
    """Query the RAG pipeline with a question.

    The pipeline will search for relevant documents and generate an answer.
    """
    result = pipeline.query(request.question)

    return QueryResponse(
        success=result.get("success", False),
        answer=result.get("answer"),
        sources=result.get("sources"),
        error=result.get("error"),
    )


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat_with_llm(
    request: ChatRequest,
    ollama: OllamaClientDep,
    rkllm: RKLLMClientDep,
) -> ChatResponse:
    """Chat directly with the LLM without RAG context.

    Use this for general questions that don't require document context.
    Uses the configured LLM backend (ollama or rkllm).
    """
    settings = get_settings()
    backend = settings.llm_backend

    try:
        if backend == LLMBackend.RKLLM:
            if not rkllm.is_available():
                return ChatResponse(
                    success=False,
                    error="RKLLM is not available. Check model path and NPU drivers.",
                )
            response = rkllm.generate(request.prompt)
        else:
            if not ollama.is_available():
                return ChatResponse(
                    success=False,
                    error="Ollama server is not available",
                )
            response = ollama.generate(request.prompt)

        return ChatResponse(success=True, response=response)
    except (
        LLMNotInitializedError,
        RKLLMNotAvailableError,
        httpx.RequestError,
        RuntimeError,
    ) as e:
        logger.error(f"Chat error: {e}")
        return ChatResponse(success=False, error=str(e))


@router.post(
    "/documents/upload",
    response_model=DocumentUploadResponse,
    tags=["Documents"],
)
async def upload_document(
    file: UploadFile,
    pipeline: RAGPipelineDep,
) -> DocumentUploadResponse:
    """Upload a document to the RAG pipeline.

    Supported formats: PDF, TXT, DOCX
    """
    settings = get_settings()

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    allowed_extensions = {".pdf", ".txt", ".docx", ".doc"}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {allowed_extensions}",
        )

    # Ensure upload directory exists
    upload_dir = Path(settings.upload_directory)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = upload_dir / file.filename
    try:
        with file_path.open("wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}") from e

    # Process document
    result = pipeline.add_document(file_path)

    return DocumentUploadResponse(
        success=result.get("success", False),
        file_name=result.get("file_name"),
        chunks_added=result.get("chunks_added"),
        document_ids=result.get("document_ids"),
        error=result.get("error"),
    )


@router.post("/documents/search", response_model=SearchResponse, tags=["Documents"])
def search_documents(
    request: SearchRequest,
    pipeline: RAGPipelineDep,
) -> SearchResponse:
    """Search for similar documents without generating an answer.

    Returns the most relevant document chunks.
    """
    try:
        results = pipeline.search_similar(request.query, k=request.k)

        search_results = [
            SearchResult(
                content=doc.page_content,
                metadata=doc.metadata,
                score=None,
            )
            for doc in results
        ]

        return SearchResponse(success=True, results=search_results)
    except (RuntimeError, KeyError, AttributeError) as e:
        logger.error(f"Search error: {e}")
        return SearchResponse(success=False, error=str(e))


@router.delete("/documents", tags=["Documents"])
def clear_documents(pipeline: RAGPipelineDep) -> dict[str, str]:
    """Clear all documents from the RAG pipeline."""
    return pipeline.clear_documents()


@router.get("/stats", response_model=StatsResponse, tags=["Info"])
def get_stats(pipeline: RAGPipelineDep) -> StatsResponse:
    """Get RAG pipeline statistics."""
    stats = pipeline.get_stats()
    backend, available = get_llm_availability()

    return StatsResponse(
        collection=stats.get("collection", {}),
        llm_backend=backend,
        llm_available=available,
        model=stats.get("model", ""),
        embedding_model=stats.get("embedding_model", ""),
    )


@router.get("/models", response_model=ModelsResponse, tags=["Models"])
def list_models(
    ollama: OllamaClientDep,
    rkllm: RKLLMClientDep,
) -> ModelsResponse:
    """List available models from the configured backend."""
    settings = get_settings()
    backend = settings.llm_backend

    try:
        if backend == LLMBackend.RKLLM:
            if not rkllm.is_available():
                return ModelsResponse(
                    success=False,
                    error="RKLLM is not available. Check model path and NPU drivers.",
                )
            models_data = rkllm.list_models()
            models = [
                ModelInfo(
                    name=m.get("name", ""),
                    size=m.get("size"),
                )
                for m in models_data
            ]
        else:
            if not ollama.is_available():
                return ModelsResponse(
                    success=False,
                    error="Ollama server is not available",
                )
            models_data = ollama.list_models()
            models = [
                ModelInfo(
                    name=m.get("name", ""),
                    modified_at=m.get("modified_at"),
                    size=m.get("size"),
                )
                for m in models_data
            ]

        return ModelsResponse(success=True, models=models)
    except (httpx.RequestError, KeyError, RuntimeError) as e:
        logger.error(f"Error listing models: {e}")
        return ModelsResponse(success=False, error=str(e))


@router.get("/models/{model_name}", tags=["Models"])
def get_model_info(
    model_name: str,
    ollama: OllamaClientDep,
    rkllm: RKLLMClientDep,
) -> dict[str, Any]:
    """Get information about a specific model."""
    settings = get_settings()
    backend = settings.llm_backend

    if backend == LLMBackend.RKLLM:
        if not rkllm.is_available():
            raise HTTPException(
                status_code=503,
                detail="RKLLM is not available",
            )
        info = rkllm.get_model_info(model_name)
        if info is None:
            raise HTTPException(
                status_code=404, detail=f"Model '{model_name}' not found"
            )
        return info
    else:
        if not ollama.is_available():
            raise HTTPException(
                status_code=503, detail="Ollama server is not available"
            )
        info = ollama.get_model_info(model_name)
        if info is None:
            raise HTTPException(
                status_code=404, detail=f"Model '{model_name}' not found"
            )
        return info
