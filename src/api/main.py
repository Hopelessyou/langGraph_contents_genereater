"""FastAPI 메인 애플리케이션"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from config.settings import settings
from .routers import search, ask, health, admin, monitoring
from .middleware import RateLimitMiddleware, LoggingMiddleware
from ..utils.logging_config import setup_logging

logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="IBS 법률 AI 시스템 API",
    description="법률 정보 RAG 기반 질의응답 API",
    version="0.1.0",
)

# 미들웨어 추가 (순서 중요)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 로깅 설정
setup_logging()

# 라우터 등록
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(ask.router, prefix="/api/v1", tags=["ask"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(monitoring.router, prefix="/api/v1", tags=["monitoring"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 핸들러"""
    logger.error(f"예외 발생: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "내부 서버 오류가 발생했습니다."},
    )


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    logger.info("IBS 법률 AI 시스템 API 서버 시작")
    logger.info(f"환경: {settings.log_level}")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    logger.info("IBS 법률 AI 시스템 API 서버 종료")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )

