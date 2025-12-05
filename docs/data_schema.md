# 데이터 스키마 문서

## 공통 스키마

모든 문서는 다음 기본 구조를 따릅니다:

```json
{
  "id": "문서 고유 ID",
  "category": "카테고리 (형사, 민사 등)",
  "sub_category": "하위 카테고리 (사기, 계약 등)",
  "type": "문서 타입",
  "title": "문서 제목",
  "content": "문서 내용 (문자열 또는 배열)",
  "metadata": {}
}
```

## 문서 타입별 스키마

### 1. 법령 (statute)

```json
{
  "id": "statute-347",
  "category": "형사",
  "sub_category": "사기",
  "type": "statute",
  "title": "형법 제347조(사기)",
  "content": "조문 내용",
  "metadata": {
    "law_name": "형법",
    "article_number": "347",
    "topics": ["사기", "편취"],
    "source": "법제처",
    "updated_at": "2024-01-01"
  }
}
```

### 2. 판례 (case)

```json
{
  "id": "case-2023do11234",
  "category": "형사",
  "sub_category": "사기",
  "type": "case",
  "title": "대법원 2023도11234 판결",
  "content": "판례 요약 내용",
  "metadata": {
    "court": "대법원",
    "year": 2023,
    "case_number": "2023도11234",
    "keywords": ["사기", "초범", "실형"],
    "holding": "판결 요지",
    "updated_at": "2024-01-10"
  }
}
```

### 3. 절차 매뉴얼 (procedure)

```json
{
  "id": "procedure-police-fraud",
  "category": "형사",
  "sub_category": "사기",
  "type": "procedure",
  "title": "사기 사건 경찰 조사 절차",
  "content": "절차 설명",
  "metadata": {
    "stage": "경찰조사",
    "topic": "절차",
    "keywords": ["경찰 조사", "사기", "절차"],
    "updated_at": "2024-01-05"
  }
}
```

### 4. 템플릿 (template)

```json
{
  "id": "template-criminal-fraud",
  "category": "형사",
  "sub_category": "사기",
  "type": "template",
  "title": "형사사기 콘텐츠 템플릿",
  "content": [
    "1. 사건 요약",
    "2. 관련 법령",
    "3. 판례 경향",
    "4. 결론"
  ],
  "metadata": {
    "usage": "콘텐츠 생성 템플릿",
    "output_styles": ["블로그형", "뉴스형"],
    "updated_at": "2024-01-02"
  }
}
```

### 5. 실무 매뉴얼 (manual)

```json
{
  "id": "manual-fraud-defense",
  "category": "형사",
  "sub_category": "사기",
  "type": "manual",
  "title": "사기 사건 변호 실무 매뉴얼",
  "content": "실무 매뉴얼 내용",
  "metadata": {
    "manual_type": "변호 실무",
    "target_audience": "변호사",
    "keywords": ["사기", "변호", "실무"],
    "updated_at": "2024-01-03"
  }
}
```

### 6. 사건 유형 (case_type)

```json
{
  "id": "case-type-fraud",
  "category": "형사",
  "sub_category": "사기",
  "type": "case_type",
  "title": "사기 사건 유형 정의",
  "content": "사건 유형 정의 내용",
  "metadata": {
    "case_type_code": "FRAUD",
    "related_keywords": ["사기", "편취"],
    "typical_penalty": "10년 이하 징역 또는 2천만원 이하 벌금",
    "updated_at": "2024-01-04"
  }
}
```

### 7. 양형기준 (sentencing_guideline)

```json
{
  "id": "sentencing-fraud",
  "category": "형사",
  "sub_category": "사기",
  "type": "sentencing_guideline",
  "title": "사기 사건 양형기준 요약",
  "content": "양형기준 요약 내용",
  "metadata": {
    "guideline_type": "형사",
    "factors": ["피해 규모", "범행 방법"],
    "typical_range": "집행유예 ~ 3년 징역",
    "updated_at": "2024-01-06"
  }
}
```

### 8. FAQ (faq)

```json
{
  "id": "faq-fraud-first-time",
  "category": "형사",
  "sub_category": "사기",
  "type": "faq",
  "title": "사기 초범은 집행유예가 가능한가요?",
  "question": "사기 초범은 집행유예가 가능한가요?",
  "content": "답변 내용",
  "metadata": {
    "question_type": "처벌",
    "related_topics": ["초범", "집행유예"],
    "frequency": 100,
    "updated_at": "2024-01-07"
  }
}
```

### 9. 키워드 맵핑 (keyword_mapping)

```json
{
  "id": "keyword-mapping-fraud",
  "category": "형사",
  "sub_category": "사기",
  "type": "keyword_mapping",
  "title": "사기 관련 키워드 맵핑",
  "content": {
    "투자금 편취": ["사기", "특정경제범죄가중처벌법"],
    "피싱": ["사기", "정보통신망법"]
  },
  "metadata": {
    "keywords": ["투자금 편취", "피싱"],
    "mapped_case_types": ["사기"],
    "confidence": 0.95,
    "updated_at": "2024-01-08"
  }
}
```

### 10. 스타일 문제 (style_issue)

```json
{
  "id": "style-issue-legal-term",
  "category": "형사",
  "sub_category": "사기",
  "type": "style_issue",
  "title": "법률 용어 오용 문제",
  "content": "스타일 문제 설명",
  "metadata": {
    "issue_type": "용어",
    "severity": "high",
    "examples": ["기망과 사기의 구분"],
    "updated_at": "2024-01-09"
  }
}
```

## 필수 필드

모든 문서 타입에서 필수 필드:
- `id`: 고유 식별자
- `type`: 문서 타입
- `title`: 제목
- `content`: 내용

## 검증 규칙

- `id`는 고유해야 함
- `type`은 정의된 타입 중 하나여야 함
- `content`는 비어있지 않아야 함
- `metadata`는 타입별 필수 필드를 포함해야 함

