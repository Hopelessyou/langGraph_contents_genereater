# RAG 용 파일 저장 방법 가이드

## 📋 전체 프로세스 요약

```
1. PDF 파일 준비 (어디든 상관없음)
   ↓
2. PDF → JSON 변환 (스크립트 실행)
   ↓
3. JSON 파일 저장 (자동 저장됨)
   ↓
4. 벡터 DB 인덱싱 (API 또는 스크립트)
   ↓
5. 검색 가능한 상태 ✅
```

---

## 🚀 단계별 가이드

### 1단계: PDF 파일 준비

**PDF 파일 위치**: 어디든 상관없습니다 (절대 경로 또는 상대 경로)

**권장 구조**:
```
ibs_legal_ai_system/
├── data/
│   └── pdfs/              ← PDF 파일 저장 (선택사항)
│       ├── cases/         ← 판례 PDF
│       └── statutes/      ← 법령 PDF
```

**PDF 파일 요구사항**:
- ✅ 텍스트 추출 가능한 PDF (텍스트 기반)
- ❌ 스캔본 이미지 PDF (OCR 필요)
- ✅ 파일명에 사건번호 포함 권장 (예: `판례_2023도11234.pdf`)

---

### 2단계: PDF → JSON 변환

#### 판례 PDF 변환

```bash
# 단일 파일 변환
python scripts/parse_case_pdf.py "판례_2023도11234.pdf"

# 폴더 내 모든 PDF 변환
python scripts/parse_case_pdf.py "data/pdfs/cases/" --folder

# 출력 디렉토리 지정
python scripts/parse_case_pdf.py "판례.pdf" --output-dir data/collected/cases
```

**자동 추출 정보**:
- 사건번호
- 법원명
- 판결일
- 판시사항
- 참조조문
- 참조판례
- 판결 요지
- 사건 개요
- 쟁점
- 판단

#### 법령 PDF 변환

```bash
# 단일 파일 변환 (조문별로 자동 분리)
python scripts/parse_statute_pdf.py "형법(법률)(제20908호)(20250408).pdf"

# 출력 디렉토리 지정
python scripts/parse_statute_pdf.py "형법.pdf" --output-dir data/collected/statutes

# 개정일 지정
python scripts/parse_statute_pdf.py "형법.pdf" --updated-at "2025-04-08"
```

**자동 생성 구조**:
```
data/collected/statutes/
└── 형법/
    ├── statute-형법-1.json
    ├── statute-형법-2.json
    ├── statute-형법-347.json
    └── ...
```

---

### 3단계: JSON 파일 저장 위치 확인

변환된 JSON 파일은 자동으로 다음 위치에 저장됩니다:

#### 판례 JSON
```
data/collected/cases/
├── case-2023도11234.json
├── case-2023노856.json
└── case-2012노856.json
```

#### 법령 JSON
```
data/collected/statutes/
├── 형법/
│   ├── statute-형법-1.json
│   └── statute-형법-347.json
└── 형사소송법/
    └── statute-형사소송법-250.json
```

**중요**: 인덱서는 하위 디렉토리를 재귀적으로 검색하므로, 법률별 폴더 구조를 사용할 수 있습니다.

---

### 4단계: 벡터 DB 인덱싱

#### 방법 1: API 사용 (권장)

**Swagger UI 사용**:
1. `http://localhost:8000/docs` 접속
2. `POST /api/v1/admin/index` 선택
3. "Try it out" 클릭
4. 요청 본문 입력:
   ```json
   {
     "directory": "data/collected/cases",
     "pattern": "*.json",
     "chunk": true
   }
   ```
5. Headers에 `X-API-Key: your_api_key` 추가
6. "Execute" 클릭

**cURL 사용**:
```bash
curl -X POST "http://localhost:8000/api/v1/admin/index" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "data/collected/cases",
    "pattern": "*.json",
    "chunk": true
  }'
```

**Python requests 사용**:
```python
import requests

url = "http://localhost:8000/api/v1/admin/index"
headers = {
    "X-API-Key": "your_api_key",
    "Content-Type": "application/json"
}
data = {
    "directory": "data/collected/cases",
    "pattern": "*.json",
    "chunk": True
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

#### 방법 2: Python 스크립트 사용

```python
from pathlib import Path
from src.rag import DocumentIndexer

# 인덱서 생성
indexer = DocumentIndexer()

# 디렉토리 내 모든 JSON 파일 인덱싱 (하위 디렉토리 포함)
results = indexer.index_directory(
    directory=Path("data/collected/cases"),
    pattern="*.json",
    chunk=True,  # 청킹 사용
    recursive=True  # 하위 디렉토리 재귀 검색 (기본값: True)
)

print(f"총 {results['total']}건 중 {results['success']}건 성공")
print(f"실패: {results['failed']}건")
```

#### 방법 3: 단일 파일 업로드

**Swagger UI 사용**:
1. `POST /api/v1/admin/upload` 선택
2. "Try it out" 클릭
3. "Choose File" 버튼으로 JSON 파일 선택
4. Headers에 `X-API-Key: your_api_key` 추가
5. "Execute" 클릭

**Python requests 사용**:
```python
import requests

url = "http://localhost:8000/api/v1/admin/upload"
headers = {"X-API-Key": "your_api_key"}

with open("data/collected/cases/case-2023도11234.json", "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files, headers=headers)
    print(response.json())
```

---

### 5단계: 인덱싱 확인

#### 인덱스 상태 확인

**API 사용**:
```bash
curl http://localhost:8000/api/v1/admin/index/status
```

**응답 예시**:
```json
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

#### 검색 테스트

```python
import requests

# 검색 테스트
response = requests.post(
    "http://localhost:8000/api/v1/search",
    json={
        "query": "사기죄",
        "n_results": 5
    }
)

print(response.json())
```

---

## 📝 실전 예제

### 예제 1: 판례 PDF 전체 프로세스

```bash
# 1. PDF 파일 준비 (어디든 상관없음)
# 예: C:\Users\1gmla\Documents\판례_2023도11234.pdf

# 2. PDF → JSON 변환
python scripts/parse_case_pdf.py "C:\Users\1gmla\Documents\판례_2023도11234.pdf"
# → data/collected/cases/case-2023도11234.json 생성

# 3. 벡터 DB 인덱싱
curl -X POST "http://localhost:8000/api/v1/admin/index" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "data/collected/cases",
    "pattern": "*.json",
    "chunk": true
  }'

# 4. 검색 테스트
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "사기 초범 집행유예",
    "n_results": 5
  }'
```

### 예제 2: 법령 PDF 전체 프로세스

```bash
# 1. PDF 파일 준비
# 예: 형법(법률)(제20908호)(20250408).pdf

# 2. PDF → JSON 변환 (조문별로 자동 분리)
python scripts/parse_statute_pdf.py "형법(법률)(제20908호)(20250408).pdf"
# → data/collected/statutes/형법/ 폴더에 조문별 JSON 파일 생성

# 3. 벡터 DB 인덱싱 (하위 디렉토리 자동 검색)
curl -X POST "http://localhost:8000/api/v1/admin/index" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "data/collected/statutes",
    "pattern": "*.json",
    "chunk": true
  }'
```

### 예제 3: 폴더 내 모든 PDF 일괄 처리

```bash
# 1. 폴더 내 모든 판례 PDF 변환
python scripts/parse_case_pdf.py "data/pdfs/cases/" --folder

# 2. 변환된 모든 JSON 파일 인덱싱
curl -X POST "http://localhost:8000/api/v1/admin/index" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "data/collected/cases",
    "pattern": "*.json",
    "chunk": true
  }'
```

---

## 🔄 증분 인덱싱 (변경된 파일만 업데이트)

새로 추가되거나 변경된 파일만 인덱싱:

```bash
# API 사용
curl -X POST "http://localhost:8000/api/v1/admin/index/incremental?directory=data/collected/cases&pattern=*.json" \
  -H "X-API-Key: your_api_key"
```

**Python 사용**:
```python
from pathlib import Path
from src.rag import DocumentIndexer, IncrementalUpdater

indexer = DocumentIndexer()
updater = IncrementalUpdater(indexer)

results = updater.update_incremental(
    directory=Path("data/collected/cases"),
    pattern="*.json"
)

print(f"신규: {results['new']}건")
print(f"업데이트: {results['updated']}건")
print(f"스킵: {results['skipped']}건")
```

---

## 📂 파일 저장 위치 정리

### 입력 파일 (PDF)
- **위치**: 어디든 상관없음
- **권장**: `data/pdfs/cases/` 또는 `data/pdfs/statutes/`

### 변환된 JSON 파일
- **판례**: `data/collected/cases/`
- **법령**: `data/collected/statutes/` (법률별 하위 폴더)

### 벡터 DB 저장소
- **위치**: `data/vector_db/` (ChromaDB)
- **설정**: `config/settings.py`의 `CHROMA_PERSIST_DIRECTORY`

---

## ✅ 체크리스트

### PDF 변환 전
- [ ] PDF 파일이 텍스트 추출 가능한지 확인
- [ ] PyPDF2 설치 확인 (`pip install PyPDF2`)
- [ ] PDF 파일 경로 확인

### JSON 변환 후
- [ ] `data/collected/cases/` 또는 `data/collected/statutes/`에 JSON 파일 생성 확인
- [ ] JSON 파일 내용 확인 (필수 필드 포함 여부)

### 인덱싱 전
- [ ] API 서버 실행 확인 (`http://localhost:8000`)
- [ ] API 키 확인 (`.env` 파일의 `API_KEY`)
- [ ] OpenAI API 키 확인 (`.env` 파일의 `OPENAI_API_KEY`)

### 인덱싱 후
- [ ] 인덱스 상태 확인 (`GET /api/v1/admin/index/status`)
- [ ] 검색 테스트 (`POST /api/v1/search`)
- [ ] 검색 결과 확인

---

## 🛠 문제 해결

### PDF 변환 실패
```
오류: PyPDF2가 설치되지 않았습니다.
해결: pip install PyPDF2
```

### 인덱싱 실패
```
오류: ValidationError: 필수 필드 'id'가 없습니다.
해결: JSON 파일 형식 확인 (data/samples/ 참고)
```

### 검색 결과 없음
```
원인: 인덱싱이 완료되지 않음
해결: 인덱스 상태 확인 후 재인덱싱
```

---

## 📚 추가 자료

- **상세 가이드**: [RAG_DATA_BUILD_GUIDE.md](./RAG_DATA_BUILD_GUIDE.md)
- **API 문서**: http://localhost:8000/docs
- **샘플 데이터**: `data/samples/` 디렉토리 참고

---

## 🎯 요약

1. **PDF 파일**: 어디든 저장 가능
2. **변환**: `parse_case_pdf.py` 또는 `parse_statute_pdf.py` 실행
3. **JSON 저장**: `data/collected/` 폴더에 자동 저장
4. **인덱싱**: API 또는 Python 스크립트로 벡터 DB에 저장
5. **검색**: 인덱싱 완료 후 검색 가능

**전체 프로세스는 약 3단계**:
```
PDF → JSON 변환 → 벡터 DB 인덱싱 → 검색 가능 ✅
```
