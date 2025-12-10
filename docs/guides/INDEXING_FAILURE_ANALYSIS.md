# 인덱싱 실패 원인 분석

## 개요

인덱싱 과정에서 발생한 두 가지 주요 오류에 대한 원인 분석 및 해결 방안입니다.

## 오류 1: 빈 임베딩 오류

### 오류 메시지
```
Expected Embeddings to be non-empty list or numpy array, got [] in add.
```

### 원인 분석

#### 1. 빈 텍스트 청크 생성
`src/rag/indexer.py`의 `index_document` 메서드에서:

```python
# 임베딩 생성 (비동기 메서드를 동기적으로 실행)
texts = [chunk["text"] for chunk in chunks]  # 빈 텍스트 필터링 없음
embeddings = await self.embedding_generator.embed_texts(texts)
```

**문제점:**
- 빈 텍스트(`""`) 또는 공백만 있는 텍스트가 포함될 수 있음
- OpenAI Embedding API에 빈 텍스트를 전달하면 빈 리스트 `[]`를 반환할 수 있음
- ChromaDB는 빈 임베딩 리스트를 허용하지 않음

#### 2. 청킹 과정에서의 빈 청크 생성 가능성

**`src/rag/chunker.py`의 문제점:**

1. **`_chunk_default` 메서드 (378-415줄):**
   ```python
   chunks.append({
       "text": chunk_text.strip(),  # 빈 문자열일 수 있음
       "metadata": {...}
   })
   ```
   - 빈 텍스트 체크 없이 청크를 추가
   - 텍스트가 모두 공백인 경우 빈 문자열이 생성됨

2. **`_chunk_statute` 메서드:**
   - `if not article_text: continue` 체크가 있지만, 일부 엣지 케이스에서 빈 청크가 생성될 수 있음

3. **`chunk=False`인 경우:**
   ```python
   if isinstance(document.content, str):
       text = document.content  # 빈 문자열일 수 있음
   ```
   - 문서 내용이 빈 문자열이거나 공백만 있는 경우 빈 청크 생성

#### 3. OpenAI Embedding API의 동작
- 빈 문자열이나 공백만 있는 텍스트에 대해 빈 리스트를 반환하거나 오류를 발생시킬 수 있음

### 해결 방안

#### 방안 1: 빈 텍스트 필터링 (권장)

`src/rag/indexer.py`의 `index_document` 메서드 수정:

```python
# 임베딩 생성 전 빈 텍스트 필터링
texts = []
valid_chunk_indices = []
for i, chunk in enumerate(chunks):
    text = chunk["text"].strip() if isinstance(chunk["text"], str) else str(chunk["text"]).strip()
    if text:  # 빈 문자열이 아닌 경우만 포함
        texts.append(text)
        valid_chunk_indices.append(i)

if not texts:
    logger.warning(f"문서 {document.id}에 유효한 텍스트 청크가 없습니다.")
    return {
        "success": False,
        "document_id": document.id,
        "error": "유효한 텍스트 청크가 없습니다.",
    }

# 유효한 청크만 사용
embeddings = await self.embedding_generator.embed_texts(texts)
valid_chunks = [chunks[i] for i in valid_chunk_indices]
```

#### 방안 2: 청킹 단계에서 빈 청크 제거

`src/rag/chunker.py`의 모든 청킹 메서드에서:

```python
# 빈 청크 제거
chunks = [chunk for chunk in chunks if chunk["text"].strip()]
```

#### 방안 3: 임베딩 생성 후 검증

```python
# 임베딩 생성 후 빈 임베딩 필터링
valid_embeddings = []
valid_chunks = []
for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
    if embedding and len(embedding) > 0:  # 빈 임베딩 제외
        valid_embeddings.append(embedding)
        valid_chunks.append(chunk)
    else:
        logger.warning(f"청크 {i}의 임베딩이 비어있습니다: {chunk.get('text', '')[:50]}")
```

---

## 오류 2: JSON 파싱 오류 (Invalid Control Character)

### 오류 메시지
```
Invalid control character at: line 7 column 70 (char 229)
```

### 원인 분석

#### 문제 파일
`data/collected/statutes/특정경제범죄 가중처벌 등에 관한 법률/statute-특정경제범죄 가중처벌 등에 관한 법률-3.json`

#### 문제 내용
```json
{
  "content": "① 「형법」 제347조(사기), 제347조의2(컴퓨터등 사용사기), 제350조(공갈), 제350조의
2(특수공갈), 제351조(제347조, 제347조의2, 제350조 및 제350조의2의 상습범만 해당한다), 제355조(횡령ㆍ배임) 또
는 제356조(업무상의 횡령과 배임)의 죄를 범한 사람은..."
}
```

**문제점:**
- JSON 문자열 내에 **리터럴 개행 문자**가 포함되어 있음
- JSON 스펙에 따르면 문자열 내 제어 문자(control character)는 이스케이프되어야 함
- `\n`, `\r`, `\t` 등은 `\\n`, `\\r`, `\\t`로 이스케이프되어야 함

#### JSON 파서의 동작
- Python의 `json.load()`는 기본적으로 제어 문자를 허용하지 않음
- `strict=False` 옵션을 사용하면 일부 제어 문자를 허용하지만, 완전한 해결책은 아님

### 해결 방안

#### 방안 1: JSON 파일 수정 (근본 해결)

문제가 있는 JSON 파일들을 수정하여 제어 문자를 이스케이프:

```python
import json
import re
from pathlib import Path

def fix_json_control_chars(file_path: Path):
    """JSON 파일의 제어 문자를 이스케이프"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 제어 문자를 이스케이프
    # \n -> \\n, \r -> \\r, \t -> \\t
    content = content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
```

#### 방안 2: JSON 파싱 시 제어 문자 처리 (임시 해결)

`src/rag/indexer.py`의 `index_file` 메서드 수정:

```python
def index_file(self, file_path: Path | str, chunk: bool = True) -> Dict[str, Any]:
    file_path = Path(file_path)
    
    if not file_path.exists():
        return {
            "success": False,
            "error": f"파일이 존재하지 않습니다: {file_path}",
        }
    
    try:
        # JSON 파일 읽기 (제어 문자 처리)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 제어 문자를 이스케이프된 형태로 변환
        # 단, 이미 이스케이프된 것은 그대로 유지
        import re
        # 문자열 내부의 제어 문자만 처리 (따옴표 안의 내용)
        def escape_control_chars(match):
            text = match.group(0)
            # 이미 이스케이프된 것은 제외
            if '\\n' in text or '\\r' in text or '\\t' in text:
                return text
            # 제어 문자 이스케이프
            text = text.replace('\n', '\\n')
            text = text.replace('\r', '\\r')
            text = text.replace('\t', '\\t')
            return text
        
        # 간단한 방법: strict=False 옵션 사용
        try:
            data = json.loads(content, strict=False)
        except json.JSONDecodeError:
            # strict=False로도 안 되면 수동 처리
            # 문자열 값 내의 제어 문자를 이스케이프
            content = re.sub(r'(?<!\\)\n', '\\n', content)
            content = re.sub(r'(?<!\\)\r', '\\r', content)
            content = re.sub(r'(?<!\\)\t', '\\t', content)
            data = json.loads(content)
        
        # 검증
        success, model = self.validator.validate(data)
        if not success:
            return {
                "success": False,
                "error": f"검증 실패: {', '.join(self.validator.get_errors())}",
            }
        
        # 인덱싱
        return self.index_document(model, chunk=chunk)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON 파싱 실패: {file_path} - {str(e)}")
        return {
            "success": False,
            "error": f"JSON 파싱 오류: {str(e)}",
        }
    except Exception as e:
        logger.error(f"파일 인덱싱 실패: {file_path} - {str(e)}")
        return {
            "success": False,
            "error": str(e),
        }
```

#### 방안 3: 데이터 수집 단계에서 예방

JSON 파일을 생성하는 단계에서 제어 문자를 올바르게 이스케이프:

```python
import json

# JSON 저장 시 ensure_ascii=False와 함께 사용
json.dumps(data, ensure_ascii=False, indent=2)
# 이렇게 하면 문자열 내의 제어 문자가 자동으로 이스케이프됨
```

---

## 권장 해결 순서

1. **즉시 적용 (임시 해결):**
   - `indexer.py`에 빈 텍스트 필터링 추가
   - `index_file` 메서드에 JSON 제어 문자 처리 추가

2. **근본 해결:**
   - 문제가 있는 JSON 파일들을 일괄 수정
   - 데이터 수집/전처리 파이프라인에서 제어 문자 이스케이프 보장
   - 청킹 로직에서 빈 청크 생성 방지

3. **검증 및 모니터링:**
   - 인덱싱 전 문서 내용 검증 로직 추가
   - 빈 텍스트/임베딩 감지 및 로깅 강화

---

## 추가 권장 사항

### 1. 문서 검증 강화
- 인덱싱 전 문서 내용이 비어있지 않은지 확인
- 최소 텍스트 길이 요구사항 설정 (예: 10자 이상)

### 2. 에러 핸들링 개선
- 구체적인 에러 메시지 제공
- 실패한 문서 ID와 원인을 상세히 로깅
- 재시도 메커니즘 고려

### 3. 데이터 품질 관리
- JSON 파일 생성 시 자동 검증
- 제어 문자 자동 이스케이프
- 빈 문서 필터링

---

## 참고

- [JSON 스펙 (RFC 7159)](https://tools.ietf.org/html/rfc7159)
- [ChromaDB 문서](https://docs.trychroma.com/)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)

