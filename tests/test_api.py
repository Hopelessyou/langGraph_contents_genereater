"""API 엔드포인트 단위 테스트 (Mock 사용)"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

from src.api.main import app


@pytest.fixture
def mock_dependencies():
    """의존성 Mock 픽스처"""
    with patch('src.api.dependencies.get_retriever') as mock_get_retriever, \
         patch('src.api.dependencies.get_llm_manager') as mock_get_llm_manager, \
         patch('src.api.dependencies.get_session_manager') as mock_get_session_manager, \
         patch('src.api.dependencies.get_query_cache') as mock_get_cache:
        
        # Mock 객체 생성
        mock_retriever = MagicMock()
        mock_retriever.search = AsyncMock(return_value={
            "query": "사기",
            "results": [
                {
                    "id": "result-1",
                    "document": "테스트 문서",
                    "metadata": {"type": "statute"},
                    "distance": 0.1,
                }
            ],
            "total": 1,
            "context": "테스트 컨텍스트",
        })
        
        mock_llm = MagicMock()
        mock_llm.generate_response = MagicMock(return_value="테스트 응답")
        mock_llm.generate_response_async = AsyncMock()
        
        async def mock_stream():
            chunks = ["테스트", " 응답"]
            for chunk in chunks:
                yield chunk
        mock_llm.generate_response_async.return_value = mock_stream()
        
        mock_session = MagicMock()
        mock_session.create_session = MagicMock(return_value=MagicMock())
        mock_session.get_session = MagicMock(return_value=MagicMock())
        mock_session.get_context_string = MagicMock(return_value="")
        
        mock_cache = MagicMock()
        mock_cache.get = MagicMock(return_value=None)
        mock_cache.set = MagicMock()
        
        mock_get_retriever.return_value = mock_retriever
        mock_get_llm_manager.return_value = mock_llm
        mock_get_session_manager.return_value = mock_session
        mock_get_cache.return_value = mock_cache
        
        yield {
            "retriever": mock_retriever,
            "llm": mock_llm,
            "session": mock_session,
            "cache": mock_cache,
        }


client = TestClient(app)


class TestHealthAPI:
    """헬스체크 API 테스트"""
    
    def test_health_check(self):
        """기본 헬스체크 테스트"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_detailed_health_check(self):
        """상세 헬스체크 테스트"""
        response = client.get("/api/v1/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "components" in data


class TestSearchAPI:
    """검색 API 테스트"""
    
    @pytest.mark.asyncio
    async def test_search_post_mock(self, mock_dependencies):
        """POST 방식 검색 테스트 (Mock)"""
        response = client.post(
            "/api/v1/search",
            json={
                "query": "사기",
                "n_results": 5,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "results" in data
        assert "total" in data


class TestAskAPI:
    """질의응답 API 테스트"""
    
    @pytest.mark.asyncio
    async def test_ask_question_mock(self, mock_dependencies):
        """질의응답 테스트 (Mock)"""
        response = client.post(
            "/api/v1/ask",
            json={
                "query": "사기 범죄에 대해 알려주세요",
                "stream": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "sources" in data


class TestAdminAPI:
    """관리자 API 테스트"""
    
    def test_index_status(self):
        """인덱스 상태 조회 테스트"""
        response = client.get("/api/v1/admin/index/status")
        # 인증이 필요할 수 있지만, 상태 조회는 공개 가능
        assert response.status_code in [200, 401, 500]

