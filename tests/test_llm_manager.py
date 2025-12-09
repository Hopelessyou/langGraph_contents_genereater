"""LLM 관리자 단위 테스트 (Mock 사용)"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from src.rag.llm_manager import LLMManager


class TestLLMManager:
    """LLMManager 테스트 (Mock 사용)"""
    
    def test_generate_response_mock(self, mock_chat_openai):
        """응답 생성 테스트 (Mock)"""
        with patch('src.rag.llm_manager.ChatOpenAI', return_value=mock_chat_openai):
            with patch('src.rag.llm_manager.settings') as mock_settings:
                mock_settings.openai_api_key = "test-key"
                mock_settings.llm_model = "gpt-4-turbo-preview"
                
                manager = LLMManager()
                manager.llm = mock_chat_openai
                
                response = manager.generate_response(
                    context="테스트 컨텍스트",
                    query="테스트 질문",
                )
                
                assert response == "테스트 응답입니다."
                assert mock_chat_openai.invoke.called
    
    @pytest.mark.asyncio
    async def test_generate_response_async_mock(self, mock_chat_openai):
        """비동기 스트리밍 응답 생성 테스트 (Mock)"""
        with patch('src.rag.llm_manager.ChatOpenAI', return_value=mock_chat_openai):
            with patch('src.rag.llm_manager.settings') as mock_settings:
                mock_settings.openai_api_key = "test-key"
                mock_settings.llm_model = "gpt-4-turbo-preview"
                
                manager = LLMManager()
                manager.llm = mock_chat_openai
                
                chunks = []
                async for chunk in manager.generate_response_async(
                    context="테스트 컨텍스트",
                    query="테스트 질문",
                ):
                    chunks.append(chunk)
                
                assert len(chunks) > 0
                assert "".join(chunks) == "테스트 응답입니다."
    
    def test_get_token_usage(self):
        """토큰 사용량 조회 테스트"""
        with patch('src.rag.llm_manager.ChatOpenAI'):
            with patch('src.rag.llm_manager.settings') as mock_settings:
                mock_settings.openai_api_key = "test-key"
                mock_settings.llm_model = "gpt-4-turbo-preview"
                
                manager = LLMManager()
                usage = manager.get_token_usage()
                
                assert "prompt_tokens" in usage
                assert "completion_tokens" in usage
                assert "total_tokens" in usage
    
    def test_reset_token_usage(self):
        """토큰 사용량 초기화 테스트"""
        with patch('src.rag.llm_manager.ChatOpenAI'):
            with patch('src.rag.llm_manager.settings') as mock_settings:
                mock_settings.openai_api_key = "test-key"
                mock_settings.llm_model = "gpt-4-turbo-preview"
                
                manager = LLMManager()
                manager.token_usage = {
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "total_tokens": 150,
                }
                
                manager.reset_token_usage()
                
                assert manager.token_usage["prompt_tokens"] == 0
                assert manager.token_usage["completion_tokens"] == 0
                assert manager.token_usage["total_tokens"] == 0

