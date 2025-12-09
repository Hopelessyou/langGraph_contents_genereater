"""검색기 단위 테스트 (Mock 사용)"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from src.rag.retriever import HybridRetriever


class TestHybridRetriever:
    """HybridRetriever 테스트 (Mock 사용)"""
    
    @pytest.mark.asyncio
    async def test_search_mock(self, mock_vector_store, mock_embedding_generator):
        """검색 테스트 (Mock)"""
        with patch('src.rag.workflow.RAGWorkflow') as mock_workflow_class:
            mock_workflow = MagicMock()
            mock_workflow.run = Mock(return_value={
                "reranked_results": [
                    {
                        "id": "result-1",
                        "document": "문서 1 내용",
                        "metadata": {"type": "statute", "title": "형법 제347조"},
                        "distance": 0.1,
                    },
                    {
                        "id": "result-2",
                        "document": "문서 2 내용",
                        "metadata": {"type": "case", "title": "대법원 판결"},
                        "distance": 0.2,
                    },
                ],
                "context": "컨텍스트 텍스트",
                "error": None,
            })
            mock_workflow_class.return_value = mock_workflow
            
            retriever = HybridRetriever(
                vector_store=mock_vector_store,
                embedding_generator=mock_embedding_generator
            )
            retriever.workflow = mock_workflow
            
            result = await retriever.search(
                query="사기 범죄",
                n_results=2,
            )
            
            assert result["query"] == "사기 범죄"
            assert len(result["results"]) == 2
            assert result["total"] == 2
            assert "context" in result
            assert result["error"] is None
    
    def test_rerank_results(self):
        """결과 재랭킹 테스트"""
        retriever = HybridRetriever(
            vector_store=MagicMock(),
            embedding_generator=MagicMock()
        )
        
        results = [
            {"distance": 0.3, "id": "1"},
            {"distance": 0.1, "id": "2"},
            {"distance": 0.2, "id": "3"},
        ]
        
        reranked = retriever.rerank_results(results, "query", top_k=2)
        
        assert len(reranked) == 2
        assert reranked[0]["id"] == "2"  # 가장 작은 거리
        assert reranked[1]["id"] == "3"
        assert all("score" in r for r in reranked)

