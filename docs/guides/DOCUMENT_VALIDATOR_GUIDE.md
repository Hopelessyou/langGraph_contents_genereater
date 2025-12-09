# DocumentValidator 사용 가이드

`DocumentValidator`는 법률 문서 JSON 데이터의 스키마를 검증하는 도구입니다. Pydantic 모델을 사용하여 타입 안전성을 보장하고, 문서 타입별 필수 필드와 데이터 형식을 자동으로 검증합니다.

---

## 목차

1. [개요](#개요)
2. [기본 사용법](#기본-사용법)
3. [고급 사용법](#고급-사용법)
4. [검증 항목 상세](#검증-항목-상세)
5. [에러 처리](#에러-처리)
6. [실전 예제](#실전-예제)
7. [문제 해결](#문제-해결)

---

## 개요

### DocumentValidator란?

`DocumentValidator`는 다음과 같은 기능을 제공합니다:

- **스키마 검증**: JSON 데이터가 올바른 문서 타입 스키마를 따르는지 검증
- **타입 안전성**: Pydantic 모델을 사용하여 타입 안전성 보장
- **필수 필드 검증**: 문서 타입별 필수 필드 존재 여부 확인
- **메타데이터 검증**: 문서 타입별 필수 메타데이터 필드 확인
- **에러 리포트**: 검증 실패 시 상세한 에러 메시지 제공

### 지원하는 문서 타입

| 문서 타입 | 모델 클래스 | 설명 |
|---------|-----------|------|
| `statute` | `StatuteModel` | 법령 문서 |
| `case` | `CaseModel` | 판례 문서 |
| `procedure` | `ProcedureModel` | 절차 매뉴얼 |
| `template` | `TemplateModel` | 템플릿 문서 |
| `manual` | `ManualModel` | 실무 매뉴얼 |
| `case_type` | `CaseTypeModel` | 사건 유형 |
| `sentencing_guideline` | `SentencingGuidelineModel` | 양형 가이드라인 |
| `faq` | `FAQModel` | FAQ 문서 |
| `keyword_mapping` | `KeywordMappingModel` | 키워드 맵핑 |
| `style_issue` | `StyleIssueModel` | 스타일 문제 |

---

## 기본 사용법

### 1. Import 및 초기화

```python
from src.processors.validator import DocumentValidator
from pathlib import Path

# 검증기 생성
validator = DocumentValidator()
```

### 2. 단일 JSON 데이터 검증

#### 2.1 딕셔너리 데이터 검증

```python
# 검증할 JSON 데이터 (딕셔너리 형식)
json_data = {
    "id": "statute-형법-347",
    "category": "형사",
    "sub_category": "사기",
    "type": "statute",
    "title": "형법 제347조(사기)",
    "content": "① 사람을 기망하여 재물의 교부를 받거나 재산상의 이익을 취득한 자는 10년 이하의 징역 또는 2천만원 이하의 벌금에 처한다.",
    "metadata": {
        "law_name": "형법",
        "article_number": "347",
        "topics": ["사기", "재물"],
        "source": "법제처",
        "updated_at": "2024-01-01",
    },
}

# 검증 수행
success, model = validator.validate(json_data)

if success:
    print(f"✅ 검증 성공!")
    print(f"   문서 타입: {model.type}")
    print(f"   문서 ID: {model.id}")
    print(f"   제목: {model.title}")
    print(f"   카테고리: {model.category} > {model.sub_category}")
    
    # Pydantic 모델 인스턴스이므로 타입 안전하게 접근 가능
    if hasattr(model, 'metadata') and model.metadata:
        print(f"   법률명: {model.metadata.get('law_name', 'N/A')}")
        print(f"   조문번호: {model.metadata.get('article_number', 'N/A')}")
else:
    print(f"❌ 검증 실패:")
    for error in validator.get_errors():
        print(f"   - {error}")
```

#### 2.2 JSON 파일 검증

```python
from pathlib import Path

# 파일 경로 지정
file_path = Path("data/collected/statutes/형법/statute-형법-347.json")

# 파일 검증
success, model = validator.validate_file(file_path)

if success:
    print(f"✅ 파일 검증 성공: {file_path.name}")
    print(f"   문서 타입: {model.type}")
    print(f"   문서 ID: {model.id}")
else:
    print(f"❌ 파일 검증 실패: {file_path.name}")
    for error in validator.get_errors():
        print(f"   - {error}")
```

### 3. 여러 문서 일괄 검증

#### 3.1 딕셔너리 리스트 검증

```python
import json
from pathlib import Path

# 여러 JSON 데이터 준비
data_list = [
    {
        "id": "statute-형법-347",
        "type": "statute",
        "category": "형사",
        "sub_category": "사기",
        "title": "형법 제347조",
        "content": "조문 내용...",
        "metadata": {"law_name": "형법", "article_number": "347"},
    },
    {
        "id": "case-2010도12928",
        "type": "case",
        "category": "형사",
        "sub_category": "사기",
        "title": "대법원 2010도12928 판결",
        "content": "판례 내용...",
        "metadata": {"court": "대법원", "case_number": "2010도12928"},
    },
]

# 일괄 검증
results = validator.validate_batch(data_list)

# 결과 확인
success_count = 0
fail_count = 0

for doc_id, (success, model) in results.items():
    if success:
        success_count += 1
        print(f"✅ {doc_id}: 검증 성공 ({model.type})")
    else:
        fail_count += 1
        print(f"❌ {doc_id}: 검증 실패")
        # 각 문서의 에러는 마지막 검증 결과에 저장됨
        for error in validator.get_errors():
            print(f"   - {error}")

print(f"\n📊 검증 결과: 성공 {success_count}개, 실패 {fail_count}개")
```

#### 3.2 디렉토리 내 모든 JSON 파일 검증

```python
from pathlib import Path
import json

validator = DocumentValidator()

# 디렉토리 내 모든 JSON 파일 찾기
json_files = list(Path("data/collected/statutes").rglob("*.json"))

print(f"총 {len(json_files)}개 파일 검증 시작...\n")

success_count = 0
fail_count = 0
failed_files = []

for file_path in json_files:
    success, model = validator.validate_file(file_path)
    
    if success:
        success_count += 1
        print(f"✅ {file_path.name}")
    else:
        fail_count += 1
        failed_files.append((file_path, validator.get_errors()))
        print(f"❌ {file_path.name}")
        for error in validator.get_errors():
            print(f"   - {error}")

print(f"\n📊 검증 결과:")
print(f"   ✅ 성공: {success_count}개")
print(f"   ❌ 실패: {fail_count}개")

if failed_files:
    print(f"\n⚠️  실패한 파일 목록:")
    for file_path, errors in failed_files:
        print(f"   - {file_path}")
        for error in errors:
            print(f"     → {error}")
```

---

## 고급 사용법

### 1. 검증 결과 활용

검증 성공 시 반환되는 `model`은 Pydantic 모델 인스턴스이므로, 타입 안전하게 데이터에 접근할 수 있습니다:

```python
success, model = validator.validate(json_data)

if success:
    # 기본 필드 접근
    print(f"ID: {model.id}")
    print(f"타입: {model.type}")
    print(f"제목: {model.title}")
    print(f"내용: {model.content[:100]}...")  # 처음 100자만
    
    # 메타데이터 접근
    if model.metadata:
        metadata = model.metadata
        
        # 타입별 특화 메타데이터 접근
        if model.type == "statute":
            print(f"법률명: {metadata.get('law_name')}")
            print(f"조문번호: {metadata.get('article_number')}")
        elif model.type == "case":
            print(f"법원: {metadata.get('court')}")
            print(f"사건번호: {metadata.get('case_number')}")
            print(f"판결일: {metadata.get('judgment_date')}")
    
    # 모델을 딕셔너리로 변환
    model_dict = model.model_dump()
    
    # 모델을 JSON 문자열로 변환
    model_json = model.model_dump_json(indent=2, ensure_ascii=False)
```

### 2. 검증 전 데이터 전처리

검증 전에 데이터를 전처리할 수 있습니다:

```python
def preprocess_data(data: dict) -> dict:
    """검증 전 데이터 전처리"""
    # 1. 필수 필드 기본값 설정
    if "category" not in data:
        data["category"] = "기타"
    if "sub_category" not in data:
        data["sub_category"] = ""
    
    # 2. 문자열 필드 공백 제거
    for key in ["title", "content"]:
        if key in data and isinstance(data[key], str):
            data[key] = data[key].strip()
    
    # 3. 메타데이터 기본값 설정
    if "metadata" not in data:
        data["metadata"] = {}
    
    return data

# 전처리 후 검증
json_data = preprocess_data(json_data)
success, model = validator.validate(json_data)
```

### 3. 커스텀 검증 로직 추가

`DocumentValidator`를 상속하여 커스텀 검증 로직을 추가할 수 있습니다:

```python
from src.processors.validator import DocumentValidator
from typing import Any, Dict, Optional
from ..models import BaseDocument

class CustomDocumentValidator(DocumentValidator):
    """커스텀 문서 검증기"""
    
    def validate(self, data: Dict[str, Any]) -> tuple[bool, Optional[BaseDocument]]:
        # 기본 검증 수행
        success, model = super().validate(data)
        
        if not success:
            return False, None
        
        # 커스텀 검증 로직 추가
        custom_errors = self._custom_validation(model)
        if custom_errors:
            self.errors.extend(custom_errors)
            return False, None
        
        return True, model
    
    def _custom_validation(self, model: BaseDocument) -> list[str]:
        """커스텀 검증 로직"""
        errors = []
        
        # 예: 제목 길이 검증
        if len(model.title) < 5:
            errors.append("제목이 너무 짧습니다 (최소 5자 이상)")
        
        # 예: 내용 길이 검증
        if isinstance(model.content, str) and len(model.content) < 10:
            errors.append("내용이 너무 짧습니다 (최소 10자 이상)")
        
        # 예: 특정 키워드 포함 여부 검증
        if model.type == "statute" and "조" not in model.title:
            errors.append("법령 제목에 '조'가 포함되어야 합니다")
        
        return errors

# 사용 예제
custom_validator = CustomDocumentValidator()
success, model = custom_validator.validate(json_data)
```

### 4. 편의 함수 사용

간단한 검증이 필요한 경우 편의 함수를 사용할 수 있습니다:

```python
from src.processors.validator import validate_document

# 편의 함수 사용
success, model, errors = validate_document(json_data)

if success:
    print(f"✅ 검증 성공: {model.id}")
else:
    print(f"❌ 검증 실패:")
    for error in errors:
        print(f"   - {error}")
```

---

## 검증 항목 상세

### 1. 기본 구조 검증

- ✅ 데이터가 딕셔너리(`dict`) 형식인지 확인
- ✅ `type` 필드 존재 여부 확인
- ✅ 지원하는 문서 타입인지 확인

**에러 예시:**
```
❌ 데이터가 딕셔너리 형식이 아닙니다.
❌ 'type' 필드가 없습니다.
❌ 지원하지 않는 문서 타입: invalid_type
```

### 2. 타입별 스키마 검증

각 문서 타입은 고유한 Pydantic 모델로 검증됩니다:

#### 2.1 법령 (statute)

**필수 필드:**
- `id`: 문서 고유 ID (문자열)
- `type`: "statute" (문자열)
- `category`: 카테고리 (문자열, 예: "형사")
- `sub_category`: 하위 카테고리 (문자열, 예: "사기")
- `title`: 제목 (문자열)
- `content`: 내용 (문자열 또는 리스트)
- `metadata`: 메타데이터 (딕셔너리)

**메타데이터 필수 필드:**
- `law_name`: 법률명 (문자열)
- `article_number`: 조문번호 (문자열)

**예제:**
```json
{
  "id": "statute-형법-347",
  "type": "statute",
  "category": "형사",
  "sub_category": "사기",
  "title": "형법 제347조(사기)",
  "content": "① 사람을 기망하여...",
  "metadata": {
    "law_name": "형법",
    "article_number": "347",
    "topics": ["사기"],
    "source": "법제처",
    "updated_at": "2024-01-01"
  }
}
```

#### 2.2 판례 (case)

**필수 필드:**
- `id`: 문서 고유 ID (문자열)
- `type`: "case" (문자열)
- `category`: 카테고리 (문자열)
- `sub_category`: 하위 카테고리 (문자열)
- `title`: 제목 (문자열)
- `content`: 내용 (문자열)
- `metadata`: 메타데이터 (딕셔너리)

**메타데이터 필수 필드:**
- `court`: 법원명 (문자열)
- `year`: 판결 연도 (정수)

**예제:**
```json
{
  "id": "case-2010도12928",
  "type": "case",
  "category": "형사",
  "sub_category": "사기",
  "title": "대법원 2010도12928 판결",
  "content": "【사건 개요】\n피고인은...",
  "metadata": {
    "court": "대법원",
    "year": 2010,
    "case_number": "2010도12928",
    "judgment_date": "2010-12-09",
    "keywords": ["사기", "기망"],
    "holding": "판결 요지..."
  }
}
```

### 3. 필수 필드 검증

각 문서 타입별로 필수 필드가 자동으로 검증됩니다:

- `id`: 반드시 존재해야 함
- `type`: 반드시 존재해야 하며, 지원하는 타입이어야 함
- `title`: 반드시 존재해야 함
- `content`: 반드시 존재해야 함
- `category`: 반드시 존재해야 함

**에러 예시:**
```
❌ 검증 실패: Field required [type=missing, input={'id': 'test'}, input_type=dict]
```

### 4. 데이터 타입 검증

Pydantic 모델이 자동으로 데이터 타입을 검증합니다:

- `id`: 문자열 (`str`)
- `type`: 문자열 (`str`)
- `category`: 문자열 (`str`)
- `sub_category`: 문자열 (`str`)
- `title`: 문자열 (`str`)
- `content`: 문자열 (`str`) 또는 리스트 (`List[str]`)
- `metadata`: 딕셔너리 (`Dict[str, Any]`)

**에러 예시:**
```
❌ 검증 실패: Input should be a valid string [type=string_type, input_value=123, input_type=int]
```

### 5. 메타데이터 검증

문서 타입별로 필수 메타데이터 필드가 검증됩니다:

- **법령 (statute)**: `law_name`, `article_number`
- **판례 (case)**: `court`, `year`
- **절차 (procedure)**: `procedure_type`
- 기타 타입별 필수 메타데이터

---

## 에러 처리

### 1. 에러 확인

검증 실패 시 `get_errors()` 메서드로 에러 목록을 확인할 수 있습니다:

```python
success, model = validator.validate(json_data)

if not success:
    errors = validator.get_errors()
    print(f"검증 실패: {len(errors)}개 에러 발견")
    for i, error in enumerate(errors, 1):
        print(f"{i}. {error}")
```

### 2. 일반적인 에러 유형

#### 2.1 필수 필드 누락

```python
# 에러 발생 데이터
data = {
    "id": "test",
    # "type" 필드 누락
}

success, model = validator.validate(data)
# ❌ 검증 실패: 'type' 필드가 없습니다.
```

#### 2.2 잘못된 문서 타입

```python
# 에러 발생 데이터
data = {
    "id": "test",
    "type": "invalid_type",  # 지원하지 않는 타입
    "title": "Test",
    "content": "Content",
}

success, model = validator.validate(data)
# ❌ 검증 실패: 지원하지 않는 문서 타입: invalid_type
```

#### 2.3 타입 불일치

```python
# 에러 발생 데이터
data = {
    "id": 123,  # 문자열이어야 함
    "type": "statute",
    "title": "Test",
    "content": "Content",
}

success, model = validator.validate(data)
# ❌ 검증 실패: Input should be a valid string [type=string_type, input_value=123, input_type=int]
```

#### 2.4 메타데이터 필수 필드 누락

```python
# 에러 발생 데이터
data = {
    "id": "statute-test",
    "type": "statute",
    "category": "형사",
    "sub_category": "사기",
    "title": "형법 제347조",
    "content": "Content",
    "metadata": {
        # "law_name" 필드 누락
        "article_number": "347",
    },
}

success, model = validator.validate(data)
# ❌ 검증 실패: Field required [type=missing, field_name=law_name, ...]
```

### 3. 에러 처리 패턴

#### 3.1 에러 로깅

```python
import logging

logger = logging.getLogger(__name__)

success, model = validator.validate(json_data)

if not success:
    errors = validator.get_errors()
    logger.error(f"문서 검증 실패: {json_data.get('id', 'unknown')}")
    for error in errors:
        logger.error(f"  - {error}")
```

#### 3.2 에러 수집 및 리포트

```python
def validate_directory(directory: Path) -> dict:
    """디렉토리 내 모든 파일 검증 및 리포트 생성"""
    validator = DocumentValidator()
    
    json_files = list(directory.rglob("*.json"))
    results = {
        "total": len(json_files),
        "success": 0,
        "failed": 0,
        "errors": [],
    }
    
    for file_path in json_files:
        success, model = validator.validate_file(file_path)
        
        if success:
            results["success"] += 1
        else:
            results["failed"] += 1
            results["errors"].append({
                "file": str(file_path),
                "errors": validator.get_errors(),
            })
    
    return results

# 사용 예제
results = validate_directory(Path("data/collected/statutes"))
print(f"검증 결과: {results['success']}/{results['total']} 성공")
if results["errors"]:
    print(f"\n실패한 파일:")
    for error_info in results["errors"]:
        print(f"  - {error_info['file']}")
        for error in error_info["errors"]:
            print(f"    → {error}")
```

---

## 실전 예제

### 예제 1: 수집된 데이터 검증 스크립트

```python
#!/usr/bin/env python3
"""수집된 데이터 검증 스크립트"""

from pathlib import Path
from src.processors.validator import DocumentValidator
import json

def main():
    """메인 함수"""
    validator = DocumentValidator()
    
    # 검증할 디렉토리
    input_dir = Path("data/collected")
    
    # 모든 JSON 파일 찾기
    json_files = list(input_dir.rglob("*.json"))
    
    print(f"📋 총 {len(json_files)}개 파일 검증 시작...\n")
    
    success_count = 0
    fail_count = 0
    failed_files = []
    
    for file_path in json_files:
        success, model = validator.validate_file(file_path)
        
        if success:
            success_count += 1
            print(f"✅ {file_path.relative_to(input_dir)}")
        else:
            fail_count += 1
            errors = validator.get_errors()
            failed_files.append((file_path, errors))
            print(f"❌ {file_path.relative_to(input_dir)}")
            for error in errors:
                print(f"   - {error}")
    
    # 결과 리포트
    print(f"\n{'='*60}")
    print(f"📊 검증 결과 요약")
    print(f"{'='*60}")
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print(f"📁 총 파일: {len(json_files)}개")
    
    if failed_files:
        print(f"\n⚠️  실패한 파일 상세:")
        for file_path, errors in failed_files:
            print(f"\n📄 {file_path.relative_to(input_dir)}")
            for error in errors:
                print(f"   → {error}")

if __name__ == "__main__":
    main()
```

### 예제 2: 검증 후 데이터 전처리 파이프라인

```python
from pathlib import Path
from src.processors.validator import DocumentValidator
from src.processors.cleaner import DataCleaner
import json

def process_and_validate(input_dir: Path, output_dir: Path):
    """검증 및 전처리 파이프라인"""
    validator = DocumentValidator()
    cleaner = DataCleaner()
    
    json_files = list(input_dir.rglob("*.json"))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    fail_count = 0
    
    for file_path in json_files:
        # 1. 검증
        success, model = validator.validate_file(file_path)
        
        if not success:
            print(f"❌ 검증 실패: {file_path.name}")
            for error in validator.get_errors():
                print(f"   - {error}")
            fail_count += 1
            continue
        
        # 2. 정제
        cleaned_data = cleaner.clean(model.model_dump())
        
        # 3. 재검증 (정제 후)
        success, cleaned_model = validator.validate(cleaned_data)
        
        if not success:
            print(f"⚠️  정제 후 검증 실패: {file_path.name}")
            fail_count += 1
            continue
        
        # 4. 저장
        output_file = output_dir / file_path.name
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(cleaned_model.model_dump(), f, ensure_ascii=False, indent=2)
        
        success_count += 1
        print(f"✅ 처리 완료: {file_path.name}")
    
    print(f"\n📊 처리 결과: 성공 {success_count}개, 실패 {fail_count}개")

# 사용 예제
process_and_validate(
    Path("data/collected/statutes"),
    Path("data/processed/statutes"),
)
```

### 예제 3: API 엔드포인트에서 사용

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.processors.validator import DocumentValidator

router = APIRouter()
validator = DocumentValidator()

class DocumentRequest(BaseModel):
    document: dict

@router.post("/validate")
async def validate_document_endpoint(request: DocumentRequest):
    """문서 검증 API 엔드포인트"""
    success, model = validator.validate(request.document)
    
    if success:
        return {
            "success": True,
            "document_id": model.id,
            "document_type": model.type,
            "message": "검증 성공",
        }
    else:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "errors": validator.get_errors(),
            }
        )
```

---

## 문제 해결

### Q1: "지원하지 않는 문서 타입" 에러가 발생합니다

**원인:** `type` 필드의 값이 지원하는 문서 타입 목록에 없습니다.

**해결 방법:**
1. `type` 필드 값 확인:
   ```python
   print(f"문서 타입: {data.get('type')}")
   ```
2. 지원하는 타입 확인:
   ```python
   from src.processors.validator import DocumentValidator
   print(f"지원하는 타입: {list(DocumentValidator.TYPE_MODEL_MAP.keys())}")
   ```
3. 올바른 타입으로 수정:
   ```python
   data["type"] = "statute"  # 올바른 타입으로 변경
   ```

### Q2: "Field required" 에러가 발생합니다

**원인:** 필수 필드가 누락되었습니다.

**해결 방법:**
1. 에러 메시지에서 누락된 필드 확인
2. 필수 필드 추가:
   ```python
   # 예: "category" 필드 누락
   data["category"] = "형사"  # 필수 필드 추가
   ```

### Q3: "Input should be a valid string" 에러가 발생합니다

**원인:** 필드의 데이터 타입이 올바르지 않습니다.

**해결 방법:**
1. 에러 메시지에서 문제가 된 필드 확인
2. 올바른 타입으로 변환:
   ```python
   # 예: id가 숫자인 경우
   data["id"] = str(data["id"])  # 문자열로 변환
   ```

### Q4: 메타데이터 검증 실패

**원인:** 문서 타입별 필수 메타데이터 필드가 누락되었습니다.

**해결 방법:**
1. 문서 타입별 필수 메타데이터 확인:
   - **법령 (statute)**: `law_name`, `article_number`
   - **판례 (case)**: `court`, `year`
2. 누락된 메타데이터 추가:
   ```python
   if "metadata" not in data:
       data["metadata"] = {}
   
   if data["type"] == "statute":
       data["metadata"]["law_name"] = "형법"
       data["metadata"]["article_number"] = "347"
   ```

### Q5: 검증은 성공했지만 데이터가 비어있습니다

**원인:** 필수 필드는 있지만 내용이 비어있을 수 있습니다.

**해결 방법:**
1. 내용 확인:
   ```python
   if success and model:
       if not model.content or len(model.content.strip()) == 0:
           print("⚠️  내용이 비어있습니다")
   ```
2. 데이터 정제 도구 사용:
   ```python
   from src.processors.cleaner import DataCleaner
   cleaner = DataCleaner()
   cleaned_data = cleaner.clean(model.model_dump())
   ```

---

## 참고 자료

- [RAG 데이터 처리 가이드](./RAG_DATA_PROCESSING_GUIDE.md)
- [RAG 데이터 구축 가이드](./RAG_DATA_BUILD_GUIDE.md)
- [Pydantic 공식 문서](https://docs.pydantic.dev/)

---

**문의 및 버그 리포트:** GitHub Issues를 통해 문의해주세요.

