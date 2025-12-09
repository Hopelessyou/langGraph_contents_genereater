"""FastAPI 메인 애플리케이션"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from config.settings import settings
from .routers import search, ask, health, admin, monitoring, generate
from .middleware import RateLimitMiddleware, LoggingMiddleware
from ..utils.logging_config import setup_logging
from ..utils.exceptions import LegalAIException

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # Startup
    logger.info("IBS 법률 AI 시스템 API 서버 시작")
    logger.info(f"환경: {settings.log_level}")
    yield
    # Shutdown
    logger.info("IBS 법률 AI 시스템 API 서버 종료")


# FastAPI 앱 생성
app = FastAPI(
    title="IBS 법률 AI 시스템 API",
    description="법률 정보 RAG 기반 질의응답 API",
    version="0.1.0",
    lifespan=lifespan,
)

# 미들웨어 추가 (순서 중요)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, default_limit=settings.rate_limit_default)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 로깅 설정
setup_logging()

# 라우터 등록
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(ask.router, prefix="/api/v1", tags=["ask"])
app.include_router(generate.router, prefix="/api/v1", tags=["generate"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(monitoring.router, prefix="/api/v1", tags=["monitoring"])


@app.exception_handler(LegalAIException)
async def legal_ai_exception_handler(request, exc: LegalAIException):
    """LegalAI 커스텀 예외 핸들러"""
    logger.error(f"LegalAI 예외 발생: {exc.code} - {exc.message}", exc_info=True)
    return JSONResponse(
        status_code=400,
        content=exc.to_dict(),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 핸들러"""
    logger.error(f"예외 발생: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "내부 서버 오류가 발생했습니다.",
                "details": {}
            }
        },
    )


if __name__ == "__main__":
    """직접 실행 시"""
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )

