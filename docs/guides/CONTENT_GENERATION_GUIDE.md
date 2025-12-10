# 블로그 콘텐츠 생성 가이드

## 📋 목차

1. [개요](#개요)
2. [전체 워크플로우](#전체-워크플로우)
3. [프롬프트 구조 및 처리](#프롬프트-구조-및-처리)
4. [파인튜닝 모델 사용 방법](#파인튜닝-모델-사용-방법)
5. [API 사용 예제](#api-사용-예제)
6. [고급 설정](#고급-설정)
7. [문제 해결](#문제-해결)

---

## 개요

### 블로그 콘텐츠 생성이란?

이 시스템은 **RAG(Retrieval-Augmented Generation)** 기반으로 법률 관련 블로그 콘텐츠를 자동 생성합니다. 벡터 데이터베이스에서 관련 법령, 판례, 절차 등을 검색하여 정확하고 전문적인 콘텐츠를 생성합니다.

**주요 특징:**
- 법령 및 판례 기반 정확한 정보 제공
- SEO 최적화된 블로그 포스팅 생성
- 다양한 콘텐츠 타입 지원 (블로그, 기사, 의견서, 분석, FAQ)
- 파인튜닝 모델 지원으로 특화된 콘텐츠 생성

**지원하는 콘텐츠 타입:**
- `blog`: 블로그 포스팅
- `article`: 법률 기사
- `opinion`: 법률 의견서
- `analysis`: 법률 케이스 분석
- `faq`: FAQ 형식

---

## 전체 워크플로우

블로그 콘텐츠 생성 요청이 들어오면 다음과 같은 단계로 진행됩니다:

```
사용자 요청
    ↓
1. 관련 문서 검색 (RAG)
    ↓
2. 컨텍스트 구성
    ↓
3. 프롬프트 생성
    ├─ 시스템 프롬프트 (콘텐츠 타입별 규칙)
    └─ 사용자 프롬프트 (주제 + 컨텍스트)
    ↓
4. LLM으로 콘텐츠 생성
    ↓
5. 콘텐츠 파싱 및 구조화
    ↓
6. 응답 반환
```

### 단계별 상세 설명

#### 1단계: 관련 문서 검색 (RAG)

**코드 위치:** `src/api/routers/generate.py:74-79`

```python
# 1. 관련 문서 검색
search_result = await retriever.search(
    query=request.topic,  # 사용자가 입력한 주제/키워드
    n_results=request.n_references,  # 참고할 문서 수 (기본값: 5)
    document_types=request.document_types,  # 문서 타입 필터 (statute, case 등)
)
```

**처리 과정:**
1. 사용자가 입력한 `topic` (예: "사기죄 처벌")을 쿼리로 사용
2. 벡터 데이터베이스에서 의미적으로 유사한 문서 검색
3. 하이브리드 검색 (벡터 검색 + 키워드 검색) 수행
4. 상위 N개 문서 반환 (기본값: 5개, 최대: 20개)

**검색 결과 예시:**
```json
{
  "query": "사기죄 처벌",
  "results": [
    {
      "id": "case-2005고합694_chunk_1",
      "document": "【판단】 피고인들은 이 사건 토지를 매수하여...",
      "metadata": {
        "title": "대구지법 2005고합694 판결",
        "case_number": "2005고합694",
        "category": "형사",
        "sub_category": "사기"
      },
      "distance": 0.234,
      "score": 0.81
    },
    ...
  ],
  "context": "[문서 1]\n제목: 대구지법 2005고합694 판결\n내용: ...\n\n[문서 2]\n..."
}
```

#### 2단계: 컨텍스트 구성

**코드 위치:** `src/api/routers/generate.py:81-83`

```python
# 2. 컨텍스트 구성
context = search_result.get("context", "")
references = search_result.get("results", [])
```

**컨텍스트 형식:**
```
[문서 1]
제목: 대구지법 2005고합694 판결
타입: case
내용: 【판단】 피고인들은 이 사건 토지를 매수하여 아파트 건설 공사를 추진하고...

[문서 2]
제목: 형법 제347조 (사기)
타입: statute
내용: ① 사람을 기망하여 재물의 교부를 받거나 재산상 이익을 취득한 자는...

[문서 3]
...
```

**컨텍스트 최적화:**
- `ContextOptimizer.optimize_context()` 메서드가 자동으로 컨텍스트 길이를 최적화
- 최대 길이: 약 12,000자 (4,000 토큰 기준)
- 문서 중요도에 따라 상위 문서 우선 선택

#### 3단계: 프롬프트 생성

프롬프트는 **시스템 프롬프트**와 **사용자 프롬프트** 두 부분으로 구성됩니다.

##### 3-1. 시스템 프롬프트 생성

**코드 위치:** `src/api/routers/generate.py:146-218`

시스템 프롬프트는 LLM의 역할과 작성 규칙을 정의합니다.

**기본 구조:**
```python
base_prompt = "당신은 전문 법률 콘텐츠 작가입니다. 제공된 법률 문서(법령, 판례 등)를 참고하여 정확하고 전문적인 법률 콘텐츠를 작성합니다.\n\n"

# 콘텐츠 타입별 지시사항 추가
type_instructions = {
    "blog": """
블로그 포스팅 작성 규칙:
- 독자 친화적이고 이해하기 쉬운 문체 사용
- 법률 용어는 쉬운 설명과 함께 사용
- 실제 사례와 판례를 활용하여 구체적으로 설명
- 실용적인 조언과 대응 방법 포함
- SEO를 고려한 제목과 키워드 배치
""",
    ...
}

# 추가 옵션 적용
if style:
    prompt += f"\n작성 스타일: {style}\n"
if target_length:
    prompt += f"\n목표 글자 수: 약 {target_length}자 (공백 제외)\n"
if keywords:
    prompt += f"\n반드시 포함할 키워드: {', '.join(keywords)}\n"
```

**블로그 타입 시스템 프롬프트 예시:**
```
당신은 전문 법률 콘텐츠 작가입니다. 제공된 법률 문서(법령, 판례 등)를 참고하여 정확하고 전문적인 법률 콘텐츠를 작성합니다.

블로그 포스팅 작성 규칙:
- 독자 친화적이고 이해하기 쉬운 문체 사용
- 법률 용어는 쉬운 설명과 함께 사용
- 실제 사례와 판례를 활용하여 구체적으로 설명
- 실용적인 조언과 대응 방법 포함
- SEO를 고려한 제목과 키워드 배치

작성 스타일: 대중적
목표 글자 수: 약 2000자 (공백 제외)
반드시 포함할 키워드: 사기죄, 처벌, 형법
키워드는 자연스럽게 문맥에 맞게 배치하세요.

중요: 제공된 법률 문서의 내용을 정확히 반영하고, 법령 조문 번호와 판례 번호를 명확히 표시하세요.
```

##### 3-2. 사용자 프롬프트 생성

**코드 위치:** `src/api/routers/generate.py:221-310`

사용자 프롬프트는 실제 생성할 콘텐츠의 주제와 구조를 지정합니다.

**블로그 타입 사용자 프롬프트 예시:**
```
다음 주제에 대해 법률 블로그 포스팅을 작성해주세요.

주제: 사기죄 처벌

다음 구조로 작성해주세요:
1. 제목 (SEO 최적화, 매력적)
2. 도입부 (문제 상황 설명, 호기심 유발)
3. 법적 기준과 처벌
4. 실제 사례와 판례
5. 대응 방법과 예방책
6. 전문가 조언 (IBS법률사무소 언급)
7. 마무리 (행동 유도)

참고 문서:
[문서 1]
제목: 대구지법 2005고합694 판결
타입: case
내용: 【판단】 피고인들은 이 사건 토지를 매수하여...

[문서 2]
제목: 형법 제347조 (사기)
타입: statute
내용: ① 사람을 기망하여 재물의 교부를 받거나...
```

#### 4단계: LLM으로 콘텐츠 생성

**코드 위치:** `src/api/routers/generate.py:100-106`, `src/rag/llm_manager.py:48-114`

```python
# 4. LLM으로 콘텐츠 생성
generated_content = llm_manager.generate_response(
    context=context,
    query=user_prompt,
    system_prompt=system_prompt,
    document_types=request.document_types,
)
```

**LLMManager 내부 처리:**

1. **컨텍스트 최적화**
   ```python
   optimized_context = ContextOptimizer.optimize_context(context)
   ```

2. **프롬프트 구성**
   ```python
   # 이미 완전한 프롬프트인 경우 (콘텐츠 생성 등)
   if "\n참고 문서:" in query or len(query) > 500:
       user_prompt = query.replace("{context}", optimized_context)
   else:
       # 일반 질의응답 프롬프트 구성
       user_prompt = PromptTemplates.build_user_prompt(
           context=optimized_context,
           query=query,
           document_types=document_types,
       )
   ```

3. **메시지 구성**
   ```python
   messages = [
       SystemMessage(content=system_prompt_text),
       HumanMessage(content=user_prompt),
   ]
   ```

4. **LLM 호출**
   ```python
   response = self.llm.invoke(messages)
   return response.content
   ```

**사용되는 LLM 모델:**
- 기본값: `gpt-4-turbo-preview` (설정에서 변경 가능)
- 파인튜닝 모델: `ft:gpt-3.5-turbo-0125:korealawyer2::CgYw1VLx` (설정 가능)

#### 5단계: 콘텐츠 파싱 및 구조화

**코드 위치:** `src/api/routers/generate.py:108-112`, `313-364`

```python
# 5. 콘텐츠 파싱 (제목, 섹션 등 추출)
parsed_content = _parse_generated_content(
    content=generated_content,
    content_type=request.content_type,
)
```

**파싱 과정:**
1. 제목 추출: 처음 10줄에서 "제목:" 또는 "Title" 포함된 줄 찾기
2. 섹션 추출: 번호나 특정 패턴으로 섹션 구분
3. 구조화된 데이터 반환

**파싱 결과 예시:**
```python
{
    "content": "전체 콘텐츠...",
    "title": "사기죄 처벌과 형량, 알아야 할 모든 것",
    "sections": {
        "1. 법적 기준과 처벌": "형법 제347조에 따르면...",
        "2. 실제 사례와 판례": "대구지법 2005고합694 판결에서...",
        ...
    }
}
```

#### 6단계: 응답 반환

**코드 위치:** `src/api/routers/generate.py:125-137`

```python
return ContentGenerationResponse(
    success=True,
    content=parsed_content.get("content", generated_content),
    title=parsed_content.get("title"),
    sections=parsed_content.get("sections"),
    references=reference_list,  # 참고 문서 목록
    metadata={
        "content_type": request.content_type,
        "topic": request.topic,
        "word_count": len(generated_content.replace(" ", "")),
    },
    timestamp=datetime.now().isoformat(),
)
```

---

## 프롬프트 구조 및 처리

### 프롬프트 구성 요소

#### 1. 시스템 프롬프트 (System Prompt)

**역할:** LLM의 역할과 작성 규칙 정의

**구성 요소:**
- 기본 역할 정의: "당신은 전문 법률 콘텐츠 작가입니다..."
- 콘텐츠 타입별 규칙 (blog, article, opinion, analysis, faq)
- 작성 스타일 지정 (선택)
- 목표 글자 수 (선택)
- 포함할 섹션 (선택)
- 필수 키워드 (선택)

**코드 위치:** `src/api/routers/generate.py:146-218`

#### 2. 사용자 프롬프트 (User Prompt)

**역할:** 실제 생성할 콘텐츠의 주제와 구조 지정

**구성 요소:**
- 주제/키워드
- 콘텐츠 구조 (섹션별 요구사항)
- 참고 문서 (RAG 검색 결과)

**코드 위치:** `src/api/routers/generate.py:221-310`

### 프롬프트 처리 흐름

```
사용자 요청
    ↓
_build_system_prompt()
    ├─ 기본 프롬프트
    ├─ 콘텐츠 타입별 규칙
    ├─ 스타일 지정 (선택)
    ├─ 목표 길이 (선택)
    ├─ 포함 섹션 (선택)
    └─ 필수 키워드 (선택)
    ↓
시스템 프롬프트 완성
    ↓
_build_user_prompt()
    ├─ 주제/키워드
    ├─ 콘텐츠 구조
    └─ 참고 문서 (컨텍스트)
    ↓
사용자 프롬프트 완성
    ↓
LLMManager.generate_response()
    ├─ 컨텍스트 최적화
    ├─ 프롬프트 조합
    └─ LLM 호출
```

### 프롬프트 최적화 기법

#### 1. 컨텍스트 최적화

**코드 위치:** `src/rag/prompts.py:111-168`

```python
class ContextOptimizer:
    MAX_CONTEXT_LENGTH = 4000  # 최대 컨텍스트 길이 (토큰 기준)
    
    @staticmethod
    def optimize_context(context: str, max_length: int = None) -> str:
        """
        컨텍스트를 최적화합니다.
        - 문서 단위로 분할
        - 각 문서의 중요도 평가 (길이 기반)
        - 상위 문서 우선 선택
        - 최대 길이 제한 내에서 재구성
        """
```

**최적화 과정:**
1. 문서 단위로 분할 (`[문서 N]` 기준)
2. 각 문서의 중요도 평가 (문서 길이 기반)
3. 중요도 순으로 정렬
4. 최대 길이 내에서 상위 문서 선택
5. 원래 순서대로 재정렬

#### 2. 프롬프트 자동 감지

**코드 위치:** `src/rag/llm_manager.py:77-87`

```python
# query가 이미 완전한 프롬프트인 경우 (콘텐츠 생성 등) 그대로 사용
if "\n참고 문서:" in query or len(query) > 500:
    # 이미 완전한 프롬프트로 보임
    user_prompt = query.replace("{context}", optimized_context)
else:
    # 일반 질의응답 프롬프트 구성
    user_prompt = PromptTemplates.build_user_prompt(
        context=optimized_context,
        query=query,
        document_types=document_types,
    )
```

**자동 감지 기준:**
- `"\n참고 문서:"` 포함 → 완전한 프롬프트로 인식
- 길이가 500자 이상 → 완전한 프롬프트로 인식
- 그 외 → 일반 질의응답 프롬프트로 구성

---

## 파인튜닝 모델 사용 방법

### 파인튜닝 모델이란?

파인튜닝(Fine-tuning)은 기존 LLM 모델을 특정 도메인(법률)에 맞게 추가 학습시키는 과정입니다. 법률 콘텐츠 생성에 특화된 모델을 사용하면 더 정확하고 일관된 결과를 얻을 수 있습니다.

**파인튜닝 모델 예시:**
- `ft:gpt-3.5-turbo-0125:korealawyer2::CgYw1VLx`
- 베이스 모델: `gpt-3.5-turbo-0125`
- 학습 데이터: 246개 샘플 (법률 콘텐츠)
- 에포크: 3

### 파인튜닝 모델 설정 방법

#### 방법 1: 환경 변수로 설정 (권장)

`.env` 파일에 모델 이름 추가:

```bash
# 기본 LLM 모델
LLM_MODEL=ft:gpt-3.5-turbo-0125:korealawyer2::CgYw1VLx

# 또는 일반 모델
LLM_MODEL=gpt-4-turbo-preview
```

**설정 파일 위치:** `config/settings.py:24`

```python
class Settings(BaseSettings):
    # LLM Settings
    llm_model: str = "gpt-4-turbo-preview"  # .env에서 LLM_MODEL로 오버라이드 가능
```

#### 방법 2: API 요청 시 동적 설정

현재는 API 레벨에서 모델을 직접 지정할 수 없지만, `LLMManager`를 커스터마이징하여 가능합니다.

**커스터마이징 예시:**

```python
from src.rag import LLMManager

# 파인튜닝 모델 사용
llm_manager = LLMManager(
    model_name="ft:gpt-3.5-turbo-0125:korealawyer2::CgYw1VLx",
    temperature=0.7
)

# 콘텐츠 생성
content = llm_manager.generate_response(
    context=context,
    query=user_prompt,
    system_prompt=system_prompt,
)
```

#### 방법 3: 의존성 주입으로 커스터마이징

**코드 위치:** `src/api/dependencies.py`

```python
@lru_cache()
def get_llm_manager() -> LLMManager:
    """LLM Manager 싱글톤"""
    # 환경 변수에서 파인튜닝 모델 읽기
    finetuned_model = os.getenv("FINETUNED_MODEL")
    model_name = finetuned_model or settings.llm_model
    
    return LLMManager(
        model_name=model_name,
        temperature=0.7
    )
```

### 파인튜닝 모델 사용 시 주의사항

1. **모델 이름 정확성**
   - 파인튜닝 모델 이름은 정확히 입력해야 합니다
   - 형식: `ft:베이스모델:조직명::모델ID`

2. **API 키 확인**
   - 파인튜닝 모델도 OpenAI API 키가 필요합니다
   - `.env` 파일에 `OPENAI_API_KEY` 설정 확인

3. **비용 고려**
   - 파인튜닝 모델 사용 시 일반 모델과 다른 요금이 적용될 수 있습니다
   - 사용량 모니터링 권장

4. **성능 비교**
   - 파인튜닝 모델: 법률 도메인 특화, 빠른 응답, 비용 효율적
   - GPT-4: 더 넓은 일반 지식, 더 정확한 분석, 높은 비용

### 파인튜닝 모델 테스트

**Python 스크립트로 테스트:**

```python
from src.rag import LLMManager

# 파인튜닝 모델로 초기화
llm_manager = LLMManager(
    model_name="ft:gpt-3.5-turbo-0125:korealawyer2::CgYw1VLx",
    temperature=0.7
)

# 간단한 테스트
test_prompt = """
다음 주제에 대해 법률 블로그 포스팅을 작성해주세요.

주제: 사기죄 처벌

참고 문서:
[문서 1]
제목: 형법 제347조
내용: ① 사람을 기망하여 재물의 교부를 받거나 재산상 이익을 취득한 자는 10년 이하의 징역 또는 2천만원 이하의 벌금에 처한다.
"""

response = llm_manager.generate_response(
    context="[문서 1]\n제목: 형법 제347조\n내용: ...",
    query=test_prompt,
    system_prompt="당신은 전문 법률 콘텐츠 작가입니다."
)

print(response)
```

---

## API 사용 예제

### 1. 기본 블로그 콘텐츠 생성

**Swagger UI 사용:**

1. `http://localhost:8000/docs` 접속
2. `POST /api/v1/generate` 선택
3. "Try it out" 클릭
4. 요청 본문 입력:

```json
{
  "topic": "사기죄 처벌",
  "content_type": "blog",
  "n_references": 5
}
```

5. "Execute" 클릭

**cURL 사용:**

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "사기죄 처벌",
    "content_type": "blog",
    "n_references": 5
  }'
```

**Python requests 사용:**

```python
import requests

url = "http://localhost:8000/api/v1/generate"
data = {
    "topic": "사기죄 처벌",
    "content_type": "blog",
    "n_references": 5
}

response = requests.post(url, json=data)
result = response.json()

print(f"제목: {result['title']}")
print(f"콘텐츠: {result['content']}")
print(f"참고 문서: {len(result['references'])}개")
```

### 2. 고급 옵션 사용

**키워드, 스타일, 길이 지정:**

```json
{
  "topic": "사기죄 처벌",
  "content_type": "blog",
  "style": "대중적",
  "target_length": 2000,
  "keywords": ["사기죄", "처벌", "형법"],
  "include_sections": ["법적기준", "판례", "대응방법"],
  "document_types": ["case", "statute"],
  "n_references": 10
}
```

### 3. 다른 콘텐츠 타입 생성

**법률 기사:**

```json
{
  "topic": "최근 사기죄 판례 동향",
  "content_type": "article",
  "style": "객관적",
  "n_references": 8
}
```

**법률 의견서:**

```json
{
  "topic": "특정경제범죄 가중처벌법 적용 여부",
  "content_type": "opinion",
  "style": "전문적",
  "n_references": 10
}
```

**FAQ:**

```json
{
  "topic": "사기죄 관련 자주 묻는 질문",
  "content_type": "faq",
  "n_references": 5
}
```

---

## 고급 설정

### 1. 커스텀 시스템 프롬프트

현재는 API 레벨에서 직접 지정할 수 없지만, 코드 수정으로 가능합니다.

**수정 방법:**

`src/api/routers/generate.py`에서 `_build_system_prompt` 함수 수정:

```python
def _build_system_prompt(
    content_type: str,
    style: Optional[str] = None,
    target_length: Optional[int] = None,
    include_sections: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None,
    custom_instructions: Optional[str] = None,  # 추가
) -> str:
    # ... 기존 코드 ...
    
    if custom_instructions:
        prompt += f"\n추가 지시사항:\n{custom_instructions}\n"
    
    return prompt
```

### 2. Temperature 조정

Temperature는 생성된 텍스트의 창의성을 조절합니다.

**설정 방법:**

`.env` 파일에 추가 (현재는 코드 수정 필요):

```python
# src/api/dependencies.py
@lru_cache()
def get_llm_manager() -> LLMManager:
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    return LLMManager(
        model_name=settings.llm_model,
        temperature=temperature
    )
```

**Temperature 값 가이드:**
- `0.0-0.3`: 매우 보수적, 사실 기반, 일관성 높음
- `0.4-0.7`: 균형잡힌 창의성 (권장)
- `0.8-1.0`: 높은 창의성, 다양성

### 3. 최대 토큰 수 제한

**설정 방법:**

`src/rag/llm_manager.py` 수정:

```python
self.llm = ChatOpenAI(
    model_name=self.model_name,
    temperature=self.temperature,
    openai_api_key=settings.openai_api_key,
    max_tokens=2000,  # 추가
)
```

### 4. 스트리밍 응답

현재는 지원하지 않지만, `LLMManager.generate_response_async()`를 사용하여 구현 가능합니다.

**구현 예시:**

```python
async def generate_content_stream(request):
    # ... 검색 및 프롬프트 생성 ...
    
    async for chunk in llm_manager.generate_response_async(
        context=context,
        query=user_prompt,
        document_types=request.document_types,
    ):
        yield chunk
```

---

## 문제 해결

### 문제 1: 생성된 콘텐츠가 너무 짧음

**원인:**
- `target_length`가 설정되지 않음
- 컨텍스트가 부족함

**해결 방법:**
1. `target_length` 파라미터 지정
2. `n_references` 증가 (더 많은 참고 문서)
3. `include_sections`로 필수 섹션 지정

### 문제 2: 생성된 콘텐츠가 부정확함

**원인:**
- 검색된 문서가 주제와 관련이 적음
- 컨텍스트가 충분하지 않음

**해결 방법:**
1. `document_types`로 문서 타입 필터링
2. `n_references` 증가
3. `topic`을 더 구체적으로 작성

### 문제 3: 파인튜닝 모델이 작동하지 않음

**원인:**
- 모델 이름 오타
- API 키 문제
- 모델이 삭제되었거나 접근 불가

**해결 방법:**
1. 모델 이름 정확히 확인
2. OpenAI 대시보드에서 모델 상태 확인
3. API 키 유효성 확인
4. 일반 모델로 테스트 후 비교

### 문제 4: 생성 속도가 느림

**원인:**
- 많은 참고 문서 사용
- 긴 콘텐츠 생성
- 네트워크 지연

**해결 방법:**
1. `n_references` 감소 (3-5개 권장)
2. `target_length` 조정
3. 파인튜닝 모델 사용 (일반적으로 더 빠름)

### 문제 5: 키워드가 자연스럽지 않게 배치됨

**원인:**
- 키워드가 너무 많음
- 키워드가 주제와 관련이 적음

**해결 방법:**
1. 키워드 수 제한 (3-5개 권장)
2. 주제와 관련된 키워드만 선택
3. 시스템 프롬프트에 "자연스럽게 배치" 지시 추가

---

## 참고 자료

- [RAG 데이터 구축 가이드](./RAG_DATA_BUILD_GUIDE.md)
- [Swagger UI 사용 가이드](./SWAGGER_UI_GUIDE.md)
- [API 문서](../api/README.md)

---

## 요약

블로그 콘텐츠 생성은 다음과 같은 과정으로 진행됩니다:

1. **RAG 검색**: 주제와 관련된 법령, 판례 검색
2. **컨텍스트 구성**: 검색 결과를 구조화된 컨텍스트로 변환
3. **프롬프트 생성**: 시스템 프롬프트 + 사용자 프롬프트 조합
4. **LLM 생성**: 프롬프트를 LLM에 전달하여 콘텐츠 생성
5. **파싱 및 반환**: 생성된 콘텐츠를 구조화하여 반환

**파인튜닝 모델 사용:**
- `.env` 파일에 `LLM_MODEL=ft:모델이름` 설정
- 또는 `LLMManager` 초기화 시 `model_name` 파라미터 지정

**최적의 결과를 위한 팁:**
- 구체적인 주제 사용
- 적절한 참고 문서 수 (5-10개)
- 목표 길이 지정
- 필수 키워드 명시
- 문서 타입 필터링

