"""LLM 관리 및 응답 생성"""

from typing import Optional, AsyncIterator, Dict, Any
import logging

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from config.settings import settings
from .prompts import PromptTemplates, ContextOptimizer

logger = logging.getLogger(__name__)


class LLMManager:
    """LLM 관리자"""
    
    def __init__(self, model_name: Optional[str] = None, temperature: float = 0.3):
        self.model_name = model_name or settings.llm_model
        self.temperature = temperature
        self.llm = None
        self.token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }
        self._initialize()
    
    def _initialize(self):
        """LLM 초기화"""
        if not OPENAI_AVAILABLE:
            raise ImportError("langchain-openai가 설치되지 않았습니다.")
        
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        self.llm = ChatOpenAI(
            model_name=self.model_name,
            temperature=self.temperature,
            openai_api_key=settings.openai_api_key,
        )
        logger.info(f"LLM 초기화: {self.model_name}")
    
    def generate_response(
        self,
        context: str,
        query: str,
        document_types: Optional[list] = None,
        stream: bool = False,
    ) -> str:
        """
        응답 생성
        
        Args:
            context: 컨텍스트
            query: 사용자 쿼리
            document_types: 문서 타입 리스트
            stream: 스트리밍 여부
            
        Returns:
            생성된 응답
        """
        try:
            # 컨텍스트 최적화
            optimized_context = ContextOptimizer.optimize_context(context)
            
            # 프롬프트 구성
            user_prompt = PromptTemplates.build_user_prompt(
                context=optimized_context,
                query=query,
                document_types=document_types,
            )
            
            # 메시지 구성
            messages = [
                SystemMessage(content=PromptTemplates.SYSTEM_PROMPT),
                HumanMessage(content=user_prompt),
            ]
            
            # 응답 생성
            if stream:
                # 스트리밍은 별도 메서드로 처리
                return self._generate_streaming_response(messages)
            else:
                response = self.llm.invoke(messages)
                
                # 토큰 사용량 추적 (응답에 포함된 경우)
                if hasattr(response, "response_metadata"):
                    usage = response.response_metadata.get("token_usage", {})
                    if usage:
                        self.token_usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
                        self.token_usage["completion_tokens"] += usage.get("completion_tokens", 0)
                        self.token_usage["total_tokens"] += usage.get("total_tokens", 0)
                
                return response.content
            
        except Exception as e:
            logger.error(f"응답 생성 실패: {str(e)}")
            raise
    
    def _generate_streaming_response(self, messages: list) -> str:
        """스트리밍 응답 생성 (간단 구현)"""
        # 실제 스트리밍은 async로 구현해야 함
        # 여기서는 동기 방식으로 구현
        response = self.llm.invoke(messages)
        return response.content
    
    async def generate_response_async(
        self,
        context: str,
        query: str,
        document_types: Optional[list] = None,
    ) -> AsyncIterator[str]:
        """
        비동기 스트리밍 응답 생성
        
        Args:
            context: 컨텍스트
            query: 사용자 쿼리
            document_types: 문서 타입 리스트
            
        Yields:
            응답 청크
        """
        try:
            # 컨텍스트 최적화
            optimized_context = ContextOptimizer.optimize_context(context)
            
            # 프롬프트 구성
            user_prompt = PromptTemplates.build_user_prompt(
                context=optimized_context,
                query=query,
                document_types=document_types,
            )
            
            # 메시지 구성
            messages = [
                SystemMessage(content=PromptTemplates.SYSTEM_PROMPT),
                HumanMessage(content=user_prompt),
            ]
            
            # 스트리밍 응답
            async for chunk in self.llm.astream(messages):
                if hasattr(chunk, "content"):
                    yield chunk.content
                else:
                    yield str(chunk)
            
        except Exception as e:
            logger.error(f"스트리밍 응답 생성 실패: {str(e)}")
            raise
    
    def get_token_usage(self) -> Dict[str, int]:
        """토큰 사용량 반환"""
        return self.token_usage.copy()
    
    def reset_token_usage(self):
        """토큰 사용량 초기화"""
        self.token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

