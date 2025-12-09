"""통합 테스트"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch

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
    
    def test_vector_store_integration(self, temp_dir, request):
        """벡터 스토어 통합 테스트"""
        # 통합 테스트는 --run-integration 플래그로 실행
        if not request.config.getoption("--run-integration", default=False):
            pytest.skip("통합 테스트는 --run-integration 플래그 필요")
        """벡터 스토어 통합 테스트"""
        import chromadb
        from src.rag.vector_store import VectorStore
        from src.models import StatuteModel
        
        # 임시 ChromaDB 경로 사용
        with patch('config.settings.settings') as mock_settings:
            mock_settings.vector_db_type = "chroma"
            mock_settings.chroma_persist_path = temp_dir / "test_vector_db"
            
            vector_store = VectorStore(collection_name="test_collection")
            
            # 테스트 문서 생성
            test_doc = StatuteModel(
                id="test-doc-1",
                category="형사",
                sub_category="사기",
                type="statute",
                title="형법 제347조",
                content="제1조 사기 범죄에 대한 조문입니다.",
            )
            
            # 임베딩 Mock (실제 API 호출 없이)
            test_embedding = [0.1] * 1536
            
            # 문서 추가
            ids = vector_store.add_documents(
                documents=[test_doc],
                embeddings=[test_embedding],
            )
            
            assert len(ids) == 1
            assert ids[0] == "test-doc-1"
            
            # 검색 테스트
            results = vector_store.search(
                query_embedding=test_embedding,
                n_results=1,
            )
            
            assert "ids" in results
            assert len(results["ids"][0]) > 0


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

