"""pytest 설정 및 픽스처"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, AsyncMock
import numpy as np


def pytest_addoption(parser):
    """pytest 커맨드라인 옵션 추가"""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="통합 테스트 실행 (실제 DB/API 사용)",
    )


@pytest.fixture
def temp_dir():
    """임시 디렉토리 픽스처"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_embedding_generator():
    """Mock EmbeddingGenerator 픽스처"""
    from unittest.mock import AsyncMock
    
    mock_gen = MagicMock()
    mock_gen.embed_text = AsyncMock(return_value=[0.1] * 1536)  # 기본 임베딩 차원
    mock_gen.embed_texts = AsyncMock(return_value=[[0.1] * 1536] * 3)
    mock_gen.get_embedding_dimension = Mock(return_value=1536)
    mock_gen.model_name = "text-embedding-3-small"
    
    return mock_gen


@pytest.fixture
def mock_llm_manager():
    """Mock LLMManager 픽스처"""
    from unittest.mock import AsyncMock
    
    mock_llm = MagicMock()
    mock_llm.generate_response = Mock(return_value="테스트 응답입니다.")
    mock_llm.generate_response_async = AsyncMock()
    
    # 스트리밍 응답 Mock
    async def mock_stream():
        chunks = ["테스트", " 응답", "입니다."]
        for chunk in chunks:
            yield chunk
    
    mock_llm.generate_response_async.return_value = mock_stream()
    mock_llm.get_token_usage = Mock(return_value={
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "total_tokens": 150,
    })
    
    return mock_llm


@pytest.fixture
def mock_vector_store():
    """Mock VectorStore 픽스처"""
    from unittest.mock import AsyncMock
    
    mock_store = MagicMock()
    mock_store.add_documents = AsyncMock(return_value=["doc-1", "doc-2"])
    mock_store.search = AsyncMock(return_value={
        "ids": [["result-1", "result-2"]],
        "documents": [["문서 1 내용", "문서 2 내용"]],
        "metadatas": [[{"type": "statute"}, {"type": "case"}]],
        "distances": [[0.1, 0.2]],
    })
    mock_store.get_count = AsyncMock(return_value=100)
    mock_store.delete = AsyncMock()
    mock_store.update = AsyncMock()
    mock_store.reset = AsyncMock()
    
    return mock_store


@pytest.fixture
def mock_openai_embeddings():
    """Mock OpenAIEmbeddings 픽스처"""
    mock_embeddings = MagicMock()
    mock_embeddings.embed_query = Mock(return_value=[0.1] * 1536)
    mock_embeddings.embed_documents = Mock(return_value=[[0.1] * 1536] * 3)
    return mock_embeddings


@pytest.fixture
def mock_chat_openai():
    """Mock ChatOpenAI 픽스처"""
    from unittest.mock import AsyncMock
    
    mock_chat = MagicMock()
    
    # 동기 응답 Mock
    mock_response = MagicMock()
    mock_response.content = "테스트 응답입니다."
    mock_response.response_metadata = {
        "token_usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        }
    }
    mock_chat.invoke = Mock(return_value=mock_response)
    
    # 비동기 스트리밍 응답 Mock
    async def mock_astream(messages):
        chunks = [
            MagicMock(content="테스트"),
            MagicMock(content=" 응답"),
            MagicMock(content="입니다."),
        ]
        for chunk in chunks:
            yield chunk
    
    mock_chat.astream = AsyncMock(side_effect=mock_astream)
    
    return mock_chat


@pytest.fixture
def sample_statute_data():
    """샘플 법령 데이터 픽스처"""
    return {
        "id": "statute-test-1",
        "category": "형사",
        "sub_category": "사기",
        "type": "statute",
        "title": "형법 제347조(사기)",
        "content": "① 사람을 기망하여 재물의 교부를 받거나 재산상의 이익을 취득한 자는 10년 이하의 징역 또는 2천만원 이하의 벌금에 처한다.",
        "metadata": {
            "law_name": "형법",
            "article_number": "347",
            "topics": ["사기", "편취"],
            "source": "법제처",
            "updated_at": "2024-01-01",
        },
    }


@pytest.fixture
def sample_case_data():
    """샘플 판례 데이터 픽스처"""
    return {
        "id": "case-test-1",
        "category": "형사",
        "sub_category": "사기",
        "type": "case",
        "title": "대법원 2024도1 판결",
        "content": "판례 내용입니다.",
        "metadata": {
            "court": "대법원",
            "year": 2024,
            "case_number": "2024도1",
            "keywords": ["사기"],
            "holding": "판결 요지",
            "updated_at": "2024-01-01",
        },
    }

