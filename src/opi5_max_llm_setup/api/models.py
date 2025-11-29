"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for RAG queries."""

    question: str = Field(..., description="Question to ask the RAG pipeline")
    k: int | None = Field(None, description="Number of documents to retrieve", ge=1)


class QueryResponse(BaseModel):
    """Response model for RAG queries."""

    success: bool
    answer: str | None = None
    sources: list[dict[str, object]] | None = None
    error: str | None = None


class ChatRequest(BaseModel):
    """Request model for direct chat with LLM."""

    prompt: str = Field(..., description="Prompt to send to the LLM")


class ChatResponse(BaseModel):
    """Response model for chat."""

    success: bool
    response: str | None = None
    error: str | None = None


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""

    success: bool
    file_name: str | None = None
    chunks_added: int | None = None
    document_ids: list[str] | None = None
    error: str | None = None


class SearchRequest(BaseModel):
    """Request model for similarity search."""

    query: str = Field(..., description="Search query")
    k: int = Field(default=5, description="Number of results", ge=1, le=20)


class SearchResult(BaseModel):
    """Single search result."""

    content: str
    metadata: dict[str, object]
    score: float | None = None


class SearchResponse(BaseModel):
    """Response model for similarity search."""

    success: bool
    results: list[SearchResult] | None = None
    error: str | None = None


class StatsResponse(BaseModel):
    """Response model for pipeline statistics."""

    collection: dict[str, object]
    ollama_available: bool
    model: str
    embedding_model: str


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    ollama_available: bool
    version: str


class ModelInfo(BaseModel):
    """Model information."""

    name: str
    modified_at: str | None = None
    size: int | None = None


class ModelsResponse(BaseModel):
    """Response model for available models."""

    success: bool
    models: list[ModelInfo] | None = None
    error: str | None = None
