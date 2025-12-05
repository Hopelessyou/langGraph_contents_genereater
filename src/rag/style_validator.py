"""스타일 검증 및 법률 용어 정확성 검사"""

from typing import List, Dict, Any, Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class StyleValidator:
    """스타일 검증기"""
    
    # 법률 용어 사전 (간단한 예시)
    LEGAL_TERMS = {
        "기망": "속이는 행위",
        "사기": "기망하여 재물을 편취하는 범죄",
        "편취": "속여서 빼앗음",
        "횡령": "타인의 재물을 보관하다가 임의로 사용",
        "배임": "타인의 사무를 처리하는 자가 임무에 위배되는 행위",
    }
    
    # 자주 틀리는 용어 매핑
    COMMON_MISTAKES = {
        "기망": ["기만", "속임"],
        "편취": ["편치", "편취"],
        "횡령": ["횡영", "횡영"],
    }
    
    @staticmethod
    def validate_style(text: str) -> Dict[str, Any]:
        """
        텍스트 스타일을 검증합니다.
        
        Args:
            text: 검증할 텍스트
            
        Returns:
            검증 결과
        """
        issues = []
        warnings = []
        
        # 법률 용어 검사
        term_issues = StyleValidator._check_legal_terms(text)
        if term_issues:
            issues.extend(term_issues)
        
        # 문법 검사 (간단한 패턴)
        grammar_issues = StyleValidator._check_grammar(text)
        if grammar_issues:
            warnings.extend(grammar_issues)
        
        # 형식 검사
        format_issues = StyleValidator._check_format(text)
        if format_issues:
            warnings.extend(format_issues)
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "score": max(0, 100 - len(issues) * 10 - len(warnings) * 5),
        }
    
    @staticmethod
    def _check_legal_terms(text: str) -> List[str]:
        """법률 용어 정확성 검사"""
        issues = []
        
        # 잘못된 용어 사용 검사
        for correct_term, mistakes in StyleValidator.COMMON_MISTAKES.items():
            for mistake in mistakes:
                if mistake in text and correct_term not in text:
                    issues.append(f"'{mistake}' 대신 '{correct_term}'을 사용해야 합니다.")
        
        return issues
    
    @staticmethod
    def _check_grammar(text: str) -> List[str]:
        """문법 검사 (간단한 패턴)"""
        warnings = []
        
        # 연속된 공백
        if re.search(r'\s{2,}', text):
            warnings.append("연속된 공백이 있습니다.")
        
        # 문장 부호 누락 (간단 체크)
        sentences = re.split(r'[.!?]', text)
        if len(sentences) > 1:
            for i, sentence in enumerate(sentences[:-1], 1):
                if sentence.strip() and not sentence.strip()[-1] in '.!?':
                    # 마지막 문장이 아니면 경고하지 않음
                    pass
        
        return warnings
    
    @staticmethod
    def _check_format(text: str) -> List[str]:
        """형식 검사"""
        warnings = []
        
        # 너무 긴 문장 (100자 이상)
        sentences = re.split(r'[.!?]', text)
        for sentence in sentences:
            if len(sentence.strip()) > 100:
                warnings.append("너무 긴 문장이 있습니다. (100자 이상)")
        
        # 특수 문자 사용
        if re.search(r'[^\w\s가-힣.,!?;:()\[\]{}"\'-]', text):
            warnings.append("부적절한 특수 문자가 포함되어 있습니다.")
        
        return warnings


class LegalTermChecker:
    """법률 용어 정확성 검사기"""
    
    @staticmethod
    def check_terms(text: str) -> Dict[str, Any]:
        """
        법률 용어 정확성을 검사합니다.
        
        Args:
            text: 검사할 텍스트
            
        Returns:
            검사 결과
        """
        issues = []
        suggestions = {}
        
        # 용어 사전과 비교
        for term, definition in StyleValidator.LEGAL_TERMS.items():
            if term in text:
                # 용어 사용 확인
                pass
        
        # 잘못된 용어 사용 검사
        for correct_term, mistakes in StyleValidator.COMMON_MISTAKES.items():
            for mistake in mistakes:
                if mistake in text:
                    issues.append({
                        "term": mistake,
                        "correct": correct_term,
                        "position": text.find(mistake),
                    })
                    suggestions[mistake] = correct_term
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
        }
    
    @staticmethod
    def suggest_corrections(text: str) -> str:
        """
        텍스트의 용어를 수정 제안합니다.
        
        Args:
            text: 수정할 텍스트
            
        Returns:
            수정 제안 텍스트
        """
        corrected = text
        
        for mistake, correct in StyleValidator.COMMON_MISTAKES.items():
            for wrong_term in StyleValidator.COMMON_MISTAKES[mistake]:
                corrected = corrected.replace(wrong_term, correct)
        
        return corrected


class GrammarValidator:
    """문법 및 형식 검증기"""
    
    @staticmethod
    def validate(text: str) -> Dict[str, Any]:
        """
        문법 및 형식을 검증합니다.
        
        Args:
            text: 검증할 텍스트
            
        Returns:
            검증 결과
        """
        issues = []
        
        # 기본 문법 검사
        grammar_issues = StyleValidator._check_grammar(text)
        issues.extend(grammar_issues)
        
        # 형식 검사
        format_issues = StyleValidator._check_format(text)
        issues.extend(format_issues)
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }

