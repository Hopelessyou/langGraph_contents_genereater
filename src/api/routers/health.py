"""헬스체크 API"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

from ...rag import VectorStore, EmbeddingGenerator
from config.settings import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """헬스체크 응답"""
    status: str
    version: str
    timestamp: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """헬스체크"""
    from datetime import datetime
    
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now().isoformat(),
    )


@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """상세 헬스체크"""
    from datetime import datetime
    
    health_status = {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat(),
        "components": {},
    }
    
    # 벡터 DB 상태 확인
    try:
        vector_store = VectorStore()
        count = vector_store.get_count()
        health_status["components"]["vector_db"] = {
            "status": "healthy",
            "document_count": count,
        }
    except Exception as e:
        health_status["components"]["vector_db"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        health_status["status"] = "degraded"
    
    # 임베딩 모델 상태 확인
    try:
        embedding_gen = EmbeddingGenerator()
        health_status["components"]["embedding"] = {
            "status": "healthy",
            "model": settings.embedding_model,
        }
    except Exception as e:
        health_status["components"]["embedding"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        health_status["status"] = "degraded"
    
    return health_status

