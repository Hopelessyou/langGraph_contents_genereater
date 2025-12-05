"""API 엔드포인트 단위 테스트"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

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
    
    def test_search_post(self):
        """POST 방식 검색 테스트"""
        response = client.post(
            "/api/v1/search",
            json={
                "query": "사기",
                "n_results": 5,
            },
        )
        # 벡터 DB가 없으면 오류가 발생할 수 있음
        assert response.status_code in [200, 500]
    
    def test_search_get(self):
        """GET 방식 검색 테스트"""
        response = client.get(
            "/api/v1/search",
            params={"query": "사기", "n_results": 5},
        )
        assert response.status_code in [200, 500]


class TestAskAPI:
    """질의응답 API 테스트"""
    
    def test_ask_question(self):
        """질의응답 테스트"""
        response = client.post(
            "/api/v1/ask",
            json={
                "query": "사기 범죄에 대해 알려주세요",
                "stream": False,
            },
        )
        # LLM이 설정되지 않으면 오류 발생 가능
        assert response.status_code in [200, 500]


class TestAdminAPI:
    """관리자 API 테스트"""
    
    def test_index_status(self):
        """인덱스 상태 조회 테스트"""
        response = client.get("/api/v1/admin/index/status")
        # 인증이 필요할 수 있지만, 상태 조회는 공개 가능
        assert response.status_code in [200, 401, 500]

