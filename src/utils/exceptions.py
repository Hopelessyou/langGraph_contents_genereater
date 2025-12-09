"""커스텀 예외 클래스"""

from typing import Optional, Dict, Any


class LegalAIException(Exception):
    """기본 예외 클래스"""
    
    def __init__(
        self, 
        message: str, 
        code: str = "GENERAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """예외를 딕셔너리로 변환"""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class VectorStoreError(LegalAIException):
    """벡터 스토어 관련 에러"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VECTOR_STORE_ERROR", details)


class EmbeddingError(LegalAIException):
    """임베딩 생성 에러"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "EMBEDDING_ERROR", details)


class SearchError(LegalAIException):
    """검색 에러"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "SEARCH_ERROR", details)


class LLMError(LegalAIException):
    """LLM 관련 에러"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "LLM_ERROR", details)


class SessionError(LegalAIException):
    """세션 관리 에러"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "SESSION_ERROR", details)


class ValidationError(LegalAIException):
    """데이터 검증 에러"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class ConfigurationError(LegalAIException):
    """설정 관련 에러"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIGURATION_ERROR", details)

