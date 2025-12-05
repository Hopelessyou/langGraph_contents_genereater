"""에러 핸들링 및 재시도 로직"""

from typing import Callable, Any, Optional, Type
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class RetryConfig:
    """재시도 설정"""
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        retryable_exceptions: tuple = (Exception,),
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.retryable_exceptions = retryable_exceptions


def retry_on_failure(
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable] = None,
):
    """
    재시도 데코레이터
    
    Args:
        config: 재시도 설정
        on_retry: 재시도 시 호출할 콜백
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay = config.initial_delay
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt < config.max_retries:
                        logger.warning(
                            f"{func.__name__} 실패 (시도 {attempt + 1}/{config.max_retries + 1}): {str(e)}"
                        )
                        
                        if on_retry:
                            on_retry(attempt + 1, e)
                        
                        time.sleep(delay)
                        delay *= config.backoff_factor
                    else:
                        logger.error(
                            f"{func.__name__} 최종 실패: {str(e)}"
                        )
                        raise
            
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


class ErrorHandler:
    """에러 핸들러"""
    
    @staticmethod
    def handle_embedding_error(error: Exception) -> str:
        """임베딩 에러 처리"""
        error_msg = str(error)
        
        if "api key" in error_msg.lower():
            return "OpenAI API 키가 유효하지 않습니다. 환경 변수를 확인해주세요."
        elif "rate limit" in error_msg.lower():
            return "API 호출 한도에 도달했습니다. 잠시 후 다시 시도해주세요."
        elif "timeout" in error_msg.lower():
            return "요청 시간이 초과되었습니다. 네트워크 연결을 확인해주세요."
        else:
            return f"임베딩 생성 중 오류가 발생했습니다: {error_msg}"
    
    @staticmethod
    def handle_llm_error(error: Exception) -> str:
        """LLM 에러 처리"""
        error_msg = str(error)
        
        if "api key" in error_msg.lower():
            return "OpenAI API 키가 유효하지 않습니다."
        elif "rate limit" in error_msg.lower():
            return "API 호출 한도에 도달했습니다. 잠시 후 다시 시도해주세요."
        elif "context length" in error_msg.lower():
            return "컨텍스트가 너무 깁니다. 쿼리를 단순화해주세요."
        else:
            return f"응답 생성 중 오류가 발생했습니다: {error_msg}"
    
    @staticmethod
    def handle_vector_db_error(error: Exception) -> str:
        """벡터 DB 에러 처리"""
        error_msg = str(error)
        
        if "connection" in error_msg.lower():
            return "벡터 DB 연결에 실패했습니다."
        elif "not found" in error_msg.lower():
            return "요청한 문서를 찾을 수 없습니다."
        else:
            return f"벡터 DB 오류: {error_msg}"
    
    @staticmethod
    def handle_generic_error(error: Exception) -> str:
        """일반 에러 처리"""
        return f"오류가 발생했습니다: {str(error)}"

