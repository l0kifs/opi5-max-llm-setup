"""API routes for RAG and LLM services."""

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

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
from opi5_max_llm_setup.config.settings import get_settings
from opi5_max_llm_setup.llm.ollama_client import OllamaClient
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


# Type aliases for dependency injection
RAGPipelineDep = Annotated[RAGPipeline, Depends(get_rag_pipeline)]
OllamaClientDep = Annotated[OllamaClient, Depends(get_ollama)]


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    """Check API health and Ollama availability."""
    settings = get_settings()
    ollama = get_ollama()
    return HealthResponse(
        status="healthy",
        ollama_available=ollama.is_available(),
        version=settings.app_version,
    )


@router.post("/query", response_model=QueryResponse, tags=["RAG"])
def query_documents(
    request: QueryRequest,
    pipeline: RAGPipelineDep,
) -> QueryResponse:
    """
    Query the RAG pipeline with a question.

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
) -> ChatResponse:
    """
    Chat directly with the LLM without RAG context.

    Use this for general questions that don't require document context.
    """
    if not ollama.is_available():
        return ChatResponse(
            success=False,
            error="Ollama server is not available",
        )

    try:
        response = ollama.generate(request.prompt)
        return ChatResponse(success=True, response=response)
    except Exception as e:
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
    """
    Upload a document to the RAG pipeline.

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
    """
    Search for similar documents without generating an answer.

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
    except Exception as e:
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

    return StatsResponse(
        collection=stats.get("collection", {}),
        ollama_available=stats.get("ollama_available", False),
        model=stats.get("model", ""),
        embedding_model=stats.get("embedding_model", ""),
    )


@router.get("/models", response_model=ModelsResponse, tags=["Models"])
def list_models(ollama: OllamaClientDep) -> ModelsResponse:
    """List available Ollama models."""
    if not ollama.is_available():
        return ModelsResponse(
            success=False,
            error="Ollama server is not available",
        )

    try:
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
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return ModelsResponse(success=False, error=str(e))


@router.get("/models/{model_name}", tags=["Models"])
def get_model_info(model_name: str, ollama: OllamaClientDep) -> dict[str, Any]:
    """Get information about a specific model."""
    if not ollama.is_available():
        raise HTTPException(status_code=503, detail="Ollama server is not available")

    info = ollama.get_model_info(model_name)
    if info is None:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")

    return info
