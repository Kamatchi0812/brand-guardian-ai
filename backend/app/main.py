from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import Settings, get_settings
from backend.app.models import AnalysisResult, HealthResponse, MemoryResponse
from backend.app.services.analyzer import BrandAnalyzer
from backend.app.services.gemini_client import GeminiClient
from backend.app.services.memory import MemoryService


# ✅ CREATE APP FIRST (IMPORTANT)
app = FastAPI(
    title="Real-Time Multimodal Brand Guardian System",
    version="0.1.0"
)

# ✅ MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ DEPENDENCIES
def get_memory_service(
    settings: Annotated[Settings, Depends(get_settings)]
) -> MemoryService:
    if not hasattr(app.state, "memory_service"):
        app.state.memory_service = MemoryService(settings)
    return app.state.memory_service


def get_gemini_client(
    settings: Annotated[Settings, Depends(get_settings)]
) -> GeminiClient:
    if not hasattr(app.state, "gemini_client"):
        app.state.gemini_client = GeminiClient(settings)
    return app.state.gemini_client


def get_analyzer() -> BrandAnalyzer:
    return BrandAnalyzer()


# ✅ HEALTH CHECK
@app.get("/health", response_model=HealthResponse)
def health(
    settings: Annotated[Settings, Depends(get_settings)]
) -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
    )


# ✅ MEMORY ENDPOINT
@app.get("/api/v1/memory", response_model=MemoryResponse)
def list_memory(
    memory_service: Annotated[MemoryService, Depends(get_memory_service)],
) -> MemoryResponse:
    return MemoryResponse(items=memory_service.list_items())


# ✅ MAIN ANALYZE ENDPOINT (FIXED)
@app.post("/api/v1/analyze", response_model=AnalysisResult)
async def analyze_content(
    text: Annotated[str, Form(...)],
    image: UploadFile | None = File(None),   # ✅ FIXED HERE
    memory_service: Annotated[MemoryService, Depends(get_memory_service)] = None,
    gemini_client: Annotated[GeminiClient, Depends(get_gemini_client)] = None,
    analyzer: Annotated[BrandAnalyzer, Depends(get_analyzer)] = None,
) -> AnalysisResult:

    # Read image if present
    image_bytes = await image.read() if image else None

    # Get related memory
    related_memories = memory_service.query(text)

    # AI Analysis
    if gemini_client.enabled:
        try:
            payload = gemini_client.analyze(
                text=text,
                image_bytes=image_bytes,
                related_memories=[item.model_dump() for item in related_memories],
            )
            result = analyzer.from_gemini(payload, related_memories)

        except Exception:
            result = analyzer.heuristic_analyze(
                text=text,
                has_image=image_bytes is not None,
                related_memories=related_memories,
            )
    else:
        result = analyzer.heuristic_analyze(
            text=text,
            has_image=image_bytes is not None,
            related_memories=related_memories,
        )

    # Store memory
    memory_service.add_memory(
        content=text,
        category=result.category,
        sentiment=result.sentiment,
        response=result.suggested_response,
    )

    return result