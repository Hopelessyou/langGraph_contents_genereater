"""성능 테스트"""

import pytest
import time
from unittest.mock import Mock, patch


@pytest.mark.slow
class TestPerformance:
    """성능 테스트"""
    
    def test_search_performance(self):
        """검색 성능 테스트"""
        from src.rag import HybridRetriever, VectorStore, EmbeddingGenerator
        
        # 실제 벡터 DB가 없으면 스킵
        pytest.skip("벡터 DB 설정 필요")
        
        retriever = HybridRetriever(
            VectorStore(),
            EmbeddingGenerator(),
        )
        
        start_time = time.time()
        result = retriever.search("사기", n_results=5)
        elapsed = time.time() - start_time
        
        assert elapsed < 2.0  # 2초 이내
        assert result is not None
    
    def test_batch_processing_performance(self):
        """배치 처리 성능 테스트"""
        from src.processors import BatchProcessor
        
        # 대량 데이터 처리 성능 테스트
        # 실제 구현 시 데이터 준비 필요
        pytest.skip("대량 데이터 준비 필요")


@pytest.mark.slow
class TestConcurrency:
    """동시성 테스트"""
    
    def test_concurrent_requests(self):
        """동시 요청 처리 테스트"""
        import concurrent.futures
        from fastapi.testclient import TestClient
        from src.api.main import app
        
        client = TestClient(app)
        
        def make_request():
            return client.get("/api/v1/health")
        
        # 10개의 동시 요청
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # 모든 요청이 성공해야 함
        assert all(r.status_code == 200 for r in results)

