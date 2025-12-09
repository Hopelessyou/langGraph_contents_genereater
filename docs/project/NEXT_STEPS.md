# 다음 작업 가이드

## ✅ 완료된 작업

1. **데이터 처리 및 인덱싱**
   - 판례 데이터: 43개 파일 인덱싱 완료
   - 형법 데이터: 253개 파일 인덱싱 완료
   - 형사소송법 데이터: 328개 파일 인덱싱 완료
   - **총 624개 파일이 벡터 DB에 인덱싱됨**

## 🎯 다음 작업 (우선순위 순)

### 1. API 서버 실행 및 테스트 (가장 중요)

#### 1.1 서버 실행

```bash
# 방법 1: Python 모듈로 실행
python -m src.api.main

# 방법 2: uvicorn으로 실행
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면:
- API 문서: http://localhost:8000/docs
- 헬스체크: http://localhost:8000/api/v1/health

#### 1.2 검색 기능 테스트

**Swagger UI에서 테스트:**
1. 브라우저에서 http://localhost:8000/docs 접속
2. `POST /api/v1/search` 엔드포인트 선택
3. "Try it out" 클릭
4. 다음 예시로 테스트:
   ```json
   {
     "query": "사기죄 처벌",
     "n_results": 5,
     "document_types": ["statute", "case"],
     "category": "형사"
   }
   ```

**Python으로 테스트:**
```python
import requests

# 검색 테스트
response = requests.post(
    "http://localhost:8000/api/v1/search",
    json={
        "query": "사기죄 처벌",
        "n_results": 5,
        "document_types": ["statute", "case"]
    }
)

print(response.json())
```

#### 1.3 질의응답 기능 테스트

```python
import requests

# 질의응답 테스트
response = requests.post(
    "http://localhost:8000/api/v1/ask",
    json={
        "query": "사기 초범은 집행유예가 가능한가요?",
        "n_results": 5
    }
)

print(response.json())
```

### 2. 실패한 파일 오류 수정 (선택사항)

일부 파일에서 metadata 처리 오류가 발생했습니다:
- 형법: 78개 파일 실패
- 형사소송법: 144개 파일 실패

**오류 원인:**
- `'StatuteMetadata' object has no attribute 'get'` 오류
- 일부 파일의 content가 비어있음

**수정 방법:**
```bash
# 실패한 파일 재처리
python scripts/process_and_index.py \
    --input-dir "data/processed/statutes/형법" \
    --doc-type "statute" \
    --collection-name "legal_documents" \
    --skip-process
```

### 3. 추가 데이터 수집 (선택사항)

현재 인덱싱된 데이터:
- 판례: 43개
- 형법: 253개
- 형사소송법: 328개

**추가 수집 가능한 데이터:**
- 특정경제범죄 가중처벌 등에 관한 법률
- 추가 판례 데이터
- 절차 매뉴얼
- FAQ

### 4. 시스템 통합 테스트

#### 4.1 전체 워크플로우 테스트

```python
# 1. 검색
search_response = requests.post(
    "http://localhost:8000/api/v1/search",
    json={"query": "사기죄", "n_results": 5}
)

# 2. 질의응답
ask_response = requests.post(
    "http://localhost:8000/api/v1/ask",
    json={"query": "사기죄 처벌 기준은?"}
)

# 3. 대화 연속성 테스트
session_id = ask_response.json()["session_id"]
follow_up = requests.post(
    "http://localhost:8000/api/v1/ask",
    json={
        "query": "집행유예는?",
        "session_id": session_id
    }
)
```

#### 4.2 성능 테스트

```python
import time

queries = [
    "사기죄 처벌",
    "집행유예 조건",
    "형법 제347조",
    "판례 검색",
    "사건 유형"
]

for query in queries:
    start = time.time()
    response = requests.post(
        "http://localhost:8000/api/v1/search",
        json={"query": query, "n_results": 5}
    )
    elapsed = time.time() - start
    print(f"{query}: {elapsed:.2f}초")
```

### 5. 모니터링 및 최적화

#### 5.1 인덱스 상태 확인

```python
from src.rag import DocumentIndexer

indexer = DocumentIndexer()
status = indexer.get_index_status()
print(status)
```

#### 5.2 검색 품질 평가

- 검색 결과의 관련성 확인
- 답변의 정확성 검증
- 응답 시간 측정

## 📝 체크리스트

- [ ] API 서버 실행
- [ ] 헬스체크 확인
- [ ] 검색 API 테스트
- [ ] 질의응답 API 테스트
- [ ] Swagger UI 확인
- [ ] 실패한 파일 재처리 (선택)
- [ ] 성능 테스트
- [ ] 문서화 업데이트

## 🚀 빠른 시작

가장 빠르게 시작하려면:

```bash
# 1. 서버 실행
python -m src.api.main

# 2. 다른 터미널에서 테스트
python -c "
import requests
response = requests.post(
    'http://localhost:8000/api/v1/search',
    json={'query': '사기죄', 'n_results': 5}
)
print(response.json())
"
```

또는 브라우저에서 http://localhost:8000/docs 접속하여 Swagger UI로 테스트하세요!

