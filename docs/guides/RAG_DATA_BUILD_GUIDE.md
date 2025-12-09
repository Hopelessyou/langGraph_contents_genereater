# RAG 데이터 구축 가이드

## 📋 목차

1. [개요](#개요)
2. [데이터 타입별 수집 방법](#데이터-타입별-수집-방법)
3. [데이터 전처리 및 검증](#데이터-전처리-및-검증)
4. [벡터화 및 인덱싱](#벡터화-및-인덱싱)
5. [실전 예제](#실전-예제)
6. [문제 해결](#문제-해결)

---

## 개요

### RAG 데이터 구축이란?

RAG(Retrieval-Augmented Generation) 데이터 구축은 법률 문서를 벡터 데이터베이스에 저장하여 AI가 검색하고 활용할 수 있도록 준비하는 과정입니다.

**구축 목적:**
- 법률 정보의 빠른 검색
- 정확한 법률 상담 제공
- 판례 및 법령 참조
- 실무 매뉴얼 활용

**구축 프로세스:**
```
원본 데이터 → 수집 → 전처리 → 검증 → 청킹 → 임베딩 → 벡터 DB 저장
```

---

## 데이터 타입별 수집 방법

이 시스템은 **10가지 법률 데이터 타입**을 지원합니다:

1. **법령 (statute)** - 법률 조문
2. **판례 (case)** - 법원 판결 요약
3. **절차 매뉴얼 (procedure)** - 법률 절차 안내
4. **실무 매뉴얼 (manual)** - 실무 가이드
5. **사건 유형 (case_type)** - 사건 분류 정의
6. **템플릿 (template)** - 문서 템플릿
7. **양형기준 (sentencing_guideline)** - 형량 기준
8. **FAQ (faq)** - 자주 묻는 질문
9. **키워드 맵핑 (keyword_mapping)** - 키워드-사건 연결
10. **스타일 문제 (style_issue)** - 문서 스타일 가이드

---

### 1. 법령 데이터 (Statute) 수집

**데이터 소스:**
- 법제처 국가법령정보센터 (https://www.law.go.kr)
- 공공데이터포털 법령 API
- 법제처 PDF 파일

**수집 방법:**

#### 방법 1: PDF 파일에서 자동 변환 (권장)
```bash
# PDF 파일을 조문별 JSON으로 자동 변환
python scripts/parse_statute_pdf.py "형법(법률)(제20908호)(20250408).pdf"

# 출력 디렉토리 지정
python scripts/parse_statute_pdf.py "형법.pdf" --output-dir data/collected/statutes

# 개정일 지정
python scripts/parse_statute_pdf.py "형법.pdf" --updated-at "2025-04-08"
```

**생성되는 구조:**
```
data/collected/statutes/
└── 형법/
    ├── statute-형법-1.json
    ├── statute-형법-2.json
    ├── statute-형법-347.json
    └── ...
```

**특징:**
- 조문 단위로 자동 분리
- 법률별 폴더 자동 생성
- 카테고리 및 키워드 자동 추출
- 메타데이터 자동 생성

#### 방법 2: 수집 스크립트 사용
```bash
python scripts/collect_data.py --type statute
```

#### 방법 3: 직접 JSON 파일 작성
```json
{
  "id": "statute-347",
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
    "updated_at": "2024-01-01"
  }
}
```

**저장 위치:** `data/collected/statutes/` 또는 `data/samples/`

---

### 2. 판례 데이터 (Case) 수집

**데이터 소스:**
- 법원종합법률정보 (https://glaw.scourt.go.kr)
- 대법원 판례집

**수집 방법:**

```bash
python scripts/collect_data.py --type case
```

**JSON 형식:**
```json
{
  "id": "case-2023do11234",
  "category": "형사",
  "sub_category": "사기",
  "type": "case",
  "title": "대법원 2023. 3. 15. 선고 2023도11234 판결",
  "content": [
    "【사건개요】 피고인은 피해자에게 거짓말로 돈을 받아 챙긴 혐의로 기소되었다.",
    "【쟁점】 사기죄의 기망행위와 착오의 인과관계",
    "【판단】 피고인의 기망행위와 피해자의 착오 사이에 인과관계가 인정된다.",
    "【결론】 원심판결을 파기하고 사건을 환송한다."
  ],
  "metadata": {
    "case_number": "2023도11234",
    "court": "대법원",
    "date": "2023-03-15",
    "judge": "주심 판사",
    "related_statutes": ["형법 제347조"],
    "keywords": ["사기", "기망", "착오"]
  }
}
```

---

### 3. 절차 매뉴얼 (Procedure) 수집

**데이터 소스:**
- 각 기관별 절차 안내서
- 법률 절차 매뉴얼 문서

**수집 방법:**

```bash
# 마크다운 파일에서 수집
python scripts/collect_data.py --type manual \
  --source-dir data/sources/manuals
```

**JSON 형식:**
```json
{
  "id": "procedure-police-fraud",
  "category": "형사",
  "sub_category": "사기",
  "type": "procedure",
  "title": "사기 사건 경찰 신고 절차",
  "content": [
    "1. 신고 접수",
    "   - 관할 경찰서 방문 또는 전화 신고",
    "   - 신고서 작성 및 증거 제출",
    "2. 수사 진행",
    "   - 피의자 조사",
    "   - 증거 수집",
    "3. 송치",
    "   - 검찰로 사건 송치"
  ],
  "metadata": {
    "agency": "경찰청",
    "procedure_type": "신고",
    "related_case_types": ["사기"],
    "estimated_time": "1-2주"
  }
}
```

---

### 4. 실무 매뉴얼 (Manual) 수집

**데이터 소스:**
- 법률 실무 가이드북
- 변호사 실무 매뉴얼

**수집 방법:**

```bash
python scripts/collect_data.py --type manual \
  --source-dir data/sources/manuals
```

**JSON 형식:**
```json
{
  "id": "manual-fraud-defense",
  "category": "형사",
  "sub_category": "사기",
  "type": "manual",
  "title": "사기 사건 변호 실무 매뉴얼",
  "content": [
    "# 사기 사건 변호 전략",
    "## 1. 사건 분석",
    "- 피의자 진술 검토",
    "- 증거 분석",
    "## 2. 변호 전략",
    "- 무죄 주장",
    "- 형량 감경 주장"
  ],
  "metadata": {
    "target_audience": "변호사",
    "difficulty": "중급",
    "related_topics": ["사기", "변호", "형사소송"]
  }
}
```

---

### 5. 사건 유형 (Case Type) 수집

**용도:** 사건을 자동으로 분류하기 위한 정의서

**JSON 형식:**
```json
{
  "id": "case-type-fraud",
  "category": "형사",
  "sub_category": "사기",
  "type": "case_type",
  "title": "사기 사건 유형 정의",
  "content": {
    "definition": "사람을 기망하여 재물을 편취하는 범죄",
    "keywords": ["사기", "편취", "기망", "재물"],
    "related_statutes": ["형법 제347조"],
    "typical_cases": ["전화 사기", "인터넷 사기", "계약 사기"],
    "defense_strategies": ["기망행위 부인", "착오 인과관계 부인"]
  },
  "metadata": {
    "severity": "중",
    "common_sentence": "집행유예 또는 징역형"
  }
}
```

---

### 6. 템플릿 (Template) 수집

**용도:** 법률 문서 작성 시 사용할 템플릿

**JSON 형식:**
```json
{
  "id": "template-criminal-fraud",
  "category": "형사",
  "sub_category": "사기",
  "type": "template",
  "title": "사기 사건 변호사 의견서 템플릿",
  "content": {
    "structure": [
      "1. 사건 개요",
      "2. 법리 검토",
      "3. 변호 의견",
      "4. 결론"
    ],
    "sections": {
      "overview": "{{case_description}}",
      "legal_review": "{{statute_reference}}",
      "opinion": "{{defense_argument}}",
      "conclusion": "{{request}}"
    },
    "variables": ["case_description", "statute_reference", "defense_argument", "request"]
  },
  "metadata": {
    "document_type": "의견서",
    "target_audience": "변호사",
    "format": "docx"
  }
}
```

---

### 7. 양형기준 (Sentencing Guideline) 수집

**용도:** 형량 산정 기준 제공

**JSON 형식:**
```json
{
  "id": "sentencing-fraud",
  "category": "형사",
  "sub_category": "사기",
  "type": "sentencing_guideline",
  "title": "사기죄 양형기준",
  "content": {
    "base_sentence": "1-3년 징역",
    "aggravating_factors": {
      "large_amount": "+1-2년",
      "organized_crime": "+2-3년",
      "repeat_offender": "+1년"
    },
    "mitigating_factors": {
      "first_offense": "-6개월~1년",
      "restitution": "-6개월",
      "cooperation": "-3개월"
    },
    "typical_sentences": [
      "초범 + 소액: 집행유예",
      "초범 + 중액: 1-2년 징역",
      "재범: 2-4년 징역"
    ]
  },
  "metadata": {
    "source": "대법원 양형기준",
    "updated_at": "2024-01-01"
  }
}
```

---

### 8. FAQ (Frequently Asked Questions) 수집

**수집 방법:**

```bash
# CSV 파일에서 수집
python scripts/collect_data.py --type faq \
  --source-file data/sources/faqs.csv
```

**JSON 형식:**
```json
{
  "id": "faq-fraud-001",
  "category": "형사",
  "sub_category": "사기",
  "type": "faq",
  "title": "사기 초범은 집행유예가 가능한가요?",
  "content": {
    "question": "사기 초범은 집행유예가 가능한가요?",
    "answer": "사기 초범이라도 피해 규모가 크면 집행유예가 어려울 수 있습니다. 일반적으로 피해액이 1천만원 미만이고 피해 회복이 이루어진 경우 집행유예 가능성이 높습니다."
  },
  "metadata": {
    "frequency": "high",
    "related_questions": ["faq-fraud-002"],
    "tags": ["집행유예", "초범", "피해액"]
  }
}
```

---

### 9. 키워드 맵핑 (Keyword Mapping) 수집

**용도:** 사용자 입력 키워드를 사건 유형으로 자동 매핑

**JSON 형식:**
```json
{
  "id": "keyword-mapping-fraud",
  "category": "형사",
  "sub_category": "사기",
  "type": "keyword_mapping",
  "title": "사기 관련 키워드 맵핑",
  "content": {
    "keywords": ["사기", "편취", "기망", "거짓말", "속임수"],
    "mapped_case_type": "case-type-fraud",
    "confidence": 0.95,
    "synonyms": {
      "사기": ["편취", "기망", "속임"],
      "거짓말": ["허위", "기망"]
    }
  },
  "metadata": {
    "priority": "high",
    "usage_count": 150
  }
}
```

---

### 10. 스타일 문제 (Style Issue) 수집

**용도:** 생성된 텍스트의 법률 용어 및 스타일 검증

**JSON 형식:**
```json
{
  "id": "style-issue-001",
  "category": "형사",
  "sub_category": "사기",
  "type": "style_issue",
  "title": "법률 용어 오용 검사",
  "content": {
    "issue_type": "terminology",
    "incorrect": "사기범",
    "correct": "사기범죄",
    "description": "'사기범'은 사람을 지칭하므로, 범죄를 지칭할 때는 '사기범죄'를 사용해야 합니다.",
    "examples": [
      {
        "wrong": "사기범을 처벌한다.",
        "right": "사기범죄를 처벌한다."
      }
    ]
  },
  "metadata": {
    "severity": "medium",
    "category": "terminology"
  }
}
```

---

## 데이터 전처리 및 검증

### 1. 데이터 검증

**자동 검증:**

```python
from src.processors.validator import DocumentValidator

validator = DocumentValidator()

# JSON 파일 검증
success, model = validator.validate(json_data)

if success:
    print(f"검증 성공: {model.type}")
else:
    print(f"검증 실패: {validator.get_errors()}")
```

**검증 항목:**
- ✅ 필수 필드 존재 여부 (id, type, title, content 등)
- ✅ 데이터 타입 일치 (문자열, 숫자, 배열 등)
- ✅ 문서 타입별 스키마 검증
- ✅ 메타데이터 필드 검증

---

### 2. 데이터 정제

**자동 정제:**

```python
from src.processors.cleaner import DataCleaner

cleaner = DataCleaner()

# 데이터 정제
cleaned_data = cleaner.clean(document_data)

# 중복 제거
unique_documents = cleaner.remove_duplicates(documents)
```

**정제 작업:**
- 공백 및 특수문자 정리
- 인코딩 정규화 (UTF-8)
- 중복 문서 제거
- 품질 검사 (최소 길이, 필수 키워드 등)

---

### 3. 배치 처리

**여러 파일 일괄 처리:**

```python
from src.processors.pipeline import BatchProcessor

processor = BatchProcessor()

# 디렉토리 내 모든 파일 처리
results = processor.process_directory(
    input_dir="data/collected",
    output_dir="data/processed",
    doc_type="statute"
)

print(f"처리 완료: {results['success']}/{results['total']}")
```

---

## 벡터화 및 인덱싱

### 1. 단일 파일 인덱싱

**Python 스크립트:**

```python
from pathlib import Path
from src.rag import DocumentIndexer

# 인덱서 생성
indexer = DocumentIndexer()

# 단일 파일 인덱싱
result = indexer.index_file("data/samples/statute-347.json")

if result["success"]:
    print(f"인덱싱 성공: {result['chunks_count']}개 청크")
else:
    print(f"인덱싱 실패: {result['error']}")
```

---

### 2. 디렉토리 일괄 인덱싱

**Python 스크립트:**

```python
from pathlib import Path
from src.rag import DocumentIndexer

indexer = DocumentIndexer()

# 디렉토리 내 모든 JSON 파일 인덱싱 (하위 디렉토리 포함)
results = indexer.index_directory(
    directory=Path("data/collected/statutes"),
    pattern="*.json",
    chunk=True,  # 청킹 사용
    recursive=True  # 하위 디렉토리 재귀 검색 (기본값: True)
)

print(f"총 {results['total']}건 중 {results['success']}건 성공")
print(f"실패: {results['failed']}건")
```

**법률별 폴더 구조 지원:**
```
data/collected/statutes/
├── 형법/
│   ├── statute-형법-1.json
│   └── statute-형법-347.json
├── 형사소송법/
│   └── statute-형사소송법-250.json
└── ...
```

`recursive=True`로 설정하면 모든 하위 디렉토리의 JSON 파일을 자동으로 검색합니다.

---

### 3. 전체 데이터 폴더 인덱싱

`data` 폴더의 모든 파일을 한 번에 인덱싱하는 방법입니다.

#### 방법 1: Python 스크립트 실행 (권장)

프로젝트에 포함된 스크립트를 사용하여 `data` 폴더의 모든 파일을 자동으로 인덱싱할 수 있습니다.

**터미널에서 실행:**

```bash
python scripts/index_all_data.py
```

**스크립트 기능:**
- `data/processed/` 폴더의 모든 JSON 파일 인덱싱
- `data/collected/` 폴더의 모든 JSON 파일 인덱싱
- 하위 디렉토리까지 재귀적으로 검색
- 진행 상황과 결과 통계 실시간 출력
- 실패한 파일 목록 표시

**실행 결과 예시:**
```
================================================================================
전체 데이터 인덱싱 시작
================================================================================

================================================================================
인덱싱 중: 처리된 데이터 (processed)
경로: data/processed
================================================================================

✅ 처리된 데이터 (processed) 인덱싱 완료:
   총 파일: 803개
   성공: 803개
   실패: 0개
   청크 수: 2456개

================================================================================
인덱싱 중: 수집된 데이터 (collected)
경로: data/collected
================================================================================

✅ 수집된 데이터 (collected) 인덱싱 완료:
   총 파일: 1926개
   성공: 1926개
   실패: 0개
   청크 수: 5234개

================================================================================
전체 인덱싱 완료
================================================================================
총 파일 수: 2729개
성공: 2729개
실패: 0개
총 청크 수: 7690개
================================================================================
```

#### 방법 2: Python 코드로 직접 실행

특정 폴더만 선택적으로 인덱싱하려면 Python 코드를 사용할 수 있습니다.

```python
from pathlib import Path
from src.rag import DocumentIndexer

indexer = DocumentIndexer()

# processed/cases 폴더만 인덱싱
results = indexer.index_directory(
    directory=Path("data/processed/cases"),
    pattern="*.json",
    chunk=True,
    recursive=True
)

print(f"성공: {results['success']}/{results['total']}")
print(f"실패: {results['failed']}개")
```

**여러 폴더를 순차적으로 인덱싱:**

```python
from pathlib import Path
from src.rag import DocumentIndexer

indexer = DocumentIndexer()

# 인덱싱할 폴더 목록
directories = [
    "data/processed/cases",
    "data/processed/statutes",
    "data/collected/cases",
]

total_success = 0
total_files = 0

for directory in directories:
    print(f"\n인덱싱 중: {directory}")
    results = indexer.index_directory(
        directory=Path(directory),
        pattern="*.json",
        chunk=True,
        recursive=True
    )
    total_success += results['success']
    total_files += results['total']
    print(f"  성공: {results['success']}/{results['total']}")

print(f"\n전체 결과: {total_success}/{total_files}개 성공")
```

#### 방법 3: API를 통한 전체 인덱싱

서버가 실행 중이면 Swagger UI에서도 전체 데이터를 인덱싱할 수 있습니다.

**Swagger UI 사용:**

1. `http://localhost:8000/docs` 접속
2. `POST /api/v1/admin/index` 엔드포인트 선택
3. "Try it out" 클릭
4. 각 디렉토리별로 요청:

**processed 폴더 인덱싱:**
```json
{
  "directory": "data/processed",
  "pattern": "*.json",
  "chunk": true
}
```

**collected 폴더 인덱싱:**
```json
{
  "directory": "data/collected",
  "pattern": "*.json",
  "chunk": true
}
```

5. "Execute" 클릭

**cURL 사용:**

```bash
# processed 폴더 인덱싱
curl -X POST "http://localhost:8000/api/v1/admin/index" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "data/processed",
    "pattern": "*.json",
    "chunk": true
  }'

# collected 폴더 인덱싱
curl -X POST "http://localhost:8000/api/v1/admin/index" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "data/collected",
    "pattern": "*.json",
    "chunk": true
  }'
```

#### 주의사항

1. **인덱싱 시간**: 파일 수가 많을 경우 인덱싱에 시간이 걸릴 수 있습니다.
   - 약 1000개 파일: 10-20분
   - 약 2000개 파일: 20-40분
   - 약 3000개 파일: 40-60분

2. **메모리 사용량**: 대량 인덱싱 시 메모리 사용량이 증가할 수 있습니다.

3. **중복 인덱싱**: 같은 파일을 여러 번 인덱싱하면 중복 데이터가 생성될 수 있습니다. 기존 인덱스를 초기화하려면:
   ```python
   from src.rag import VectorStore
   vector_store = VectorStore()
   vector_store.reset()  # 주의: 모든 데이터가 삭제됩니다!
   ```

4. **증분 인덱싱**: 새로 추가된 파일만 인덱싱하려면 증분 인덱싱 기능을 사용하세요 (아래 섹션 참조).

---

### 4. API를 통한 인덱싱

**Swagger UI 사용:**

1. `http://localhost:8000/docs` 접속
2. `POST /api/v1/admin/index` 선택
3. "Try it out" 클릭
4. 요청 본문 입력:
   ```json
   {
     "directory": "data/samples",
     "pattern": "*.json",
     "chunk": true
   }
   ```
5. "Execute" 클릭

**cURL 사용:**

```bash
curl -X POST "http://localhost:8000/api/v1/admin/index" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "data/samples",
    "pattern": "*.json",
    "chunk": true
  }'
```

**Python requests 사용:**

```python
import requests

url = "http://localhost:8000/api/v1/admin/index"
headers = {
    "X-API-Key": "your_api_key",
    "Content-Type": "application/json"
}
data = {
    "directory": "data/samples",
    "pattern": "*.json",
    "chunk": True
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

---

### 5. 파일 업로드 및 인덱싱

**Swagger UI 사용:**

1. `POST /api/v1/admin/upload` 선택
2. "Try it out" 클릭
3. "Choose File" 버튼으로 JSON 파일 선택
4. "Execute" 클릭

**Python requests 사용:**

```python
import requests

url = "http://localhost:8000/api/v1/admin/upload"
headers = {"X-API-Key": "your_api_key"}

with open("data/samples/statute-347.json", "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files, headers=headers)
    print(response.json())
```

---

### 6. 증분 인덱싱

**새로 추가되거나 변경된 파일만 인덱싱:**

```python
from src.rag import DocumentIndexer, IncrementalUpdater

indexer = DocumentIndexer()
updater = IncrementalUpdater(indexer)

# 증분 업데이트
results = updater.update_incremental(
    directory=Path("data/collected"),
    pattern="*.json"
)

print(f"신규: {results['new']}건")
print(f"업데이트: {results['updated']}건")
print(f"스킵: {results['skipped']}건")
```

**API 사용:**

```bash
curl -X POST "http://localhost:8000/api/v1/admin/index/incremental?directory=data/collected&pattern=*.json" \
  -H "X-API-Key: your_api_key"
```

---

## 실전 예제

### 예제 1: 처음부터 끝까지 데이터 구축

```bash
# 1. 데이터 수집
python scripts/collect_data.py --type all \
  --output-dir data/collected

# 2. 데이터 검증 및 정제 (선택사항)
python -c "
from src.processors.pipeline import BatchProcessor
processor = BatchProcessor()
processor.process_directory('data/collected', 'data/processed')
"

# 3. 벡터 DB 인덱싱
python -c "
from pathlib import Path
from src.rag import DocumentIndexer
indexer = DocumentIndexer()
results = indexer.index_directory(Path('data/collected'), '*.json')
print(f'인덱싱 완료: {results[\"success\"]}/{results[\"total\"]}건')
"
```

---

### 예제 2: 특정 데이터 타입만 구축

```bash
# 법령 데이터만 수집 및 인덱싱
python scripts/collect_data.py --type statute

# API로 인덱싱
curl -X POST "http://localhost:8000/api/v1/admin/index" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "data/collected/statutes",
    "pattern": "*.json",
    "chunk": true
  }'
```

---

### 예제 3: 샘플 데이터로 테스트

```bash
# 샘플 데이터 인덱싱
python -c "
from pathlib import Path
from src.rag import DocumentIndexer
indexer = DocumentIndexer()
results = indexer.index_directory(Path('data/samples'), '*.json')
print(results)
"
```

---

### 예제 4: Python 스크립트로 전체 파이프라인

```python
# build_rag_data.py
from pathlib import Path
from src.rag import DocumentIndexer
from src.processors.pipeline import BatchProcessor
import logging

logging.basicConfig(level=logging.INFO)

def build_rag_data():
    """RAG 데이터 구축 전체 파이프라인"""
    
    # 1. 데이터 처리
    print("1. 데이터 처리 중...")
    processor = BatchProcessor()
    processor.process_directory(
        input_dir=Path("data/collected"),
        output_dir=Path("data/processed")
    )
    
    # 2. 벡터 DB 인덱싱
    print("2. 벡터 DB 인덱싱 중...")
    indexer = DocumentIndexer()
    results = indexer.index_directory(
        directory=Path("data/processed"),
        pattern="*.json",
        chunk=True
    )
    
    # 3. 결과 출력
    print(f"\n인덱싱 완료!")
    print(f"총 {results['total']}건 중 {results['success']}건 성공")
    print(f"실패: {results['failed']}건")
    
    # 4. 인덱스 상태 확인
    status = indexer.get_index_status()
    print(f"\n인덱스 상태:")
    print(f"- 컬렉션: {status['collection_name']}")
    print(f"- 문서 수: {status['document_count']}")

if __name__ == "__main__":
    build_rag_data()
```

실행:
```bash
python build_rag_data.py
```

---

## 문제 해결

### 문제 1: 검증 실패

**증상:**
```
ValidationError: 필수 필드 'id'가 없습니다.
```

**해결:**
- JSON 파일에 필수 필드가 모두 있는지 확인
- `data/samples/` 디렉토리의 샘플 파일 참고
- Pydantic 모델 스키마 확인

---

### 문제 2: 임베딩 생성 실패

**증상:**
```
OpenAI API Error: Rate limit exceeded
```

**해결:**
- API 키 확인: `.env` 파일의 `OPENAI_API_KEY` 설정
- 요청 속도 제한: 배치 크기 줄이기
- 재시도 로직: 자동 재시도 기능 사용

---

### 문제 3: 벡터 DB 저장 실패

**증상:**
```
ChromaDB Error: Collection not found
```

**해결:**
- ChromaDB 디렉토리 확인: `CHROMA_PERSIST_DIRECTORY` 설정
- 컬렉션 자동 생성: 코드에서 자동 생성됨
- 권한 확인: 디렉토리 쓰기 권한 확인

---

### 문제 4: 인덱싱 속도가 느림

**해결:**
- 배치 크기 조정: 한 번에 더 많은 문서 처리
- 청킹 비활성화: 작은 문서는 `chunk=False`
- 증분 인덱싱 사용: 변경된 파일만 업데이트

---

## 모니터링 및 확인

### 인덱스 상태 확인

**API 사용:**
```bash
curl http://localhost:8000/api/v1/admin/index/status
```

**Python 사용:**
```python
from src.rag import DocumentIndexer

indexer = DocumentIndexer()
status = indexer.get_index_status()
print(status)
```

**응답 예시:**
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

---

### 검색 테스트

인덱싱이 완료되면 검색 API로 테스트:

```python
import requests

# 검색 테스트
response = requests.post(
    "http://localhost:8000/api/v1/search",
    json={"query": "사기죄", "n_results": 5}
)

print(response.json())
```

---

## 최적화 팁

1. **청킹 전략 조정**
   - 법령: 조문 단위 (큰 청크)
   - 판례: 요지 단위 (중간 청크)
   - FAQ: 전체 문서 (작은 청크)

2. **임베딩 모델 선택**
   - 정확도 우선: `text-embedding-3-large`
   - 속도 우선: `text-embedding-3-small`

3. **증분 업데이트 활용**
   - 전체 재인덱싱 대신 변경된 파일만 업데이트
   - 시간 및 비용 절감

4. **메타데이터 활용**
   - 검색 필터링을 위한 메타데이터 충실히 작성
   - 카테고리, 문서 타입 등 필수 메타데이터 포함

---

이제 RAG 데이터를 구축할 준비가 되었습니다! 🚀

