"""pytest 설정 및 픽스처"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """임시 디렉토리 픽스처"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


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

