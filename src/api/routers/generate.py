"""법률 콘텐츠 생성 API"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
import json

from ...rag import HybridRetriever, LLMManager
from ..dependencies import get_retriever, get_llm_manager

router = APIRouter()


class ContentGenerationRequest(BaseModel):
    """콘텐츠 생성 요청"""
    topic: str = Field(..., description="생성할 콘텐츠 주제/키워드")
    content_type: Literal["blog", "article", "opinion", "analysis", "faq"] = Field(
        default="blog",
        description="콘텐츠 타입: blog(블로그), article(기사), opinion(의견서), analysis(분석), faq(FAQ)"
    )
    style: Optional[str] = Field(
        None,
        description="작성 스타일 (예: 전문적, 대중적, 간결한 등)"
    )
    target_length: Optional[int] = Field(
        None,
        description="목표 글자 수 (공백 제외)"
    )
    include_sections: Optional[List[str]] = Field(
        None,
        description="포함할 섹션 (예: ['법적기준', '판례', '대응방법'])"
    )
    keywords: Optional[List[str]] = Field(
        None,
        description="반드시 포함할 키워드 목록"
    )
    document_types: Optional[List[str]] = Field(
        None,
        description="참고할 문서 타입 (statute, case 등)"
    )
    n_references: int = Field(
        default=5,
        ge=1,
        le=20,
        description="참고할 문서 수"
    )


class ContentGenerationResponse(BaseModel):
    """콘텐츠 생성 응답"""
    success: bool
    content: str
    title: Optional[str] = None
    sections: Optional[Dict[str, str]] = None
    references: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str


@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(
    request: ContentGenerationRequest,
    retriever: HybridRetriever = Depends(get_retriever),
    llm_manager: LLMManager = Depends(get_llm_manager),
):
    """
    법률 콘텐츠 생성
    
    RAG 기반으로 법률 관련 콘텐츠(블로그, 기사, 의견서 등)를 생성합니다.
    """
    try:
        
        # 1. 관련 문서 검색
        search_result = retriever.search(
            query=request.topic,
            n_results=request.n_references,
            document_types=request.document_types,
        )
        
        # 2. 컨텍스트 구성
        context = search_result.get("context", "")
        references = search_result.get("results", [])
        
        # 3. 콘텐츠 타입별 프롬프트 생성
        system_prompt = _build_system_prompt(
            content_type=request.content_type,
            style=request.style,
            target_length=request.target_length,
            include_sections=request.include_sections,
            keywords=request.keywords,
        )
        
        user_prompt = _build_user_prompt(
            topic=request.topic,
            context=context,
            content_type=request.content_type,
        )
        
        # 4. LLM으로 콘텐츠 생성
        generated_content = llm_manager.generate_response(
            context=context,
            query=user_prompt,
            system_prompt=system_prompt,
            document_types=request.document_types,
        )
        
        # 5. 콘텐츠 파싱 (제목, 섹션 등 추출)
        parsed_content = _parse_generated_content(
            content=generated_content,
            content_type=request.content_type,
        )
        
        # 6. 참고 문서 정보 정리
        reference_list = [
            {
                "title": ref.get("metadata", {}).get("title", "N/A"),
                "type": ref.get("metadata", {}).get("type", "N/A"),
                "id": ref.get("id", "N/A"),
                "relevance": ref.get("score") or (1 - ref.get("distance", 1)) if ref.get("distance") else None,
            }
            for ref in references[:request.n_references]
        ]
        
        return ContentGenerationResponse(
            success=True,
            content=parsed_content.get("content", generated_content),
            title=parsed_content.get("title"),
            sections=parsed_content.get("sections"),
            references=reference_list,
            metadata={
                "content_type": request.content_type,
                "topic": request.topic,
                "word_count": len(generated_content.replace(" ", "")),
            },
            timestamp=datetime.now().isoformat(),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"콘텐츠 생성 중 오류가 발생했습니다: {str(e)}"
        )


def _build_system_prompt(
    content_type: str,
    style: Optional[str] = None,
    target_length: Optional[int] = None,
    include_sections: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None,
) -> str:
    """시스템 프롬프트 생성"""
    
    base_prompt = "당신은 전문 법률 콘텐츠 작가입니다. 제공된 법률 문서(법령, 판례 등)를 참고하여 정확하고 전문적인 법률 콘텐츠를 작성합니다.\n\n"
    
    # 콘텐츠 타입별 지시사항
    type_instructions = {
        "blog": """
블로그 포스팅 작성 규칙:
- 독자 친화적이고 이해하기 쉬운 문체 사용
- 법률 용어는 쉬운 설명과 함께 사용
- 실제 사례와 판례를 활용하여 구체적으로 설명
- 실용적인 조언과 대응 방법 포함
- SEO를 고려한 제목과 키워드 배치
""",
        "article": """
법률 기사 작성 규칙:
- 객관적이고 중립적인 톤 유지
- 사실에 기반한 정확한 정보 제공
- 법령 조문과 판례를 명확히 인용
- 전문가 의견과 분석 포함
""",
        "opinion": """
법률 의견서 작성 규칙:
- 전문적이고 정확한 법률 분석
- 관련 법령과 판례를 상세히 인용
- 법리적 논거를 체계적으로 제시
- 결론과 권고사항을 명확히 제시
""",
        "analysis": """
법률 케이스 분석 작성 규칙:
- 사건의 사실관계를 명확히 정리
- 법적 쟁점을 체계적으로 분석
- 관련 법령과 판례를 비교 분석
- 법리적 판단과 시사점 제시
""",
        "faq": """
FAQ 작성 규칙:
- 질문은 일반인이 궁금해할 만한 내용으로 구성
- 답변은 간결하고 명확하게 작성
- 관련 법령 조문 번호 명시
- 실무적인 조언 포함
""",
    }
    
    prompt = base_prompt + type_instructions.get(content_type, "")
    
    # 스타일 지정
    if style:
        prompt += f"\n작성 스타일: {style}\n"
    
    # 목표 길이
    if target_length:
        prompt += f"\n목표 글자 수: 약 {target_length}자 (공백 제외)\n"
    
    # 포함할 섹션
    if include_sections:
        prompt += f"\n반드시 포함할 섹션: {', '.join(include_sections)}\n"
    
    # 키워드
    if keywords:
        prompt += f"\n반드시 포함할 키워드: {', '.join(keywords)}\n"
        prompt += "키워드는 자연스럽게 문맥에 맞게 배치하세요.\n"
    
    prompt += "\n중요: 제공된 법률 문서의 내용을 정확히 반영하고, 법령 조문 번호와 판례 번호를 명확히 표시하세요."
    
    return prompt


def _build_user_prompt(
    topic: str,
    context: str,
    content_type: str,
) -> str:
    """사용자 프롬프트 생성"""
    
    prompts = {
        "blog": f"""
다음 주제에 대해 법률 블로그 포스팅을 작성해주세요.

주제: {topic}

다음 구조로 작성해주세요:
1. 제목 (SEO 최적화, 매력적)
2. 도입부 (문제 상황 설명, 호기심 유발)
3. 법적 기준과 처벌
4. 실제 사례와 판례
5. 대응 방법과 예방책
6. 전문가 조언 (IBS법률사무소 언급)
7. 마무리 (행동 유도)

참고 문서:
{context}
""",
        "article": f"""
다음 주제에 대해 법률 기사를 작성해주세요.

주제: {topic}

다음 구조로 작성해주세요:
1. 제목
2. 기사 본문 (사실 관계, 법적 배경, 전문가 의견)
3. 관련 법령 및 판례 인용
4. 시사점 및 전망

참고 문서:
{context}
""",
        "opinion": f"""
다음 주제에 대해 법률 의견서를 작성해주세요.

주제: {topic}

다음 구조로 작성해주세요:
1. 의견서 제목
2. 사실관계
3. 법적 쟁점
4. 관련 법령 및 판례
5. 법리적 분석
6. 결론 및 의견

참고 문서:
{context}
""",
        "analysis": f"""
다음 주제에 대해 법률 케이스 분석을 작성해주세요.

주제: {topic}

다음 구조로 작성해주세요:
1. 분석 제목
2. 사건 개요
3. 법적 쟁점
4. 관련 법령 검토
5. 관련 판례 분석
6. 법리적 판단
7. 시사점

참고 문서:
{context}
""",
        "faq": f"""
다음 주제에 대해 FAQ를 작성해주세요.

주제: {topic}

질문과 답변 형식으로 작성하되, 다음 주제들을 포함해주세요:
- 법적 정의 및 기준
- 처벌 및 법적 효과
- 실제 사례
- 대응 방법
- 전문가 상담 필요성

참고 문서:
{context}
""",
    }
    
    return prompts.get(content_type, f"다음 주제에 대해 법률 콘텐츠를 작성해주세요:\n\n주제: {topic}\n\n참고 문서:\n{context}")


def _parse_generated_content(
    content: str,
    content_type: str,
) -> Dict[str, Any]:
    """생성된 콘텐츠 파싱"""
    result = {
        "content": content,
        "title": None,
        "sections": None,
    }
    
    # 제목 추출 시도
    lines = content.split("\n")
    for line in lines[:10]:  # 처음 10줄에서 제목 찾기
        line = line.strip()
        if line and ("제목" in line or "Title" in line.lower()):
            # "제목: ..." 형식에서 추출
            if ":" in line:
                result["title"] = line.split(":", 1)[1].strip()
            elif len(line) < 100:  # 짧은 줄은 제목일 가능성
                result["title"] = line
            break
    
    # 섹션 추출 (블로그, 기사 등)
    if content_type in ["blog", "article"]:
        sections = {}
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 섹션 헤더 감지 (번호나 제목 형식)
            if (line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")) or
                line.startswith(("①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧")) or
                (len(line) < 50 and ":" not in line and line.endswith(("법", "책", "안", "점", "례")))):
                if current_section:
                    sections[current_section] = "\n".join(current_content)
                current_section = line
                current_content = []
            else:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = "\n".join(current_content)
        
        if sections:
            result["sections"] = sections
    
    return result

