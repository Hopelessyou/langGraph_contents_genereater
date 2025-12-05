# IBS 법률 AI 시스템

법률 정보 RAG(Retrieval-Augmented Generation) 기반 질의응답 시스템

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 목차

- [프로젝트 개요](#프로젝트-개요)
- [주요 기능](#주요-기능)
- [기술 스택](#기술-스택)
- [프로젝트 구조](#프로젝트-구조)
- [시작하기](#시작하기)
- [사용 방법](#사용-방법)
- [API 문서](#api-문서)
- [데이터 모델](#데이터-모델)
- [개발 가이드](#개발-가이드)
- [배포](#배포)
- [테스트](#테스트)
- [기여하기](#기여하기)
- [라이선스](#라이선스)

## 🎯 프로젝트 개요

IBS 법률 AI 시스템은 법령, 판례, 절차 매뉴얼 등 다양한 법률 데이터를 벡터 데이터베이스에 저장하고, RAG(Retrieval-Augmented Generation) 기술을 활용하여 법률 상담 및 정보 제공 서비스를 제공하는 시스템입니다.

### 핵심 특징

- **10가지 법률 문서 타입 지원**: 법령, 판례, 절차 매뉴얼, 실무 매뉴얼, 사건 유형, 템플릿, 양형기준, FAQ, 키워드 맵핑, 스타일 문제
- **하이브리드 검색**: 벡터 검색과 키워드 검색을 결합한 고성능 검색
- **대화형 질의응답**: 멀티 턴 대화 지원 및 컨텍스트 관리
- **실시간 스트리밍**: Server-Sent Events를 통한 실시간 응답 스트리밍
- **자동 분류 및 추천**: 키워드 기반 자동 분류 및 관련 문서 추천
- **스타일 검증**: 법률 용어 정확성 검사 및 문법 검증
- **모니터링 및 로깅**: 구조화된 로깅 및 성능 메트릭 수집

## ✨ 주요 기능

### 1. 데이터 관리
- **자동 검증**: Pydantic 기반 데이터 검증
- **배치 처리**: 대량 데이터 일괄 처리 파이프라인
- **데이터 정제**: 중복 제거 및 품질 검증
- **증분 업데이트**: 변경된 데이터만 효율적으로 업데이트

### 2. 검색 기능
- **벡터 검색**: 의미 기반 유사도 검색
- **키워드 검색**: 전통적인 키워드 매칭
- **하이브리드 검색**: 벡터 + 키워드 결합 검색
- **메타데이터 필터링**: 카테고리, 문서 타입 등으로 필터링
- **결과 재랭킹**: 관련성 기반 결과 정렬

### 3. 질의응답
- **RAG 기반 답변**: 검색된 문서를 기반으로 정확한 답변 생성
- **대화 히스토리**: 이전 대화 참조를 통한 연속성 있는 대화
- **출처 표시**: 답변의 근거가 되는 법령 조문, 판례 번호 등 표시
- **스트리밍 응답**: 실시간으로 답변 생성

### 4. 고급 기능
- **문서 추천**: 관련 문서 자동 추천
- **결과 요약**: 검색 결과 자동 요약
- **자동 분류**: 키워드 기반 자동 카테고리 분류
- **사건 유형 추천**: 관련 사건 유형 추천
- **템플릿 매칭**: 적합한 템플릿 자동 매칭
- **스타일 검증**: 법률 용어 정확성 및 문법 검증

### 5. 모니터링
- **구조화된 로깅**: JSON 형식 로그 저장
- **성능 메트릭**: 검색 성능, LLM 사용량 추적
- **에러 알림**: 임계값 기반 자동 알림
- **API 모니터링**: 요청 수, 응답 시간 등 통계

## 🛠 기술 스택

### 백엔드
- **Python 3.10+**: 메인 프로그래밍 언어
- **FastAPI**: 고성능 웹 프레임워크
- **Pydantic**: 데이터 검증 및 설정 관리
- **LangChain/LangGraph**: RAG 워크플로우 관리
- **ChromaDB**: 벡터 데이터베이스
- **OpenAI API**: 임베딩 및 LLM

### 데이터 처리
- **Pydantic Models**: 타입 안전한 데이터 모델
- **JSON Schema**: 데이터 검증
- **Text Chunking**: 문서 청킹 전략

### 테스트
- **pytest**: 테스트 프레임워크
- **pytest-asyncio**: 비동기 테스트
- **pytest-cov**: 코드 커버리지

### 배포
- **Docker**: 컨테이너화
- **docker-compose**: 다중 컨테이너 관리
- **GitHub Actions**: CI/CD 파이프라인

## 📁 프로젝트 구조

```
ibs_legal_ai_system/
├── src/                          # 소스 코드
│   ├── models/                   # 데이터 모델
│   │   ├── base.py              # BaseDocument 공통 모델
│   │   ├── statute.py           # 법령 모델
│   │   ├── case.py              # 판례 모델
│   │   ├── procedure.py         # 절차 매뉴얼 모델
│   │   ├── template.py          # 템플릿 모델
│   │   ├── manual.py            # 실무 매뉴얼 모델
│   │   ├── case_type.py         # 사건 유형 모델
│   │   ├── sentencing_guideline.py  # 양형기준 모델
│   │   ├── faq.py               # FAQ 모델
│   │   ├── keyword_mapping.py   # 키워드 맵핑 모델
│   │   └── style_issue.py       # 스타일 문제 모델
│   │
│   ├── processors/               # 데이터 처리
│   │   ├── validator.py         # 데이터 검증
│   │   ├── converter.py         # JSON 변환
│   │   ├── cleaner.py           # 데이터 정제
│   │   ├── pipeline.py         # 처리 파이프라인
│   │   ├── quality_checker.py  # 품질 검증
│   │   └── dummy_data_generator.py  # 더미 데이터 생성
│   │
│   ├── collectors/               # 데이터 수집
│   │   ├── statute_collector.py # 법령 수집기
│   │   ├── case_collector.py    # 판례 수집기
│   │   ├── manual_collector.py  # 매뉴얼 수집기
│   │   └── faq_collector.py     # FAQ 수집기
│   │
│   ├── rag/                      # RAG 시스템
│   │   ├── vector_store.py      # 벡터 DB 관리
│   │   ├── embedding.py         # 임베딩 생성
│   │   ├── chunker.py          # 텍스트 청킹
│   │   ├── indexer.py          # 인덱싱
│   │   ├── incremental_updater.py  # 증분 업데이트
│   │   ├── monitor.py           # 인덱싱 모니터링
│   │   ├── workflow.py         # LangGraph 워크플로우
│   │   ├── prompts.py          # 프롬프트 템플릿
│   │   ├── llm_manager.py      # LLM 관리
│   │   ├── retriever.py        # 하이브리드 검색
│   │   ├── session_manager.py # 세션 관리
│   │   ├── error_handler.py    # 에러 핸들링
│   │   ├── source_formatter.py # 출처 포맷팅
│   │   ├── recommender.py      # 문서 추천
│   │   ├── summarizer.py       # 결과 요약
│   │   ├── classifier.py       # 키워드 분류
│   │   ├── style_validator.py  # 스타일 검증
│   │   └── query_logger.py     # 쿼리 로깅
│   │
│   ├── api/                      # API 서버
│   │   ├── main.py              # FastAPI 앱
│   │   ├── auth.py              # 인증
│   │   ├── middleware.py        # 미들웨어
│   │   └── routers/             # 라우터
│   │       ├── health.py        # 헬스체크
│   │       ├── search.py        # 검색 API
│   │       ├── ask.py           # 질의응답 API
│   │       ├── admin.py         # 관리자 API
│   │       └── monitoring.py    # 모니터링 API
│   │
│   └── utils/                    # 유틸리티
│       ├── logging_config.py   # 로깅 설정
│       ├── monitoring.py        # 모니터링
│       ├── error_logger.py      # 에러 로깅
│       └── alert_system.py      # 알림 시스템
│
├── config/                       # 설정
│   └── settings.py              # 애플리케이션 설정
│
├── tests/                        # 테스트
│   ├── test_models.py          # 모델 테스트
│   ├── test_processors.py      # 프로세서 테스트
│   ├── test_rag.py             # RAG 테스트
│   ├── test_api.py             # API 테스트
│   ├── test_integration.py     # 통합 테스트
│   ├── test_performance.py     # 성능 테스트
│   └── conftest.py             # pytest 설정
│
├── data/                         # 데이터
│   ├── samples/                # 샘플 데이터
│   ├── dummy/                   # 더미 데이터
│   ├── collected/               # 수집된 데이터
│   ├── processed/              # 처리된 데이터
│   └── vector_db/               # 벡터 DB 저장소
│
├── docs/                         # 문서
│   ├── api_documentation.md    # API 문서
│   ├── user_guide.md           # 사용자 가이드
│   ├── developer_guide.md      # 개발자 가이드
│   └── data_schema.md          # 데이터 스키마
│
├── scripts/                      # 스크립트
│   ├── collect_data.py         # 데이터 수집
│   ├── run_tests.py            # 테스트 실행
│   ├── deploy.sh               # 배포 스크립트 (Bash)
│   └── deploy.ps1              # 배포 스크립트 (PowerShell)
│
├── .github/workflows/           # CI/CD
│   └── ci.yml                  # GitHub Actions 워크플로우
│
├── Dockerfile                   # Docker 이미지
├── docker-compose.yml           # Docker Compose 설정
├── requirements.txt             # Python 의존성
├── pytest.ini                   # pytest 설정
├── .env.example                 # 환경 변수 예시
├── .gitignore                   # Git 무시 파일
├── 제작_순서_계획서.md          # 제작 계획서
└── README.md                    # 이 파일
```

## 🚀 시작하기

### 필수 요구사항

- **Python 3.10 이상**
- **pip** (Python 패키지 관리자)
- **Docker** (선택사항, 컨테이너 실행 시)
- **OpenAI API 키** (임베딩 및 LLM 사용 시)

### 설치

#### 1. 저장소 클론

```bash
git clone <repository-url>
cd ibs_legal_ai_system
```

#### 2. 가상환경 생성 및 활성화

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. 의존성 설치

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. 환경 변수 설정

`.env.example` 파일을 참고하여 `.env` 파일을 생성:

```bash
cp .env.example .env
```

`.env` 파일을 편집하여 다음 변수들을 설정:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# LLM 설정
LLM_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-large

# 벡터 DB
CHROMA_PERSIST_DIRECTORY=./data/vector_db
CHROMA_COLLECTION_NAME=legal_documents

# API 설정
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# 인증
API_KEY=your_api_key_here

# 로깅
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# 데이터 디렉토리
DATA_DIR=./data
```

### 서버 실행

#### 로컬 실행

```bash
# 방법 1: Python 모듈로 실행
python -m src.api.main

# 방법 2: uvicorn 직접 실행
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면 다음 URL에서 접근 가능:
- **API 서버**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Docker 실행

```bash
# Docker Compose로 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

## 📖 사용 방법

### 1. 데이터 인덱싱

#### 샘플 데이터 인덱싱

```bash
# 샘플 데이터 인덱싱
curl -X POST "http://localhost:8000/api/v1/admin/index" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "./data/samples",
    "pattern": "*.json",
    "chunk": true
  }'
```

#### 데이터 수집 및 인덱싱

```bash
# 방법 1: PDF 파일에서 법령 데이터 자동 변환 (권장)
python scripts/parse_statute_pdf.py "형법(법률)(제20908호)(20250408).pdf"
# → data/collected/statutes/형법/ 폴더에 조문별 JSON 파일 생성

# 방법 2: 데이터 수집 스크립트 사용
python scripts/collect_data.py --type all

# 수집된 데이터 인덱싱 (하위 디렉토리 자동 검색)
curl -X POST "http://localhost:8000/api/v1/admin/index" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "./data/collected/statutes",
    "pattern": "*.json",
    "chunk": true
  }'
```

**참고:** 인덱서는 하위 디렉토리를 재귀적으로 검색하므로, 법률별 폴더 구조를 사용할 수 있습니다:
```
data/collected/statutes/
├── 형법/
│   ├── statute-형법-1.json
│   └── statute-형법-347.json
└── 형사소송법/
    └── statute-형사소송법-250.json
```

### 2. 검색 API 사용

#### Python 예시

```python
import requests

# 검색 요청
response = requests.post(
    "http://localhost:8000/api/v1/search",
    json={
        "query": "사기 범죄의 처벌",
        "n_results": 5,
        "document_types": ["statute", "case"],
        "category": "형사",
        "sub_category": "사기"
    }
)

results = response.json()
print(f"검색 결과: {results['total']}건")
for result in results['results']:
    print(f"- {result['metadata'].get('title', 'N/A')}")
```

#### cURL 예시

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "사기 범죄",
    "n_results": 5
  }'
```

### 3. 질의응답 API 사용

#### Python 예시

```python
import requests

# 질의응답
response = requests.post(
    "http://localhost:8000/api/v1/ask",
    json={
        "query": "사기 초범은 집행유예가 가능한가요?",
        "stream": False
    }
)

answer = response.json()
print(f"질문: {answer['query']}")
print(f"답변: {answer['response']}")
print(f"출처:")
for source in answer['sources']:
    print(f"  - {source['citation']}")
```

#### 대화 연속성 (세션 사용)

```python
import requests

# 첫 번째 질문
response1 = requests.post(
    "http://localhost:8000/api/v1/ask",
    json={"query": "사기 범죄에 대해 알려주세요"}
)
session_id = response1.json()["session_id"]

# 두 번째 질문 (이전 대화 참조)
response2 = requests.post(
    "http://localhost:8000/api/v1/ask",
    json={
        "query": "처벌은 어떻게 되나요?",
        "session_id": session_id
    }
)
```

#### 스트리밍 응답

```python
import requests
import json

response = requests.post(
    "http://localhost:8000/api/v1/ask/stream",
    json={"query": "사기 범죄에 대해 설명해주세요"},
    stream=True
)

for line in response.iter_lines():
    if line:
        data = json.loads(line.decode('utf-8').replace('data: ', ''))
        if 'chunk' in data:
            print(data['chunk'], end='', flush=True)
```

### 4. 관리자 API 사용

#### 인덱스 상태 확인

```bash
curl -X GET "http://localhost:8000/api/v1/admin/index/status" \
  -H "X-API-Key: your_api_key"
```

#### 문서 업로드

```bash
curl -X POST "http://localhost:8000/api/v1/admin/upload" \
  -H "X-API-Key: your_api_key" \
  -F "file=@./data/samples/statute-347.json"
```

## 📚 API 문서

### 주요 엔드포인트

#### 공개 API

- `GET /api/v1/health` - 헬스체크
- `GET /api/v1/health/detailed` - 상세 헬스체크
- `POST /api/v1/search` - 문서 검색
- `GET /api/v1/search` - 문서 검색 (GET)
- `POST /api/v1/ask` - 질의응답
- `POST /api/v1/ask/stream` - 스트리밍 질의응답
- `GET /api/v1/monitoring/stats` - 모니터링 통계

#### 관리자 API (인증 필요)

- `POST /api/v1/admin/index` - 문서 인덱싱
- `POST /api/v1/admin/index/incremental` - 증분 인덱싱
- `GET /api/v1/admin/index/status` - 인덱스 상태
- `POST /api/v1/admin/index/reset` - 인덱스 초기화
- `POST /api/v1/admin/upload` - 문서 업로드
- `GET /api/v1/monitoring/vector-db` - 벡터 DB 상태

자세한 API 문서는 다음을 참고하세요:
- **Swagger UI**: http://localhost:8000/docs
- **API 문서**: [docs/api_documentation.md](./docs/api_documentation.md)

## 📊 데이터 모델

### 지원하는 문서 타입

1. **법령 (statute)**: 법률 조문
2. **판례 (case)**: 법원 판결 요약
3. **절차 매뉴얼 (procedure)**: 법률 절차 안내
4. **실무 매뉴얼 (manual)**: 실무 가이드
5. **사건 유형 (case_type)**: 사건 유형 정의
6. **템플릿 (template)**: 콘텐츠 생성 템플릿
7. **양형기준 (sentencing_guideline)**: 양형 기준 요약
8. **FAQ (faq)**: 자주 묻는 질문
9. **키워드 맵핑 (keyword_mapping)**: 키워드-사건 매핑
10. **스타일 문제 (style_issue)**: 스타일 가이드

### 공통 스키마

모든 문서는 다음 기본 구조를 따릅니다:

```json
{
  "id": "문서 고유 ID",
  "category": "카테고리 (형사, 민사 등)",
  "sub_category": "하위 카테고리 (사기, 계약 등)",
  "type": "문서 타입",
  "title": "문서 제목",
  "content": "문서 내용",
  "metadata": {}
}
```

자세한 스키마는 [docs/data_schema.md](./docs/data_schema.md)를 참고하세요.

## 🔧 개발 가이드

### 개발 환경 설정

```bash
# 개발 의존성 설치
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# 코드 포맷팅
black src/ tests/

# 린팅
flake8 src/ tests/
```

### 테스트 실행

```bash
# 모든 테스트
pytest

# 특정 테스트 파일
pytest tests/test_models.py

# 커버리지 포함
pytest --cov=src --cov-report=html

# 통합 테스트만
pytest -m integration

# 성능 테스트
pytest -m slow
```

### 코드 구조

- **모델**: `src/models/` - Pydantic 데이터 모델
- **프로세서**: `src/processors/` - 데이터 처리 로직
- **RAG**: `src/rag/` - RAG 시스템 핵심 로직
- **API**: `src/api/` - FastAPI 라우터 및 미들웨어
- **유틸리티**: `src/utils/` - 공통 유틸리티

자세한 개발 가이드는 [docs/developer_guide.md](./docs/developer_guide.md)를 참고하세요.

## 🐳 배포

### Docker 배포

#### Docker 이미지 빌드

```bash
docker build -t ibs-legal-ai:latest .
```

#### Docker Compose 실행

```bash
# 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f api

# 서비스 중지
docker-compose down
```

#### 배포 스크립트 사용

**Linux/Mac:**
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

**Windows:**
```powershell
.\scripts\deploy.ps1
```

### 프로덕션 배포

프로덕션 환경에서는 다음을 고려하세요:

1. **환경 변수**: `.env` 파일 대신 환경 변수 또는 시크릿 관리 시스템 사용
2. **HTTPS**: 역방향 프록시(Nginx, Traefik) 사용
3. **로깅**: 중앙화된 로그 관리 시스템 연동
4. **모니터링**: Prometheus, Grafana 등 모니터링 도구 연동
5. **백업**: 벡터 DB 정기 백업

## 📈 모니터링

### 로그 확인

```bash
# 애플리케이션 로그
tail -f logs/app.log

# 쿼리 로그
tail -f data/logs/queries.jsonl

# 에러 로그
tail -f data/logs/errors.jsonl
```

### 모니터링 API

```bash
# 통계 조회
curl http://localhost:8000/api/v1/monitoring/stats

# 벡터 DB 상태
curl -X GET "http://localhost:8000/api/v1/monitoring/vector-db" \
  -H "X-API-Key: your_api_key"
```

## 🤝 기여하기

기여를 환영합니다! 다음 단계를 따르세요:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 코딩 스타일

- **Python**: PEP 8 준수
- **포맷팅**: Black 사용
- **타입 힌트**: 가능한 모든 곳에 타입 힌트 추가
- **문서화**: Docstring 작성

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

## 📞 지원 및 문의

- **이슈 리포트**: [GitHub Issues](https://github.com/your-repo/issues)
- **문서**: [docs/](./docs/) 디렉토리 참고
- **이메일**: support@example.com

## 🙏 감사의 말

이 프로젝트는 다음 오픈소스 프로젝트를 사용합니다:

- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://www.langchain.com/)
- [ChromaDB](https://www.trychroma.com/)
- [Pydantic](https://docs.pydantic.dev/)

## 🔄 프로그램 작동 순서

### 전체 시스템 아키텍처

```
사용자 요청
    ↓
FastAPI 서버
    ↓
라우터 (검색/질의응답)
    ↓
RAG 워크플로우 (LangGraph)
    ↓
┌─────────────────┬─────────────────┐
│  벡터 검색      │  키워드 검색    │
│  (ChromaDB)     │  (메타데이터)   │
└─────────────────┴─────────────────┘
    ↓
결과 재랭킹 및 필터링
    ↓
컨텍스트 구성
    ↓
LLM (OpenAI GPT)
    ↓
응답 생성 및 반환
```

### 1. 시스템 초기화 단계

#### 1.1 애플리케이션 시작

```python
# src/api/main.py
1. FastAPI 앱 생성
2. 미들웨어 등록 (CORS, Rate Limiting, Logging)
3. 라우터 등록 (/search, /ask, /health, /admin)
4. 로깅 시스템 초기화
5. 벡터 DB 연결 (ChromaDB)
6. 임베딩 모델 초기화 (OpenAI)
7. LLM 매니저 초기화
```

**실행 순서:**
```
1. uvicorn 서버 시작
2. on_event("startup") 실행
   - 로깅 설정 (setup_logging)
   - 벡터 DB 연결 확인
   - 임베딩 모델 로드
3. 서버 리스닝 시작 (포트 8000)
```

#### 1.2 데이터 준비 (최초 1회 또는 업데이트 시)

데이터 준비는 법률 문서를 벡터 데이터베이스에 인덱싱하여 검색 가능하게 만드는 과정입니다. 이 과정은 최초 1회 또는 데이터가 업데이트될 때 수행합니다.

**실행 방법:**

```bash
# 방법 1: 데이터 수집 스크립트 실행 (선택사항)
python scripts/collect_data.py --type all

# 방법 2: API를 통한 인덱싱 (권장)
# Swagger UI (http://localhost:8000/docs)에서
# POST /api/v1/admin/index 엔드포인트 사용

# 방법 3: Python 스크립트로 직접 인덱싱
from src.rag import DocumentIndexer
indexer = DocumentIndexer()
results = indexer.index_directory(
    directory=Path("data/samples"),
    pattern="*.json",
    chunk=True
)
```

**API 요청 예시:**

```json
POST /api/v1/admin/index
Headers: {
  "X-API-Key": "your_api_key_here",
  "Content-Type": "application/json"
}
Body: {
  "directory": "data/samples",
  "pattern": "*.json",
  "chunk": true
}
```

**응답 예시:**

```json
{
  "success": true,
  "total": 10,
  "indexed": 9,
  "failed": 1,
  "details": [
    {
      "file": "statute-347.json",
      "status": "success",
      "chunks": 3,
      "document_id": "statute-347"
    },
    {
      "file": "invalid.json",
      "status": "failed",
      "error": "ValidationError: 필수 필드 'id'가 없습니다."
    }
  ]
}
```

---

**상세 처리 순서:**

##### 1단계: JSON 파일 읽기

시스템은 지정된 디렉토리에서 JSON 파일을 재귀적으로 검색합니다.

**읽는 위치:**
- `data/samples/*.json` - 샘플 데이터
- `data/collected/**/*.json` - 수집된 데이터 (모든 하위 디렉토리 포함)
- `data/processed/*.json` - 처리된 데이터

**처리 방식:**
```python
# src/rag/indexer.py
def index_directory(self, directory: Path, pattern: str = "*.json"):
    json_files = list(directory.rglob(pattern))  # 재귀적 검색
    
    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)  # JSON 파싱
            # 다음 단계로 전달
```

**지원하는 파일 형식:**
- 단일 문서 JSON: `{"id": "...", "type": "statute", ...}`
- 문서 배열 JSON: `[{"id": "1", ...}, {"id": "2", ...}]`
- 배치 파일: 여러 문서를 포함하는 큰 JSON 파일

---

##### 2단계: 데이터 검증

Pydantic 모델을 사용하여 데이터의 유효성을 검증합니다.

**검증 항목:**

1. **필수 필드 확인**
   ```python
   # 필수 필드: id, category, sub_category, type, title, content
   if not all([doc.id, doc.category, doc.type, doc.title, doc.content]):
       raise ValidationError("필수 필드가 누락되었습니다.")
   ```

2. **타입 검증**
   ```python
   # Pydantic 모델이 자동으로 타입 검증
   # 예: id는 str, content는 str 또는 list[str]
   document = StatuteModel(**json_data)  # 타입 불일치 시 자동 에러
   ```

3. **문서 타입별 스키마 검증**
   - `statute`: 법령 메타데이터 검증 (law_name, article_number 등)
   - `case`: 판례 메타데이터 검증 (case_number, court 등)
   - `procedure`: 절차 메타데이터 검증
   - 기타 타입별 특화 검증

**검증 실패 시:**
```json
{
  "status": "failed",
  "error": "ValidationError: 'law_name' 필드가 필수입니다.",
  "file": "statute-347.json"
}
```

**검증 성공 시:**
- Pydantic 모델 인스턴스로 변환
- 타입 안전성 보장
- 다음 단계로 전달

---

##### 3단계: 데이터 정제

원본 데이터를 정제하여 품질을 향상시킵니다.

**정제 작업:**

1. **공백 및 특수문자 정리**
   ```python
   # 앞뒤 공백 제거
   text = text.strip()
   
   # 연속된 공백을 하나로
   text = re.sub(r'\s+', ' ', text)
   
   # 제어 문자 제거
   text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
   ```

2. **중복 제거**
   ```python
   # 동일한 ID를 가진 문서 중복 확인
   seen_ids = set()
   if document.id in seen_ids:
       logger.warning(f"중복 문서 발견: {document.id}")
       # 처리 정책: 스킵 또는 업데이트
   seen_ids.add(document.id)
   ```

3. **품질 검사**
   ```python
   # 최소 길이 확인
   if len(document.content) < 10:
       raise ValueError("문서 내용이 너무 짧습니다.")
   
   # 필수 키워드 확인 (선택사항)
   if document.type == "statute" and "조" not in document.title:
       logger.warning(f"법령 형식이 아닐 수 있습니다: {document.title}")
   ```

4. **인코딩 정규화**
   ```python
   # UTF-8로 통일
   text = text.encode('utf-8', errors='ignore').decode('utf-8')
   ```

**정제 후:**
- 깨끗한 텍스트 데이터
- 중복 없는 문서 목록
- 품질 검증 완료된 데이터

---

##### 4단계: 텍스트 청킹

긴 문서를 검색에 적합한 크기로 분할합니다.

**청킹 전략 (문서 타입별):**

1. **법령 (statute) - 조문 단위**
   ```python
   # 조문 번호를 기준으로 분할
   # 예: "제347조", "제348조" 등으로 구분
   chunks = re.split(r'제\d+조', content)
   # 각 조문을 독립적인 청크로 처리
   ```

2. **판례 (case) - 요지 단위**
   ```python
   # 판례의 주요 섹션별로 분할
   # - 사건 개요
   # - 쟁점
   # - 판단
   # - 결론
   sections = ["【사건개요】", "【쟁점】", "【판단】", "【결론】"]
   chunks = split_by_sections(content, sections)
   ```

3. **매뉴얼 (manual) - 섹션 단위**
   ```python
   # 마크다운 헤더나 번호를 기준으로 분할
   # 예: "## 1. 절차", "## 2. 주의사항"
   chunks = split_by_headers(content)
   ```

4. **기타 타입 - 고정 크기 청킹**
   ```python
   # 기본 청킹 전략: 고정 크기 + 오버랩
   chunk_size = 1000  # 토큰 수
   chunk_overlap = 200  # 겹치는 부분
   
   # 텍스트를 1000 토큰씩 분할하되, 200 토큰씩 겹치게
   chunks = sliding_window_chunk(text, chunk_size, chunk_overlap)
   ```

**청킹 결과:**
```python
[
  {
    "text": "형법 제347조(사기) ① 사람을 기망하여...",
    "metadata": {
      "chunk_index": 0,
      "document_id": "statute-347",
      "document_type": "statute",
      "chunk_type": "article",
      "article_number": "347"
    }
  },
  {
    "text": "형법 제348조(컴퓨터등사용사기)...",
    "metadata": {
      "chunk_index": 1,
      "document_id": "statute-347",
      "document_type": "statute",
      "chunk_type": "article",
      "article_number": "348"
    }
  }
]
```

**청킹 파라미터:**
- `chunk_size`: 기본 1000 토큰 (설정 가능)
- `chunk_overlap`: 기본 200 토큰 (문맥 유지)
- `min_chunk_size`: 최소 100 토큰 (너무 작은 청크 방지)

---

##### 5단계: 임베딩 생성

텍스트를 벡터로 변환하여 의미적 유사도를 계산할 수 있게 합니다.

**임베딩 생성 과정:**

1. **OpenAI Embedding API 호출**
   ```python
   # src/rag/embedding.py
   def embed_texts(self, texts: List[str]) -> List[List[float]]:
       # 배치 처리로 효율성 향상
       response = openai.embeddings.create(
           model=self.model,  # "text-embedding-3-large"
           input=texts,  # 여러 텍스트를 한 번에 처리
       )
       return [item.embedding for item in response.data]
   ```

2. **벡터 변환**
   ```python
   # 텍스트 → 벡터 (1536차원 또는 3072차원)
   text = "형법 제347조(사기)..."
   embedding = [0.123, -0.456, 0.789, ...]  # 1536개 숫자 배열
   ```

3. **배치 처리 최적화**
   ```python
   # 한 번에 최대 100개 텍스트 처리 (API 제한)
   batch_size = 100
   for i in range(0, len(texts), batch_size):
       batch = texts[i:i+batch_size]
       embeddings = self.embed_texts(batch)
       # 결과 저장
   ```

**임베딩 모델:**
- 기본: `text-embedding-3-large` (3072차원, 높은 정확도)
- 대안: `text-embedding-3-small` (1536차원, 빠른 속도)
- 설정: `env.example`의 `EMBEDDING_MODEL`로 변경 가능

**임베딩 결과:**
```python
{
  "text": "형법 제347조(사기)...",
  "embedding": [0.123, -0.456, 0.789, ..., 0.234],  # 3072차원 벡터
  "model": "text-embedding-3-large",
  "dimensions": 3072
}
```

---

##### 6단계: 벡터 DB 저장

생성된 임베딩과 메타데이터를 ChromaDB에 저장합니다.

**저장 과정:**

1. **ChromaDB 컬렉션 확인/생성**
   ```python
   # src/rag/vector_store.py
   collection = chroma_client.get_or_create_collection(
       name="legal_documents",
       metadata={"description": "법률 문서 벡터 저장소"}
   )
   ```

2. **벡터 및 메타데이터 저장**
   ```python
   # 각 청크를 개별 문서로 저장
   collection.add(
       ids=[f"{doc_id}_chunk_{i}" for i in range(len(chunks))],
       embeddings=[chunk["embedding"] for chunk in chunks],
       documents=[chunk["text"] for chunk in chunks],
       metadatas=[chunk["metadata"] for chunk in chunks]
   )
   ```

3. **저장되는 메타데이터:**
   ```python
   {
       "document_id": "statute-347",
       "document_type": "statute",
       "category": "형사",
       "sub_category": "사기",
       "chunk_index": 0,
       "chunk_type": "article",
       "article_number": "347",
       "law_name": "형법",
       "title": "형법 제347조(사기)"
   }
   ```

4. **인덱스 업데이트**
   ```python
   # ChromaDB가 자동으로 인덱스 업데이트
   # HNSW (Hierarchical Navigable Small World) 알고리즘 사용
   # 빠른 유사도 검색을 위한 인덱스 구조 생성
   ```

**저장 결과:**
```python
{
  "document_id": "statute-347",
  "chunks_count": 3,
  "status": "success",
  "vector_ids": [
    "statute-347_chunk_0",
    "statute-347_chunk_1",
    "statute-347_chunk_2"
  ]
}
```

**저장 위치:**
- 로컬 파일 시스템: `./data/vector_db/` (기본값)
- 설정: `env.example`의 `CHROMA_PERSIST_DIRECTORY`로 변경 가능

---

**전체 처리 흐름 다이어그램:**

```
JSON 파일
    ↓
[1] 파일 읽기 → JSON 파싱
    ↓
[2] 데이터 검증 → Pydantic 모델 변환
    ↓
[3] 데이터 정제 → 정제된 문서
    ↓
[4] 텍스트 청킹 → 청크 배열
    ↓
[5] 임베딩 생성 → 벡터 배열
    ↓
[6] 벡터 DB 저장 → 인덱싱 완료
    ↓
검색 가능한 상태
```

**처리 시간 예시:**
- 소규모 (10개 문서): 약 1-2분
- 중규모 (100개 문서): 약 10-15분
- 대규모 (1000개 문서): 약 1-2시간

**모니터링:**
```bash
# 인덱스 상태 확인
GET /api/v1/admin/index/status

# 응답
{
  "collection_name": "legal_documents",
  "document_count": 150,
  "indexed_documents": 150,
  "health_status": {
    "status": "healthy",
    "total_chunks": 450
  }
}
```

### 2. 검색 API 작동 순서

#### 2.1 요청 수신

```
사용자 → POST /api/v1/search
{
  "query": "사기 범죄",
  "n_results": 5,
  "document_types": ["statute", "case"]
}
```

#### 2.2 요청 처리 흐름

```
1. 미들웨어 처리
   ├─ LoggingMiddleware: 요청 로깅
   ├─ RateLimitMiddleware: 요청 제한 확인
   └─ CORS: CORS 헤더 추가

2. 라우터 (search.py)
   ├─ 요청 검증 (Pydantic)
   ├─ 서비스 인스턴스 가져오기
   │  ├─ VectorStore
   │  ├─ EmbeddingGenerator
   │  └─ HybridRetriever
   └─ 검색 실행

3. 하이브리드 검색 (HybridRetriever)
   ├─ 쿼리 임베딩 생성
   │  └─ OpenAI Embedding API
   │
   ├─ 벡터 검색
   │  ├─ ChromaDB similarity_search
   │  ├─ n_results * 2 검색 (재랭킹을 위해)
   │  └─ 거리 계산
   │
   ├─ 키워드 검색 (선택적)
   │  ├─ 메타데이터 필터링
   │  └─ 키워드 매칭
   │
   └─ 결과 병합 및 재랭킹
      ├─ 벡터 점수 정규화
      ├─ 키워드 점수 계산
      ├─ 가중 평균 계산
      └─ 상위 n_results 선택

4. 결과 포맷팅
   ├─ 출처 정보 추가 (SourceFormatter)
   ├─ 메타데이터 정리
   └─ 응답 생성

5. 응답 반환
   {
     "query": "사기 범죄",
     "results": [...],
     "total": 5,
     "timestamp": "..."
   }

6. 로깅
   ├─ 쿼리 로깅 (QueryLogger)
   ├─ 성능 메트릭 기록
   └─ API 모니터링 업데이트
```

#### 2.3 상세 처리 단계

**Step 1: 쿼리 분석**
```python
# src/rag/retriever.py
query = "사기 범죄"
query_embedding = embedding_generator.embed_text(query)
# → [0.123, -0.456, 0.789, ...] (1536차원 벡터)
```

**Step 2: 벡터 검색**
```python
# src/rag/vector_store.py
results = vector_store.search(
    query_embedding=query_embedding,
    n_results=10,  # 재랭킹을 위해 2배 검색
    where={"type": {"$in": ["statute", "case"]}}
)
# → 유사도 점수와 함께 문서 반환
```

**Step 3: 메타데이터 필터링**
```python
# src/rag/retriever.py
filtered_results = filter_by_metadata(
    results,
    document_types=["statute", "case"],
    category="형사"
)
```

**Step 4: 재랭킹**
```python
# src/rag/retriever.py
reranked = rerank_results(
    vector_results=filtered_results,
    query=query,
    weights={"vector": 0.7, "keyword": 0.3}
)
# → 최종 상위 5개 선택
```

### 3. 질의응답 API 작동 순서

#### 3.1 요청 수신

```
사용자 → POST /api/v1/ask
{
  "query": "사기 초범은 집행유예가 가능한가요?",
  "session_id": "optional-session-id",
  "stream": false
}
```

#### 3.2 RAG 워크플로우 (LangGraph)

```
1. 세션 관리
   ├─ 세션 ID 확인
   ├─ 기존 세션 로드 또는 새 세션 생성
   └─ 대화 히스토리 가져오기 (최근 3턴)

2. 쿼리 분석 노드
   ├─ 키워드 추출
   ├─ 카테고리 분류 (KeywordClassifier)
   ├─ 문서 타입 추론
   └─ 의도 분석

3. 검색 노드
   ├─ 벡터 검색 실행
   ├─ 키워드 검색 실행
   ├─ 결과 병합
   └─ 상위 5개 문서 선택

4. 메타데이터 필터링 노드
   ├─ 카테고리 필터
   ├─ 문서 타입 필터
   └─ 관련성 점수 계산

5. 재랭킹 노드
   ├─ 관련성 재계산
   ├─ 출처 신뢰도 확인
   └─ 최종 순위 결정

6. 컨텍스트 구성 노드
   ├─ 검색 결과 텍스트 추출
   ├─ 이전 대화 컨텍스트 추가
   ├─ 프롬프트 템플릿 적용
   └─ 컨텍스트 윈도우 최적화

7. LLM 호출 노드
   ├─ 프롬프트 구성
   │  ├─ 시스템 프롬프트
   │  ├─ 컨텍스트 (검색된 문서)
   │  ├─ 대화 히스토리
   │  └─ 사용자 쿼리
   │
   ├─ OpenAI API 호출
   │  ├─ GPT-4 모델 사용
   │  ├─ 스트리밍 또는 일반 모드
   │  └─ 토큰 사용량 추적
   │
   └─ 응답 생성

8. 후처리 노드
   ├─ 출처 정보 추출 (SourceFormatter)
   ├─ 스타일 검증 (StyleValidator)
   ├─ 법률 용어 검사 (LegalTermChecker)
   └─ 응답 포맷팅

9. 세션 업데이트
   ├─ 사용자 메시지 추가
   ├─ 어시스턴트 응답 추가
   └─ 세션 저장

10. 응답 반환
    {
      "query": "...",
      "response": "...",
      "session_id": "...",
      "sources": [...],
      "timestamp": "..."
    }
```

#### 3.3 프롬프트 구성 예시

```python
# src/rag/prompts.py
system_prompt = """
당신은 법률 전문가입니다. 다음 문서를 참고하여 정확하고 명확한 답변을 제공하세요.
"""

context = """
[법령] 형법 제347조(사기)
① 사람을 기망하여 재물의 교부를 받거나 재산상의 이익을 취득한 자는 
10년 이하의 징역 또는 2천만원 이하의 벌금에 처한다.

[판례] 대법원 2023도11234
초범이라도 피해 규모가 크면 실형이 선고될 수 있다.
"""

user_query = "사기 초범은 집행유예가 가능한가요?"

final_prompt = f"""
{system_prompt}

관련 문서:
{context}

이전 대화:
{history}

질문: {user_query}

답변:
"""
```

### 4. 스트리밍 응답 처리

#### 4.1 스트리밍 요청

```
POST /api/v1/ask/stream
{
  "query": "...",
  "stream": true
}
```

#### 4.2 스트리밍 처리 흐름

```
1. 일반 검색 워크플로우 실행
   └─ 컨텍스트 구성까지 동일

2. LLM 스트리밍 호출
   ├─ OpenAI API (stream=True)
   ├─ Server-Sent Events (SSE) 형식
   └─ 청크 단위로 응답 수신

3. 실시간 전송
   ├─ 각 토큰/청크 수신 시 즉시 전송
   ├─ "data: {chunk}\n\n" 형식
   └─ 클라이언트에서 실시간 표시

4. 완료 신호
   └─ "data: {"done": true}\n\n"
```

### 5. 증분 업데이트 작동 순서

#### 5.1 증분 인덱싱 요청

```
POST /api/v1/admin/index/incremental
{
  "directory": "./data/new_documents",
  "pattern": "*.json"
}
```

#### 5.2 처리 순서

```
1. 디렉토리 스캔
   ├─ 파일 목록 수집
   └─ 수정 시간 확인

2. 변경 감지
   ├─ 기존 인덱스와 비교
   ├─ 새 파일 식별
   ├─ 수정된 파일 식별
   └─ 삭제된 파일 식별

3. 선택적 처리
   ├─ 새 파일만 인덱싱
   ├─ 수정된 파일만 재인덱싱
   └─ 삭제된 파일 제거

4. 배치 처리
   ├─ 여러 파일 병렬 처리
   ├─ 임베딩 생성 (배치)
   └─ 벡터 DB 업데이트

5. 상태 업데이트
   ├─ 인덱싱 상태 저장
   └─ 타임스탬프 업데이트
```

### 6. 에러 처리 및 재시도

#### 6.1 에러 처리 흐름

```
1. 에러 발생
   ├─ API 호출 실패 (OpenAI)
   ├─ 벡터 DB 오류
   └─ 검증 오류

2. 에러 로깅
   ├─ ErrorLogger.log_error()
   ├─ JSON 형식으로 저장
   └─ 심각도 분류

3. 재시도 로직
   ├─ 일시적 오류: 자동 재시도 (최대 3회)
   ├─ 지수 백오프 (1초, 2초, 4초)
   └─ 영구적 오류: 즉시 실패

4. 사용자 응답
   ├─ 친화적인 에러 메시지
   ├─ 에러 코드 반환
   └─ 로그 ID 제공 (디버깅용)
```

### 7. 모니터링 및 로깅

#### 7.1 실시간 모니터링

```
1. 요청 수신 시
   ├─ LoggingMiddleware: 요청 로깅
   └─ APIMonitor: 요청 카운트 증가

2. 처리 중
   ├─ 성능 메트릭 수집
   │  ├─ 응답 시간 측정
   │  ├─ 토큰 사용량 추적
   │  └─ 벡터 DB 쿼리 시간
   │
   └─ QueryLogger: 쿼리 로깅

3. 응답 전송 시
   ├─ 응답 시간 기록
   ├─ 상태 코드 기록
   └─ 모니터링 통계 업데이트

4. 주기적 체크
   ├─ 벡터 DB 상태 확인
   ├─ 임계값 확인
   └─ 알림 전송 (필요 시)
```

### 8. 전체 요청-응답 사이클

```
[사용자 요청]
    ↓
[FastAPI 서버]
    ├─ 미들웨어 처리 (로깅, Rate Limiting)
    ├─ 라우터 라우팅
    └─ 요청 검증
    ↓
[RAG 워크플로우]
    ├─ 세션 관리
    ├─ 쿼리 분석
    ├─ 벡터 검색
    ├─ 결과 재랭킹
    ├─ 컨텍스트 구성
    ├─ LLM 호출
    └─ 후처리
    ↓
[응답 생성]
    ├─ 출처 정보 추가
    ├─ 스타일 검증
    └─ 포맷팅
    ↓
[로깅 및 모니터링]
    ├─ 쿼리 로깅
    ├─ 성능 메트릭 기록
    └─ 통계 업데이트
    ↓
[사용자 응답]
```

### 9. 성능 최적화 포인트

1. **캐싱**: 자주 검색되는 쿼리 결과 캐싱
2. **배치 처리**: 여러 임베딩을 한 번에 생성
3. **비동기 처리**: I/O 작업 비동기 처리
4. **연결 풀링**: 벡터 DB 연결 재사용
5. **인덱스 최적화**: 벡터 DB 인덱스 튜닝

### 10. 데이터 흐름도

```
[원본 데이터]
    ↓
[수집기] → JSON 파일
    ↓
[검증기] → 검증된 데이터
    ↓
[정제기] → 정제된 데이터
    ↓
[청킹] → 텍스트 청크
    ↓
[임베딩] → 벡터
    ↓
[벡터 DB] → 인덱싱 완료
    ↓
[검색] → 관련 문서 검색
    ↓
[LLM] → 답변 생성
    ↓
[사용자] → 최종 응답
```

## 📚 참고 자료

- [제작 순서 계획서](./제작_순서_계획서.md)
- [사용자 가이드](./docs/user_guide.md)
- [개발자 가이드](./docs/developer_guide.md)
- [데이터 스키마](./docs/data_schema.md)
- [API 문서](./docs/api_documentation.md)

---

**IBS 법률 AI 시스템** - 법률 정보 RAG 기반 질의응답 시스템
