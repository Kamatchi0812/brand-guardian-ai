from typing import List, Literal, Optional

from pydantic import BaseModel, Field


ThreatCategory = Literal["complaint", "meme", "fake_news", "neutral"]
SentimentLabel = Literal["positive", "neutral", "negative"]


class MemoryItem(BaseModel):
    id: str
    content: str
    category: str
    sentiment: str
    response: str
    created_at: str
    similarity: Optional[float] = None


class AnalysisResult(BaseModel):
    category: ThreatCategory
    sentiment: SentimentLabel
    risk_score: float = Field(ge=0.0, le=1.0)
    summary: str
    reasoning: str
    suggested_response: str
    related_memories: List[MemoryItem] = Field(default_factory=list)
    mode: Literal["gemini", "heuristic"]


class MemoryResponse(BaseModel):
    items: List[MemoryItem]


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
