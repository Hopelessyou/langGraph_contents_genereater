# 사용자 가이드

## 시작하기

### 1. 환경 설정

1. `.env.example` 파일을 `.env`로 복사
2. 필요한 환경 변수 설정:
   - `OPENAI_API_KEY`: OpenAI API 키
   - 기타 설정은 `env.example` 참고

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 서버 실행

```bash
python -m src.api.main
```

또는

```bash
uvicorn src.api.main:app --reload
```

서버는 `http://localhost:8000`에서 실행됩니다.

## API 사용 예시

### 검색

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/search",
    json={
        "query": "사기 범죄",
        "n_results": 5,
    }
)

results = response.json()
print(results["results"])
```

### 질의응답

```python
response = requests.post(
    "http://localhost:8000/api/v1/ask",
    json={
        "query": "사기 초범은 집행유예가 가능한가요?",
    }
)

answer = response.json()
print(answer["response"])
```

### 대화 연속성 (세션 사용)

```python
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
        "session_id": session_id,
    }
)
```

## Swagger UI

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 데이터 인덱싱

### 샘플 데이터 인덱싱

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/admin/index",
    headers={"X-API-Key": "your_api_key"},
    json={
        "directory": "./data/samples",
        "pattern": "*.json",
    }
)
```

### 증분 업데이트

```python
response = requests.post(
    "http://localhost:8000/api/v1/admin/index/incremental",
    headers={"X-API-Key": "your_api_key"},
    params={
        "directory": "./data/new_documents",
        "pattern": "*.json",
    }
)
```

