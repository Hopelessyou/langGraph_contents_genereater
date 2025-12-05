# IBS 법률 AI 시스템 사용 가이드

## 🚀 빠른 시작

### 1. 서버 실행

```bash
# 프로젝트 디렉토리로 이동
cd gpt_langraph/ibs_legal_ai_system

# 서버 실행
python -m src.api.main
```

서버가 `http://localhost:8000`에서 실행됩니다.

---

## 📖 API 문서 (Swagger UI)

가장 쉬운 방법은 **브라우저에서 API 문서를 확인**하는 것입니다:

```
http://localhost:8000/docs
```

이 페이지에서:
- ✅ 모든 API 엔드포인트 확인
- ✅ 직접 테스트 가능
- ✅ 요청/응답 형식 확인
- ✅ 예제 코드 생성

---

## 🔍 주요 API 엔드포인트

### 1. 헬스체크

**기본 헬스체크**
```bash
# 브라우저에서 접속
http://localhost:8000/api/v1/health

# 또는 PowerShell에서
curl http://localhost:8000/api/v1/health

# 또는 Python에서
import requests
response = requests.get("http://localhost:8000/api/v1/health")
print(response.json())
```

**응답 예시:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-12-05T11:08:58.398388"
}
```

**상세 헬스체크**
```bash
http://localhost:8000/api/v1/health/detailed
```

---

### 2. 문서 검색 API

법률 문서를 검색합니다.

**엔드포인트:** `POST /api/v1/search`

**요청 예시 (PowerShell):**
```powershell
$body = @{
    query = "사기죄 처벌"
    n_results = 5
    document_types = @("statute", "case")
    category = "형사"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/search" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

**요청 예시 (Python):**
```python
import requests

url = "http://localhost:8000/api/v1/search"
data = {
    "query": "사기죄 처벌",
    "n_results": 5,
    "document_types": ["statute", "case"],
    "category": "형사"
}

response = requests.post(url, json=data)
print(response.json())
```

**요청 예시 (curl):**
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "사기죄 처벌",
    "n_results": 5,
    "document_types": ["statute", "case"],
    "category": "형사"
  }'
```

**요청 파라미터:**
- `query` (필수): 검색할 질문 또는 키워드
- `n_results` (선택): 반환할 결과 수 (기본값: 5, 최대: 20)
- `document_types` (선택): 문서 타입 필터
  - 가능한 값: `statute`, `case`, `procedure`, `manual`, `template` 등
- `category` (선택): 카테고리 필터 (예: "형사", "민사")
- `sub_category` (선택): 하위 카테고리 필터

**응답 예시:**
```json
{
  "query": "사기죄 처벌",
  "results": [
    {
      "id": "statute-347",
      "document": "형법 제347조(사기)...",
      "metadata": {
        "law_name": "형법",
        "article_number": "347",
        "category": "형사",
        "sub_category": "사기"
      },
      "score": 0.95
    }
  ],
  "total": 1,
  "timestamp": "2025-12-05T11:10:00"
}
```

---

### 3. 질의응답 API

법률 질문에 대한 답변을 생성합니다.

**엔드포인트:** `POST /api/v1/ask`

**요청 예시 (Python):**
```python
import requests

url = "http://localhost:8000/api/v1/ask"
data = {
    "query": "사기죄는 어떤 처벌을 받나요?",
    "session_id": "user-123",  # 선택사항: 대화 연속성 유지
    "stream": False,  # True로 설정하면 스트리밍 응답
    "document_types": ["statute", "case"]
}

response = requests.post(url, json=data)
result = response.json()
print(result["answer"])
print(result["sources"])  # 참조한 문서들
```

**스트리밍 응답 (Python):**
```python
import requests
import json

url = "http://localhost:8000/api/v1/ask"
data = {
    "query": "사기죄는 어떤 처벌을 받나요?",
    "stream": True
}

response = requests.post(url, json=data, stream=True)

for line in response.iter_lines():
    if line:
        chunk = json.loads(line)
        print(chunk.get("content", ""), end="", flush=True)
```

**요청 파라미터:**
- `query` (필수): 질문 내용
- `session_id` (선택): 세션 ID (대화 히스토리 유지)
- `stream` (선택): 스트리밍 응답 여부 (기본값: false)
- `document_types` (선택): 검색할 문서 타입 필터

**응답 예시:**
```json
{
  "answer": "사기죄는 형법 제347조에 따라 10년 이하의 징역 또는 2천만원 이하의 벌금에 처해집니다...",
  "sources": [
    {
      "id": "statute-347",
      "title": "형법 제347조(사기)",
      "type": "statute"
    }
  ],
  "session_id": "user-123",
  "timestamp": "2025-12-05T11:10:00"
}
```

---

### 4. 관리자 API

**문서 업로드 및 인덱싱**
```bash
# API 키 필요 (환경 변수에서 설정)
curl -X POST "http://localhost:8000/api/v1/admin/upload" \
  -H "X-API-Key: your_api_key" \
  -F "file=@data/samples/statute-347.json"
```

**인덱스 재구성**
```bash
curl -X POST "http://localhost:8000/api/v1/admin/reindex" \
  -H "X-API-Key: your_api_key"
```

---

## 🧪 테스트 예제

### Python 스크립트 예제

`test_api.py` 파일 생성:

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 1. 헬스체크
print("=== 헬스체크 ===")
response = requests.get(f"{BASE_URL}/health")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# 2. 문서 검색
print("\n=== 문서 검색 ===")
search_data = {
    "query": "사기죄",
    "n_results": 3
}
response = requests.post(f"{BASE_URL}/search", json=search_data)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# 3. 질의응답
print("\n=== 질의응답 ===")
ask_data = {
    "query": "사기죄는 무엇인가요?",
    "stream": False
}
response = requests.post(f"{BASE_URL}/ask", json=ask_data)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

실행:
```bash
python test_api.py
```

---

## 📝 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-large
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 🔐 API 인증

일부 관리자 엔드포인트는 API 키가 필요합니다.

요청 헤더에 추가:
```
X-API-Key: your_api_key_here
```

---

## 📚 추가 리소스

- **API 문서**: http://localhost:8000/docs
- **ReDoc 문서**: http://localhost:8000/redoc
- **프로젝트 README**: `README.md` 참조

---

## ❓ 문제 해결

### 서버가 시작되지 않을 때
1. 포트 8000이 사용 중인지 확인
2. `.env` 파일이 올바르게 설정되었는지 확인
3. 필요한 패키지가 설치되었는지 확인: `pip install -r requirements.txt`

### API 요청이 실패할 때
1. 서버가 실행 중인지 확인
2. 요청 형식이 올바른지 확인 (Swagger UI에서 테스트)
3. 로그 파일 확인: `logs/app.log`

---

## 💡 팁

1. **Swagger UI 활용**: 가장 쉬운 테스트 방법입니다
2. **세션 ID 사용**: 연속된 대화를 위해 `session_id`를 유지하세요
3. **스트리밍 사용**: 긴 응답의 경우 `stream: true`로 설정하면 실시간으로 받을 수 있습니다
4. **필터 활용**: `document_types`, `category` 등을 사용하여 검색 범위를 좁히세요

