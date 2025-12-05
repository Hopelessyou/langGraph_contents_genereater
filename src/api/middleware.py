"""미들웨어"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
from typing import Dict
from collections import defaultdict

from ..utils.monitoring import APIMonitor

logger = logging.getLogger(__name__)

# 전역 모니터 인스턴스
api_monitor = APIMonitor()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate Limiting 미들웨어"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts: Dict[str, list] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # 클라이언트 IP 추출
        client_ip = request.client.host if request.client else "unknown"
        
        # 현재 시간
        current_time = time.time()
        
        # 1분 이내 요청만 유지
        self.request_counts[client_ip] = [
            t for t in self.request_counts[client_ip]
            if current_time - t < 60
        ]
        
        # 요청 수 확인
        if len(self.request_counts[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.",
            )
        
        # 요청 시간 기록
        self.request_counts[client_ip].append(current_time)
        
        # 요청 처리
        response = await call_next(request)
        return response


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

