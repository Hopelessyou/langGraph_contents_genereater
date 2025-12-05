"""프롬프트 템플릿 및 시스템 프롬프트"""

from typing import Dict, Any, List


class PromptTemplates:
    """프롬프트 템플릿 관리"""
    
    SYSTEM_PROMPT = """당신은 법률 전문가 AI 어시스턴트입니다. 
사용자의 법률 질문에 대해 정확하고 전문적인 답변을 제공합니다.

주요 역할:
1. 법령, 판례, 절차 등 법률 정보를 정확하게 설명
2. 사용자의 질문에 대해 명확하고 이해하기 쉬운 답변 제공
3. 관련 법령 조문과 판례를 적절히 인용
4. 실무적인 조언과 주의사항 제공

답변 작성 시 주의사항:
- 정확한 법률 용어 사용
- 출처를 명확히 표시 (법령 조문 번호, 판례 번호 등)
- 추측이나 불확실한 정보 제공 금지
- 사용자의 상황에 맞는 실무적 조언 제공"""

    @staticmethod
    def get_statute_prompt(context: str, query: str) -> str:
        """법령 관련 프롬프트"""
        return f"""다음은 관련 법령 정보입니다:

{context}

사용자 질문: {query}

위 법령 정보를 바탕으로 사용자의 질문에 답변해주세요.
답변 시 다음을 포함해주세요:
1. 관련 법령 조문 번호와 내용
2. 법령의 핵심 내용 설명
3. 실무 적용 시 주의사항"""

    @staticmethod
    def get_case_prompt(context: str, query: str) -> str:
        """판례 관련 프롬프트"""
        return f"""다음은 관련 판례 정보입니다:

{context}

사용자 질문: {query}

위 판례 정보를 바탕으로 사용자의 질문에 답변해주세요.
답변 시 다음을 포함해주세요:
1. 관련 판례 번호와 법원
2. 판결 요지
3. 실무에 대한 시사점"""

    @staticmethod
    def get_procedure_prompt(context: str, query: str) -> str:
        """절차 관련 프롬프트"""
        return f"""다음은 관련 절차 정보입니다:

{context}

사용자 질문: {query}

위 절차 정보를 바탕으로 사용자의 질문에 답변해주세요.
답변 시 다음을 포함해주세요:
1. 절차의 단계별 설명
2. 각 단계에서 주의할 사항
3. 필요한 서류나 준비사항"""

    @staticmethod
    def get_general_prompt(context: str, query: str) -> str:
        """일반 프롬프트"""
        return f"""다음은 검색된 법률 정보입니다:

{context}

사용자 질문: {query}

위 정보를 바탕으로 사용자의 질문에 정확하고 전문적인 답변을 제공해주세요.
답변 시 다음을 포함해주세요:
1. 핵심 내용 요약
2. 관련 법령이나 판례 인용
3. 실무적 조언"""

    @staticmethod
    def get_prompt_by_type(doc_type: str, context: str, query: str) -> str:
        """문서 타입에 따른 프롬프트 선택"""
        if doc_type == "statute":
            return PromptTemplates.get_statute_prompt(context, query)
        elif doc_type == "case":
            return PromptTemplates.get_case_prompt(context, query)
        elif doc_type == "procedure":
            return PromptTemplates.get_procedure_prompt(context, query)
        else:
            return PromptTemplates.get_general_prompt(context, query)

    @staticmethod
    def build_user_prompt(
        context: str,
        query: str,
        document_types: List[str] = None,
    ) -> str:
        """사용자 프롬프트 구성"""
        if document_types and len(document_types) == 1:
            return PromptTemplates.get_prompt_by_type(
                document_types[0], context, query
            )
        else:
            return PromptTemplates.get_general_prompt(context, query)


class ContextOptimizer:
    """컨텍스트 윈도우 최적화"""
    
    MAX_CONTEXT_LENGTH = 4000  # 최대 컨텍스트 길이 (토큰 기준, 대략)
    
    @staticmethod
    def optimize_context(
        context: str,
        max_length: int = None,
    ) -> str:
        """
        컨텍스트를 최적화합니다.
        
        Args:
            context: 원본 컨텍스트
            max_length: 최대 길이 (문자 수)
            
        Returns:
            최적화된 컨텍스트
        """
        if max_length is None:
            max_length = ContextOptimizer.MAX_CONTEXT_LENGTH * 3  # 대략 문자 수
        
        if len(context) <= max_length:
            return context
        
        # 문서 단위로 분할
        documents = context.split("[문서")
        
        # 각 문서의 중요도 평가 (길이 기반 간단 평가)
        doc_scores = []
        for i, doc in enumerate(documents):
            if not doc.strip():
                continue
            # 간단한 점수: 문서 길이 (더 긴 문서가 더 많은 정보 포함)
            score = len(doc)
            doc_scores.append((i, doc, score))
        
        # 점수 순으로 정렬
        doc_scores.sort(key=lambda x: x[2], reverse=True)
        
        # 상위 문서들로 컨텍스트 재구성
        optimized_parts = []
        current_length = 0
        
        for _, doc, _ in doc_scores:
            doc_text = f"[문서{doc}"
            if current_length + len(doc_text) <= max_length:
                optimized_parts.append(doc_text)
                current_length += len(doc_text)
            else:
                break
        
        # 원래 순서대로 정렬
        optimized_parts.sort(key=lambda x: int(x.split("]")[0].replace("[문서", "")))
        
        return "\n".join(optimized_parts) if optimized_parts else context[:max_length]

