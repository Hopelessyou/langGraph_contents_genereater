# RAG 데이터 처리 가이드 (상세 사용법)

이 문서는 `RAG_DATA_BUILD_GUIDE.md`의 435-569 라인에 해당하는 데이터 전처리 및 인덱싱 기능의 상세한 사용법을 설명합니다.

---

## 목차

1. [빠른 시작](#빠른-시작)
2. [데이터 검증 (DocumentValidator)](#1-데이터-검증-documentvalidator)
3. [데이터 정제 (DataCleaner)](#2-데이터-정제-datacleaner)
4. [배치 처리 (BatchProcessor)](#3-배치-처리-batchprocessor)
5. [벡터화 및 인덱싱 (DocumentIndexer)](#4-벡터화-및-인덱싱-documentindexer)

---

## 빠른 시작

### 방법 1: 스크립트 사용 (권장)

가장 간단한 방법은 제공된 스크립트를 사용하는 것입니다:

```bash
# 법령 데이터 처리 및 인덱싱
python scripts/process_and_index.py \
    --input-dir "data/collected/statutes" \
    --doc-type "statute" \
    --collection-name "legal_documents"

# 판례 데이터 처리 및 인덱싱
python scripts/process_and_index.py \
    --input-dir "data/collected/cases" \
    --doc-type "case" \
    --collection-name "legal_documents"

# 전처리만 수행 (인덱싱 건너뛰기)
python scripts/process_and_index.py \
    --input-dir "data/collected/statutes" \
    --doc-type "statute" \
    --skip-index

# 인덱싱만 수행 (전처리 건너뛰기)
python scripts/process_and_index.py \
    --input-dir "data/processed/statutes" \
    --doc-type "statute" \
    --skip-process
```

### 방법 2: Python 코드로 직접 실행

```python
# process_data.py 파일 생성
from src.processors.pipeline import BatchProcessor
from src.rag import DocumentIndexer
from pathlib import Path

# 1단계: 전처리
processor = BatchProcessor()
results = processor.process_directory(
    input_dir="data/collected/statutes",
    output_dir="data/processed/statutes",
    doc_type="statute",
    clean=True,
    validate=True,
    remove_duplicates=True,
)

print(f"전처리 완료: {results['success']}/{results['total']}")

# 2단계: 인덱싱
indexer = DocumentIndexer(collection_name="legal_documents")
index_results = indexer.index_directory(
    directory=Path("data/processed/statutes"),
    pattern="*.json",
    chunk=True,
    recursive=True,
)

print(f"인덱싱 완료: {index_results['success']}/{index_results['total']}")
```

---

## 1. 데이터 검증 (DocumentValidator)

### 개요

`DocumentValidator`는 수집된 JSON 파일이 올바른 스키마를 따르는지 검증하는 도구입니다. Pydantic 모델을 사용하여 타입 안전성을 보장합니다.

### 기본 사용법

#### 1.1 단일 JSON 데이터 검증

```python
from src.processors.validator import DocumentValidator
import json

# 검증기 생성
validator = DocumentValidator()

# JSON 데이터 준비 (딕셔너리 형식)
json_data = {
    "id": "statute-형법-347",
    "category": "형사",
    "sub_category": "사기",
    "type": "statute",
    "title": "형법 제347조",
    "content": "사기죄의 조문 내용...",
    "metadata": {
        "law_name": "형법",
        "article_number": "347",
        "topics": ["사기"],
        "source": "법제처",
        "updated_at": "2024-01-01",
    },
}

# 검증 수행
success, model = validator.validate(json_data)

if success:
    print(f"✅ 검증 성공: {model.type}")
    print(f"   문서 ID: {model.id}")
    print(f"   제목: {model.title}")
    # model은 Pydantic 모델 인스턴스이므로 타입 안전하게 접근 가능
else:
    print(f"❌ 검증 실패:")
    for error in validator.get_errors():
        print(f"   - {error}")
```

#### 1.2 JSON 파일 검증

```python
from pathlib import Path
from src.processors.validator import DocumentValidator

validator = DocumentValidator()

# 파일 경로 지정
file_path = Path("data/collected/statutes/형법/statute-형법-347.json")

# 파일 검증
success, model = validator.validate_file(file_path)

if success:
    print(f"✅ 파일 검증 성공: {file_path.name}")
    print(f"   문서 타입: {model.type}")
else:
    print(f"❌ 파일 검증 실패: {file_path.name}")
    for error in validator.get_errors():
        print(f"   - {error}")
```

#### 1.3 여러 문서 일괄 검증

```python
from src.processors.validator import DocumentValidator
import json
from pathlib import Path

validator = DocumentValidator()

# 여러 JSON 파일 읽기
json_files = [
    "data/collected/statutes/형법/statute-형법-347.json",
    "data/collected/statutes/형법/statute-형법-348.json",
    "data/collected/cases/case-2010도12928.json",
]

# 모든 파일의 데이터를 리스트로 수집
data_list = []
for file_path in json_files:
    with open(file_path, "r", encoding="utf-8") as f:
        data_list.append(json.load(f))

# 일괄 검증
results = validator.validate_batch(data_list)

# 결과 확인
for doc_id, (success, model) in results.items():
    if success:
        print(f"✅ {doc_id}: 검증 성공")
    else:
        print(f"❌ {doc_id}: 검증 실패")
```

### 검증 항목

`DocumentValidator`는 다음 항목들을 자동으로 검증합니다:

1. **기본 구조 검증**
   - 데이터가 딕셔너리 형식인지 확인
   - `type` 필드 존재 여부 확인
   - 지원하는 문서 타입인지 확인

2. **타입별 스키마 검증**
   - `statute`: `StatuteModel` 스키마 검증
   - `case`: `CaseModel` 스키마 검증
   - `procedure`: `ProcedureModel` 스키마 검증
   - `template`: `TemplateModel` 스키마 검증
   - 기타 문서 타입별 모델 검증

3. **필수 필드 검증**
   - `id`, `type`, `title`, `content` 등 필수 필드 존재 여부
   - 각 필드의 데이터 타입 일치 여부

4. **메타데이터 검증**
   - 문서 타입별 필수 메타데이터 필드 확인

### 지원하는 문서 타입

- `statute`: 법령
- `case`: 판례
- `procedure`: 절차
- `template`: 템플릿
- `manual`: 매뉴얼
- `case_type`: 사건 유형
- `sentencing_guideline`: 양형 가이드라인
- `faq`: FAQ
- `style_issue`: 스타일 이슈

---

## 2. 데이터 정제 (DataCleaner)

### 개요

`DataCleaner`는 수집된 데이터의 품질을 향상시키기 위해 정제 작업을 수행하는 도구입니다.

### 기본 사용법

#### 2.1 단일 문서 정제

```python
from src.processors.cleaner import DataCleaner

cleaner = DataCleaner()

# 정제할 데이터
document_data = {
    "id": "statute-test",
    "title": "  형법 제347조  ",  # 앞뒤 공백
    "content": "사기죄의   내용입니다.\n\n\n여러 줄바꿈이 있습니다.",
    "metadata": {
        "law_name": "형법",
        "article_number": "347",
    }
}

# 모든 정제 규칙 적용
cleaned_data = cleaner.clean(document_data)

print("정제 전:", document_data["title"])
print("정제 후:", cleaned_data["title"])
# 출력: 정제 전: "  형법 제347조  "
# 출력: 정제 후: "형법 제347조"
```

#### 2.2 특정 정제 규칙만 적용

```python
from src.processors.cleaner import DataCleaner

cleaner = DataCleaner()

# 공백 정제만 적용
cleaned_data = cleaner.clean(
    document_data,
    rules=["whitespace"]  # 특정 규칙만 지정
)

# 여러 규칙 선택적 적용
cleaned_data = cleaner.clean(
    document_data,
    rules=["whitespace", "special_chars"]  # 공백 + 특수문자 정제
)
```

#### 2.3 중복 문서 제거

```python
from src.processors.cleaner import DataCleaner

cleaner = DataCleaner()

# 여러 문서 리스트
documents = [
    {"id": "doc1", "title": "형법 제347조", "content": "내용1"},
    {"id": "doc2", "title": "형법 제348조", "content": "내용2"},
    {"id": "doc1", "title": "형법 제347조", "content": "내용1"},  # 중복
    {"id": "doc3", "title": "형법 제349조", "content": "내용3"},
]

# 중복 제거 (id 기준)
unique_documents = cleaner.remove_duplicates(documents)

print(f"원본: {len(documents)}개")
print(f"중복 제거 후: {len(unique_documents)}개")
# 출력: 원본: 4개
# 출력: 중복 제거 후: 3개
```

### 정제 규칙

`DataCleaner`는 다음 정제 규칙을 제공합니다:

1. **whitespace**: 공백 정제
   - 문자열 필드의 앞뒤 공백 제거
   - 리스트 내 문자열 항목의 공백 제거
   - 중첩된 딕셔너리도 재귀적으로 처리

2. **special_chars**: 특수문자 정제
   - 연속된 공백을 하나로 통합
   - 제어 문자 제거 (`\x00-\x1f`, `\x7f-\x9f`)
   - `title`, `content` 필드에 적용

3. **empty_fields**: 빈 필드 제거 (선택적)
   - `None` 값 제거
   - 빈 문자열, 빈 리스트, 빈 딕셔너리는 유지 (메타데이터 구조 보존)

4. **normalize_text**: 텍스트 정규화
   - 전각 문자를 반각으로 변환
   - 예: `（` → `(`, `）` → `)`, `：` → `:`, `，` → `,`

### 필수 필드 검증

```python
from src.processors.cleaner import DataCleaner

cleaner = DataCleaner()

# 필수 필드 검증
data = {
    "id": "test",
    "type": "statute",
    "title": "제목",
    # "content" 필드 누락
}

valid, errors = cleaner.validate_required_fields(data)

if not valid:
    print("필수 필드 누락:")
    for error in errors:
        print(f"  - {error}")
```

---

## 3. 배치 처리 (BatchProcessor)

### 개요

`BatchProcessor`는 디렉토리 내 여러 파일을 일괄적으로 처리하는 파이프라인입니다. 변환, 정제, 검증을 한 번에 수행합니다.

### 기본 사용법

#### 3.1 단일 파일 처리

```python
from pathlib import Path
from src.processors.pipeline import BatchProcessor

processor = BatchProcessor()

# 단일 파일 처리
success, error = processor.process_file(
    input_path="data/collected/statutes/형법/statute-형법-347.json",
    output_path="data/processed/statutes/statute-형법-347.json",
    doc_type="statute",
    clean=True,      # 정제 수행
    validate=True,   # 검증 수행
)

if success:
    print("✅ 파일 처리 성공")
else:
    print(f"❌ 파일 처리 실패: {error}")
```

#### 3.2 디렉토리 일괄 처리

```python
from pathlib import Path
from src.processors.pipeline import BatchProcessor

processor = BatchProcessor()

# 디렉토리 내 모든 파일 처리
results = processor.process_directory(
    input_dir="data/collected/statutes",
    output_dir="data/processed/statutes",
    doc_type="statute",
    pattern="*.json",           # 파일 패턴
    clean=True,                  # 정제 수행
    validate=True,               # 검증 수행
    remove_duplicates=True,      # 중복 제거
)

# 결과 확인
total = len(results)
success = sum(1 for success, _ in results.values() if success)
failed = total - success

print(f"처리 완료: {success}/{total}")
print(f"실패: {failed}개")

# 각 파일별 결과 확인
for filename, (success, error) in results.items():
    if success:
        print(f"✅ {filename}")
    else:
        print(f"❌ {filename}: {error}")
```

#### 3.3 실제 사용 예제

```python
from pathlib import Path
from src.processors.pipeline import BatchProcessor

# 프로세서 생성
processor = BatchProcessor()

# 1. 법령 데이터 처리
statute_results = processor.process_directory(
    input_dir="data/collected/statutes",
    output_dir="data/processed/statutes",
    doc_type="statute",
    pattern="*.json",
    clean=True,
    validate=True,
    remove_duplicates=True,
)

print(f"\n법령 처리 결과:")
print(f"  성공: {sum(1 for s, _ in statute_results.values() if s)}개")
print(f"  실패: {sum(1 for s, _ in statute_results.values() if not s)}개")

# 2. 판례 데이터 처리
case_results = processor.process_directory(
    input_dir="data/collected/cases",
    output_dir="data/processed/cases",
    doc_type="case",
    pattern="*.json",
    clean=True,
    validate=True,
    remove_duplicates=True,
)

print(f"\n판례 처리 결과:")
print(f"  성공: {sum(1 for s, _ in case_results.values() if s)}개")
print(f"  실패: {sum(1 for s, _ in case_results.values() if not s)}개")
```

### 처리 파이프라인

`BatchProcessor`는 다음 순서로 파일을 처리합니다:

1. **원본 데이터 읽기**: JSON 파일 로드
2. **표준 형식 변환**: `JSONConverter`를 사용하여 표준 형식으로 변환
3. **데이터 정제**: `DataCleaner`를 사용하여 정제
4. **데이터 검증**: `DocumentValidator`를 사용하여 검증
5. **결과 저장**: 정제 및 검증된 데이터를 출력 디렉토리에 저장
6. **중복 제거**: `remove_duplicates=True`인 경우 ID 기준으로 중복 제거

### 파라미터 설명

- `input_dir`: 입력 디렉토리 경로
- `output_dir`: 출력 디렉토리 경로 (자동 생성됨)
- `doc_type`: 문서 타입 (`statute`, `case`, `procedure` 등)
- `pattern`: 파일 패턴 (기본값: `"*.json"`)
- `clean`: 정제 수행 여부 (기본값: `True`)
- `validate`: 검증 수행 여부 (기본값: `True`)
- `remove_duplicates`: 중복 제거 여부 (기본값: `True`)

---

## 4. 벡터화 및 인덱싱 (DocumentIndexer)

### 개요

`DocumentIndexer`는 검증된 JSON 문서를 벡터 데이터베이스(ChromaDB)에 인덱싱하는 도구입니다. 문서를 청크로 분할하고 임베딩을 생성하여 벡터 검색이 가능하도록 합니다.

### 사전 준비

인덱싱을 사용하기 전에 다음이 필요합니다:

1. **환경 변수 설정**
   ```bash
   # .env 파일에 OpenAI API 키 설정
   OPENAI_API_KEY=your-api-key-here
   ```

2. **의존성 설치**
   ```bash
   pip install chromadb openai
   ```

### 기본 사용법

#### 4.1 단일 파일 인덱싱

```python
from pathlib import Path
from src.rag import DocumentIndexer

# 인덱서 생성
indexer = DocumentIndexer(
    collection_name="legal_documents",  # 컬렉션 이름
    chunk_size=1000,                    # 청크 크기 (문자 수)
    chunk_overlap=200,                   # 청크 겹침 (문자 수)
)

# 단일 파일 인덱싱
result = indexer.index_file(
    file_path="data/processed/statutes/statute-형법-347.json",
    chunk=True,  # 청킹 사용 (긴 문서를 여러 청크로 분할)
)

if result["success"]:
    print(f"✅ 인덱싱 성공")
    print(f"   문서 ID: {result['document_id']}")
    print(f"   청크 수: {result['chunks_count']}개")
    print(f"   인덱싱된 ID: {result['indexed_ids']}")
else:
    print(f"❌ 인덱싱 실패: {result['error']}")
```

#### 4.2 디렉토리 일괄 인덱싱

```python
from pathlib import Path
from src.rag import DocumentIndexer

# 인덱서 생성
indexer = DocumentIndexer(
    collection_name="legal_documents",
    chunk_size=1000,
    chunk_overlap=200,
)

# 디렉토리 내 모든 JSON 파일 인덱싱
results = indexer.index_directory(
    directory=Path("data/processed/statutes"),
    pattern="*.json",
    chunk=True,        # 청킹 사용
    recursive=True,    # 하위 디렉토리 재귀 검색
)

print(f"총 {results['total']}건 중 {results['success']}건 성공")
print(f"실패: {results['failed']}건")

# 상세 결과 확인
for detail in results["details"]:
    if isinstance(detail, dict):
        file_path = detail.get("file", "unknown")
        result = detail.get("result", {})
        if result.get("success", False):
            print(f"✅ {file_path}: {result.get('chunks_count', 0)}개 청크")
        else:
            print(f"❌ {file_path}: {result.get('error', '알 수 없는 오류')}")
```

#### 4.3 법률별 폴더 구조 지원

```python
from pathlib import Path
from src.rag import DocumentIndexer

indexer = DocumentIndexer()

# 법률별로 폴더가 나뉘어진 구조도 지원
# data/processed/statutes/
# ├── 형법/
# │   ├── statute-형법-1.json
# │   └── statute-형법-347.json
# ├── 형사소송법/
# │   └── statute-형사소송법-250.json
# └── ...

results = indexer.index_directory(
    directory=Path("data/processed/statutes"),
    pattern="*.json",
    chunk=True,
    recursive=True,  # 하위 디렉토리까지 재귀적으로 검색
)

print(f"인덱싱 완료: {results['success']}/{results['total']}건")
```

#### 4.4 청킹 없이 인덱싱

```python
from src.rag import DocumentIndexer

indexer = DocumentIndexer()

# 청킹 없이 전체 문서를 하나의 벡터로 인덱싱
result = indexer.index_file(
    file_path="data/processed/statutes/statute-형법-347.json",
    chunk=False,  # 청킹 비활성화
)

if result["success"]:
    print(f"✅ 인덱싱 성공 (청크 수: {result['chunks_count']})")
    # chunk=False인 경우 chunks_count는 1
```

### 인덱싱 프로세스

`DocumentIndexer`는 다음 순서로 문서를 인덱싱합니다:

1. **JSON 파일 읽기**: 파일에서 데이터 로드
2. **데이터 검증**: `DocumentValidator`로 스키마 검증
3. **문서 모델 생성**: Pydantic 모델 인스턴스 생성
4. **청킹 (선택적)**: `chunk=True`인 경우 문서를 여러 청크로 분할
   - 기본 청크 크기: 1000자
   - 청크 겹침: 200자
5. **임베딩 생성**: OpenAI API를 사용하여 각 청크의 임베딩 생성
6. **벡터 DB 저장**: ChromaDB에 문서와 임베딩 저장

### 청킹 설정

```python
# 작은 청크 (더 세밀한 검색)
indexer = DocumentIndexer(
    chunk_size=500,    # 500자 단위
    chunk_overlap=100, # 100자 겹침
)

# 큰 청크 (더 넓은 컨텍스트)
indexer = DocumentIndexer(
    chunk_size=2000,   # 2000자 단위
    chunk_overlap=400, # 400자 겹침
)
```

### 실제 사용 시나리오

#### 시나리오 1: 전체 데이터 파이프라인

```python
from pathlib import Path
from src.processors.pipeline import BatchProcessor
from src.rag import DocumentIndexer

# 1단계: 데이터 전처리
processor = BatchProcessor()

# 법령 데이터 전처리
statute_results = processor.process_directory(
    input_dir="data/collected/statutes",
    output_dir="data/processed/statutes",
    doc_type="statute",
    clean=True,
    validate=True,
    remove_duplicates=True,
)

print(f"법령 전처리 완료: {sum(1 for s, _ in statute_results.values() if s)}개")

# 2단계: 벡터 인덱싱
indexer = DocumentIndexer(collection_name="legal_documents")

# 법령 인덱싱
index_results = indexer.index_directory(
    directory=Path("data/processed/statutes"),
    pattern="*.json",
    chunk=True,
    recursive=True,
)

print(f"법령 인덱싱 완료: {index_results['success']}개")
```

#### 시나리오 2: 판례 데이터 인덱싱

```python
from pathlib import Path
from src.rag import DocumentIndexer

indexer = DocumentIndexer(
    collection_name="legal_cases",
    chunk_size=1500,  # 판례는 더 긴 컨텍스트 필요
    chunk_overlap=300,
)

# 판례 데이터 인덱싱
results = indexer.index_directory(
    directory=Path("data/collected/cases"),
    pattern="*.json",
    chunk=True,
    recursive=False,  # 하위 디렉토리 없음
)

print(f"판례 인덱싱 완료:")
print(f"  성공: {results['success']}개")
print(f"  실패: {results['failed']}개")
print(f"  총 청크 수: {sum(r.get('chunks_count', 0) for r in results['details'] if isinstance(r, dict) and r.get('result', {}).get('success', False))}")
```

### 인덱싱 결과 확인

```python
from src.rag import DocumentIndexer

indexer = DocumentIndexer()

results = indexer.index_directory(
    directory=Path("data/processed/statutes"),
    pattern="*.json",
    chunk=True,
    recursive=True,
)

# 상세 결과 분석
total_chunks = 0
failed_files = []

for detail in results["details"]:
    if isinstance(detail, dict):
        file_path = detail.get("file", "unknown")
        result = detail.get("result", {})
        if result.get("success", False):
            total_chunks += result.get("chunks_count", 0)
        else:
            failed_files.append((file_path, result.get("error", "알 수 없는 오류")))

print(f"\n인덱싱 통계:")
print(f"  총 파일: {results['total']}개")
print(f"  성공: {results['success']}개")
print(f"  실패: {results['failed']}개")
print(f"  총 청크 수: {total_chunks}개")

if failed_files:
    print(f"\n실패한 파일:")
    for file_path, error in failed_files:
        print(f"  - {file_path}: {error}")
```

---

## 전체 워크플로우 예제

다음은 수집된 데이터를 전처리하고 인덱싱하는 전체 워크플로우입니다:

### 방법 1: 스크립트 사용 (가장 간단)

```bash
# 법령 데이터 전체 처리
python scripts/process_and_index.py \
    --input-dir "data/collected/statutes" \
    --doc-type "statute"

# 판례 데이터 전체 처리
python scripts/process_and_index.py \
    --input-dir "data/collected/cases" \
    --doc-type "case"
```

### 방법 2: Python 코드로 직접 실행

```python
# process_all_data.py 파일 생성
from pathlib import Path
from src.processors.pipeline import BatchProcessor
from src.rag import DocumentIndexer

def process_and_index_all_data():
    """전체 데이터 처리 및 인덱싱"""
    
    processor = BatchProcessor()
    indexer = DocumentIndexer(collection_name="legal_documents")
    
    # 처리할 문서 타입들
    doc_types = {
        "statute": "data/collected/statutes",
        "case": "data/collected/cases",
        "procedure": "data/collected/procedures",
    }
    
    # 1단계: 전처리
    print("=" * 60)
    print("1단계: 데이터 전처리")
    print("=" * 60)
    
    for doc_type, input_dir in doc_types.items():
        output_dir = f"data/processed/{doc_type}"
        
        print(f"\n[{doc_type}] 전처리 중...")
        results = processor.process_directory(
            input_dir=input_dir,
            output_dir=output_dir,
            doc_type=doc_type,
            clean=True,
            validate=True,
            remove_duplicates=True,
        )
        
        success_count = sum(1 for s, _ in results.values() if s)
        failed_count = len(results) - success_count
        print(f"  ✅ 성공: {success_count}개")
        print(f"  ❌ 실패: {failed_count}개")
    
    # 2단계: 인덱싱
    print("\n" + "=" * 60)
    print("2단계: 벡터 인덱싱")
    print("=" * 60)
    
    for doc_type in doc_types.keys():
        processed_dir = Path(f"data/processed/{doc_type}")
        
        if not processed_dir.exists():
            print(f"\n[{doc_type}] 처리된 데이터가 없습니다. 건너뜁니다.")
            continue
        
        print(f"\n[{doc_type}] 인덱싱 중...")
        results = indexer.index_directory(
            directory=processed_dir,
            pattern="*.json",
            chunk=True,
            recursive=True,
        )
        
        print(f"  ✅ 성공: {results['success']}개")
        print(f"  ❌ 실패: {results['failed']}개")
    
    print("\n" + "=" * 60)
    print("전체 프로세스 완료!")
    print("=" * 60)

# 실행
if __name__ == "__main__":
    process_and_index_all_data()
```

---

## 주의사항

1. **API 키 설정**: `DocumentIndexer`는 OpenAI API를 사용하므로 `.env` 파일에 `OPENAI_API_KEY`를 설정해야 합니다.

2. **비용 고려**: 대량의 문서를 인덱싱할 때는 OpenAI API 사용 비용이 발생합니다. 청크 수가 많을수록 비용이 증가합니다.

3. **청킹 전략**: 
   - 짧은 문서(법령 조문 등): `chunk=False` 또는 작은 `chunk_size`
   - 긴 문서(판례 등): `chunk=True` 및 적절한 `chunk_size`

4. **중복 제거**: `BatchProcessor`의 `remove_duplicates=True`는 ID 기준으로 중복을 제거합니다. 같은 ID를 가진 문서가 여러 개 있으면 첫 번째 것만 유지됩니다.

5. **에러 처리**: 각 단계에서 실패한 파일은 로그에 기록되므로, 배치 처리 후 실패한 파일들을 확인하고 수동으로 처리해야 할 수 있습니다.

---

## 문제 해결

### 인덱싱 실패 시

```python
# 상세한 에러 정보 확인
results = indexer.index_directory(...)

for detail in results["details"]:
    if isinstance(detail, dict):
        file_path = detail.get("file", "unknown")
        result = detail.get("result", {})
        if not result.get("success", False):
            print(f"파일: {file_path}")
            print(f"오류: {result.get('error', '알 수 없는 오류')}")
```

### 검증 실패 시

```python
# 검증 오류 상세 확인
validator = DocumentValidator()
success, model = validator.validate(data)

if not success:
    for error in validator.get_errors():
        print(f"오류: {error}")
```

### 메모리 부족 시

```python
# 청크 크기를 줄여서 처리
indexer = DocumentIndexer(
    chunk_size=500,  # 더 작은 청크
    chunk_overlap=100,
)
```

---

## 실행 명령어 요약

### 가장 간단한 방법

```bash
# 법령 데이터 처리 및 인덱싱
python scripts/process_and_index.py --input-dir "data/collected/statutes" --doc-type "statute"

# 판례 데이터 처리 및 인덱싱
python scripts/process_and_index.py --input-dir "data/collected/cases" --doc-type "case"
```

### 옵션 사용

```bash
# 전처리만 수행
python scripts/process_and_index.py --input-dir "data/collected/statutes" --doc-type "statute" --skip-index

# 인덱싱만 수행 (이미 전처리된 경우)
python scripts/process_and_index.py --input-dir "data/processed/statutes" --doc-type "statute" --skip-process

# 청킹 없이 인덱싱
python scripts/process_and_index.py --input-dir "data/processed/statutes" --doc-type "statute" --skip-process --no-chunk

# 다른 컬렉션 이름 사용
python scripts/process_and_index.py --input-dir "data/collected/statutes" --doc-type "statute" --collection-name "my_collection"
```

이 가이드를 참고하여 데이터 전처리 및 인덱싱을 수행하세요!
