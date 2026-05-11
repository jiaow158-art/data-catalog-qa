from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class QaRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500, description="用户自然语言问题")
    use_llm: bool = Field(False, description="是否使用 LLM 润色答案")


class QaResponse(BaseModel):
    question: str
    answer: str
    intent: str
    confidence: float
    entities: dict[str, Optional[str]]
    used_llm: bool = False


class LLMConfigResponse(BaseModel):
    """Current LLM configuration (API key is masked)."""
    provider: str
    model: str
    base_url: str
    api_key_configured: bool
    max_tokens: int
    temperature: float


class LLMConfigUpdate(BaseModel):
    """Update LLM configuration at runtime."""
    api_key: Optional[str] = Field(None, max_length=200)
    base_url: Optional[str] = Field(None, max_length=500)
    model: Optional[str] = Field(None, max_length=100)


class LLMTestResponse(BaseModel):
    """Result of testing the LLM connection."""
    ok: bool
    message: str
    model: str = ""
    latency_ms: int = 0


class LLMTestRequest(BaseModel):
    """Optional overrides for testing. If not provided, uses current runtime/settings config."""
    api_key: Optional[str] = Field(None, max_length=200)
    base_url: Optional[str] = Field(None, max_length=500)
    model: Optional[str] = Field(None, max_length=100)
