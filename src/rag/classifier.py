"""키워드 기반 자동 분류"""

from typing import List, Dict, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)


class KeywordClassifier:
    """키워드 기반 분류기"""
    
    # 카테고리 키워드 매핑
    CATEGORY_KEYWORDS = {
        "형사": ["형사", "범죄", "처벌", "징역", "벌금", "사기", "절도", "폭행", "살인"],
        "민사": ["민사", "계약", "손해배상", "소유권", "임대차", "금전"],
        "가족": ["가족", "이혼", "상속", "양육", "부양"],
        "행정": ["행정", "허가", "인허가", "과태료", "과징금"],
    }
    
    # 하위 카테고리 키워드 매핑
    SUB_CATEGORY_KEYWORDS = {
        "사기": ["사기", "편취", "기망", "투자금", "피싱"],
        "절도": ["절도", "도난", "절취"],
        "폭행": ["폭행", "상해", "협박"],
        "계약": ["계약", "계약서", "위약금", "해약"],
        "손해배상": ["손해배상", "배상", "과실"],
    }
    
    # 문서 타입 키워드 매핑
    DOC_TYPE_KEYWORDS = {
        "statute": ["법령", "조문", "법률", "법규"],
        "case": ["판례", "판결", "선고", "법원"],
        "procedure": ["절차", "순서", "절차", "방법"],
        "template": ["템플릿", "양식", "서식"],
    }
    
    @classmethod
    def classify(cls, text: str) -> Dict[str, Any]:
        """
        텍스트를 분류합니다.
        
        Args:
            text: 분류할 텍스트
            
        Returns:
            분류 결과 (category, sub_category, document_types)
        """
        text_lower = text.lower()
        
        # 카테고리 분류
        category = cls._classify_category(text_lower)
        
        # 하위 카테고리 분류
        sub_category = cls._classify_sub_category(text_lower)
        
        # 문서 타입 분류
        document_types = cls._classify_document_types(text_lower)
        
        return {
            "category": category,
            "sub_category": sub_category,
            "document_types": document_types,
        }
    
    @classmethod
    def _classify_category(cls, text: str) -> Optional[str]:
        """카테고리 분류"""
        scores = {}
        
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[category] = score
        
        if scores:
            return max(scores, key=scores.get)
        return None
    
    @classmethod
    def _classify_sub_category(cls, text: str) -> Optional[str]:
        """하위 카테고리 분류"""
        scores = {}
        
        for sub_category, keywords in cls.SUB_CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[sub_category] = score
        
        if scores:
            return max(scores, key=scores.get)
        return None
    
    @classmethod
    def _classify_document_types(cls, text: str) -> List[str]:
        """문서 타입 분류"""
        types = []
        
        for doc_type, keywords in cls.DOC_TYPE_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                types.append(doc_type)
        
        return types if types else None


class CaseTypeRecommender:
    """사건 유형 추천기"""
    
    @staticmethod
    def recommend_case_type(
        query: str,
        keywords: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        관련 사건 유형을 추천합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 추가 키워드
            
        Returns:
            추천 사건 유형 리스트
        """
        # 키워드 추출
        if keywords is None:
            keywords = query.split()
        
        # 간단한 매핑 (실제로는 더 정교한 로직 필요)
        recommendations = []
        
        if "사기" in query or "편취" in query:
            recommendations.append({
                "case_type": "사기",
                "confidence": 0.9,
                "related_keywords": ["사기", "편취", "기망"],
            })
        
        if "절도" in query or "도난" in query:
            recommendations.append({
                "case_type": "절도",
                "confidence": 0.8,
                "related_keywords": ["절도", "도난"],
            })
        
        return recommendations


class TemplateMatcher:
    """템플릿 자동 매칭"""
    
    @staticmethod
    def match_template(
        query: str,
        category: Optional[str] = None,
        sub_category: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        쿼리에 맞는 템플릿을 매칭합니다.
        
        Args:
            query: 사용자 쿼리
            category: 카테고리
            sub_category: 하위 카테고리
            
        Returns:
            매칭된 템플릿 정보
        """
        # 간단한 매칭 로직
        # 실제로는 벡터 검색이나 더 정교한 매칭 필요
        
        if category == "형사" and sub_category == "사기":
            return {
                "template_id": "template-criminal-fraud",
                "title": "형사사기 콘텐츠 템플릿",
                "match_score": 0.9,
            }
        
        return None

