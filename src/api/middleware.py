"""미들웨어"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
from typing import Dict, Optional
from collections import defaultdict

from ..utils.monitoring import APIMonitor
from config.settings import settings

logger = logging.getLogger(__name__)

# 전역 모니터 인스턴스
api_monitor = APIMonitor()


class PathBasedRateLimitMiddleware(BaseHTTPMiddleware):
    """경로별 Rate Limiting 미들웨어"""
    
    def __init__(self, app, default_limit: Optional[int] = None):
        super().__init__(app)
        self.default_limit = default_limit or settings.rate_limit_default
        
        # 경로별 제한 설정
        self.path_limits: Dict[str, int] = {
            "/api/v1/ask": settings.rate_limit_ask,
            "/api/v1/ask/stream": settings.rate_limit_ask,
            "/api/v1/search": settings.rate_limit_search,
            "/api/v1/generate": settings.rate_limit_generate,
            "/api/v1/admin": settings.rate_limit_admin,
        }
        
        # IP별 경로별 요청 카운트: {ip: {path: [timestamps]}}
        self.request_counts: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
    
    def _get_limit_for_path(self, path: str) -> int:
        """경로에 대한 Rate Limit 반환"""
        # 정확한 경로 매칭
        if path in self.path_limits:
            return self.path_limits[path]
        
        # 경로 시작 부분으로 매칭
        for pattern, limit in self.path_limits.items():
            if path.startswith(pattern):
                return limit
        
        # 기본 제한
        return self.default_limit
    
    async def dispatch(self, request: Request, call_next):
        # 클라이언트 IP 추출
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        
        # 경로에 대한 제한 가져오기
        limit = self._get_limit_for_path(path)
        
        # 현재 시간
        current_time = time.time()
        
        # 1분 이내 요청만 유지
        self.request_counts[client_ip][path] = [
            t for t in self.request_counts[client_ip][path]
            if current_time - t < 60
        ]
        
        # 요청 수 확인
        if len(self.request_counts[client_ip][path]) >= limit:
            logger.warning(
                f"Rate limit exceeded for {client_ip} on {path} "
                f"({len(self.request_counts[client_ip][path])}/{limit})"
            )
            raise HTTPException(
                status_code=429,
                detail=f"요청 한도를 초과했습니다. ({limit}회/분) 잠시 후 다시 시도해주세요.",
                headers={"X-RateLimit-Limit": str(limit), "X-RateLimit-Remaining": "0"},
            )
        
        # 요청 시간 기록
        self.request_counts[client_ip][path].append(current_time)
        
        # 요청 처리
        response = await call_next(request)
        
        # Rate Limit 헤더 추가
        remaining = limit - len(self.request_counts[client_ip][path])
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time) + 60)
        
        return response


# 하위 호환성을 위한 별칭
RateLimitMiddleware = PathBasedRateLimitMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """로깅 미들웨어"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 요청 로깅
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        # 요청 처리
        response = await call_next(request)
        
        # 응답 시간 계산
        process_time = time.time() - start_time
        
        # 모니터링 기록
        api_monitor.record_request(
            endpoint=request.url.path,
            method=request.method,
            response_time=process_time,
            status_code=response.status_code,
        )
        
        # 응답 로깅
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        # 응답 헤더에 처리 시간 추가
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

