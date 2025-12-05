# 개발자 가이드

## 프로젝트 구조

```
ibs_legal_ai_system/
├── src/
│   ├── models/          # 데이터 모델
│   ├── processors/      # 데이터 처리
│   ├── rag/            # RAG 시스템
│   ├── api/            # API 서버
│   └── utils/          # 유틸리티
├── config/             # 설정
├── tests/              # 테스트
├── data/               # 데이터
└── docs/               # 문서
```

## 개발 환경 설정

### 1. 가상환경 생성

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env` 파일 생성 및 설정 (`.env.example` 참고)

## 코드 구조

### 데이터 모델

모든 법률 문서는 `BaseDocument`를 상속받습니다:

```python
from src.models import StatuteModel

statute = StatuteModel(
    id="statute-1",
    category="형사",
    sub_category="사기",
    type="statute",
    title="형법 제347조",
    content="조문 내용",
    metadata={...}
)
```

### RAG 시스템 사용

```python
from src.rag import (
    VectorStore,
    EmbeddingGenerator,
    HybridRetriever,
    LLMManager,
)

# 초기화
vector_store = VectorStore()
embedding_gen = EmbeddingGenerator()
retriever = HybridRetriever(vector_store, embedding_gen)
llm_manager = LLMManager()

# 검색
results = retriever.search("사기", n_results=5)

# 질의응답
context = results["context"]
response = llm_manager.generate_response(context, "사기 범죄는?")
```

### 데이터 처리

```python
from src.processors import (
    DocumentValidator,
    BatchProcessor,
    QualityChecker,
)

# 검증
validator = DocumentValidator()
success, model = validator.validate(data)

# 배치 처리
processor = BatchProcessor()
results = processor.process_directory(
    input_dir="./data/raw",
    output_dir="./data/processed",
    doc_type="statute",
)

# 품질 검사
checker = QualityChecker()
quality = checker.check_quality(data)
```

## 테스트 실행

```bash
# 모든 테스트
pytest

# 특정 테스트 파일
pytest tests/test_models.py

# 통합 테스트만
pytest -m integration

# 성능 테스트
pytest -m slow
```

## 로깅

로깅은 자동으로 설정됩니다:

- 콘솔: INFO 레벨 이상
- 파일: JSON 형식, `./logs/app.log`

```python
import logging

logger = logging.getLogger(__name__)
logger.info("정보 메시지")
logger.error("에러 메시지")
```

## 모니터링

모니터링 API를 통해 시스템 상태를 확인할 수 있습니다:

```python
import requests

# 통계 조회
response = requests.get("http://localhost:8000/api/v1/monitoring/stats")
stats = response.json()
```

## 확장 가이드

### 새로운 데이터 타입 추가

1. `src/models/`에 새 모델 추가
2. `BaseDocument`의 `type` Literal에 추가
3. `DocumentValidator`에 모델 매핑 추가
4. 필요시 청킹 전략 추가

### 새로운 API 엔드포인트 추가

1. `src/api/routers/`에 새 라우터 파일 생성
2. `src/api/main.py`에 라우터 등록

## 배포

### Docker 사용 (예정)

```bash
docker build -t ibs-legal-ai .
docker run -p 8000:8000 ibs-legal-ai
```

### 환경 변수

프로덕션 환경에서는 다음을 설정하세요:

- `OPENAI_API_KEY`: 필수
- `API_KEY`: 관리자 API 인증용
- `LOG_LEVEL`: `INFO` 또는 `WARNING`
- `CHROMA_PERSIST_DIRECTORY`: 벡터 DB 저장 경로

