"""인증 및 보안"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Optional
import os

# API 키 헤더
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_key() -> Optional[str]:
    """환경 변수에서 API 키 가져오기"""
    return os.getenv("API_KEY")


def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    API 키 검증
    
    Args:
        api_key: 요청의 API 키
        
    Returns:
        검증된 API 키
        
    Raises:
        HTTPException: API 키가 유효하지 않은 경우
    """
    expected_key = get_api_key()
    
    # API 키가 설정되지 않은 경우 인증 건너뛰기
    if not expected_key:
        return ""
    
    if not api_key or api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 API 키입니다.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return api_key

