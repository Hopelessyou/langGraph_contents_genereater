"""임베딩 생성기 단위 테스트 (Mock 사용)"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from src.rag.embedding import EmbeddingGenerator


class TestEmbeddingGenerator:
    """EmbeddingGenerator 테스트 (Mock 사용)"""
    
    @pytest.mark.asyncio
    async def test_embed_text_mock(self, mock_openai_embeddings):
        """단일 텍스트 임베딩 생성 테스트 (Mock)"""
        with patch('src.rag.embedding.OpenAIEmbeddings', return_value=mock_openai_embeddings):
            with patch('src.rag.embedding.settings') as mock_settings:
                mock_settings.openai_api_key = "test-key"
                mock_settings.embedding_model = "text-embedding-3-small"
                
                generator = EmbeddingGenerator()
                generator.embeddings = mock_openai_embeddings
                
                result = await generator.embed_text("테스트 텍스트")
                
                assert len(result) == 1536
                assert all(isinstance(x, float) for x in result)
                mock_openai_embeddings.embed_query.assert_called_once_with("테스트 텍스트")
    
    @pytest.mark.asyncio
    async def test_embed_texts_mock(self, mock_openai_embeddings):
        """일괄 텍스트 임베딩 생성 테스트 (Mock)"""
        with patch('src.rag.embedding.OpenAIEmbeddings', return_value=mock_openai_embeddings):
            with patch('src.rag.embedding.settings') as mock_settings:
                mock_settings.openai_api_key = "test-key"
                mock_settings.embedding_model = "text-embedding-3-small"
                
                generator = EmbeddingGenerator()
                generator.embeddings = mock_openai_embeddings
                
                texts = ["텍스트 1", "텍스트 2", "텍스트 3"]
                results = await generator.embed_texts(texts)
                
                assert len(results) == 3
                assert all(len(r) == 1536 for r in results)
                mock_openai_embeddings.embed_documents.assert_called_once_with(texts)
    
    def test_get_embedding_dimension(self):
        """임베딩 차원 반환 테스트"""
        with patch('src.rag.embedding.OpenAIEmbeddings'):
            with patch('src.rag.embedding.settings') as mock_settings:
                mock_settings.openai_api_key = "test-key"
                mock_settings.embedding_model = "text-embedding-3-large"
                
                generator = EmbeddingGenerator()
                dimension = generator.get_embedding_dimension()
                
                assert dimension == 3072
    
    def test_get_embedding_dimension_small(self):
        """작은 모델의 임베딩 차원 테스트"""
        with patch('src.rag.embedding.OpenAIEmbeddings'):
            with patch('src.rag.embedding.settings') as mock_settings:
                mock_settings.openai_api_key = "test-key"
                mock_settings.embedding_model = "text-embedding-3-small"
                
                generator = EmbeddingGenerator()
                dimension = generator.get_embedding_dimension()
                
                assert dimension == 1536

