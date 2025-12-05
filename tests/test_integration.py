"""통합 테스트"""

import pytest
import json
from pathlib import Path

from src.processors import DocumentValidator, BatchProcessor
from src.rag import DocumentIndexer, VectorStore, EmbeddingGenerator


@pytest.mark.integration
class TestDataPipeline:
    """데이터 파이프라인 통합 테스트"""
    
    def test_full_pipeline(self, temp_dir, sample_statute_data):
        """전체 파이프라인 테스트"""
        # 1. JSON 파일 생성
        json_file = temp_dir / "test_statute.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(sample_statute_data, f, ensure_ascii=False)
        
        # 2. 검증
        validator = DocumentValidator()
        success, model = validator.validate_file(json_file)
        assert success is True
        
        # 3. 배치 처리
        processor = BatchProcessor()
        output_dir = temp_dir / "processed"
        results = processor.process_directory(
            input_dir=temp_dir,
            output_dir=output_dir,
            doc_type="statute",
        )
        
        assert len(results) > 0
        assert any(success for success, _ in results.values())


@pytest.mark.integration
class TestRAGWorkflow:
    """RAG 워크플로우 통합 테스트"""
    
    @pytest.mark.skip(reason="벡터 DB 및 임베딩 모델 설정 필요")
    def test_search_workflow(self):
        """검색 워크플로우 테스트"""
        from src.rag import RAGWorkflow, VectorStore, EmbeddingGenerator
        
        vector_store = VectorStore()
        embedding_gen = EmbeddingGenerator()
        workflow = RAGWorkflow(vector_store, embedding_gen)
        
        result = workflow.run("사기 범죄에 대해 알려주세요")
        
        assert "query" in result
        assert "context" in result
        assert result.get("error") is None


@pytest.mark.integration
class TestAPIIntegration:
    """API 통합 테스트"""
    
    @pytest.mark.skip(reason="전체 시스템 설정 필요")
    def test_search_to_ask_flow(self):
        """검색부터 질의응답까지 전체 플로우 테스트"""
        from fastapi.testclient import TestClient
        from src.api.main import app
        
        client = TestClient(app)
        
        # 1. 검색
        search_response = client.post(
            "/api/v1/search",
            json={"query": "사기", "n_results": 3},
        )
        assert search_response.status_code == 200
        
        # 2. 질의응답
        ask_response = client.post(
            "/api/v1/ask",
            json={"query": "사기 범죄의 처벌은?"},
        )
        assert ask_response.status_code == 200

