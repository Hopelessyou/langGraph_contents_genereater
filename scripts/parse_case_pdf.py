"""판례 PDF를 JSON 파일로 변환하는 스크립트"""

import re
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


class CasePDFParser:
    """판례 PDF 파서"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def parse_pdf_text(self, pdf_path: Path) -> str:
        """
        PDF 파일을 텍스트로 변환합니다.
        PyPDF2 실패 시 pdfplumber로 자동 전환합니다.
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            PDF 텍스트 내용
        """
        # 방법 1: PyPDF2 시도
        try:
            import PyPDF2
            text = ""
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            if text.strip():  # 텍스트가 추출되었는지 확인
                return text
            else:
                logger.warning(f"PyPDF2로 텍스트를 추출하지 못했습니다. pdfplumber로 시도합니다.")
                raise ValueError("PyPDF2 failed to extract text")
                
        except (ImportError, Exception) as e:
            if isinstance(e, ImportError):
                logger.warning("PyPDF2가 설치되지 않았습니다. pdfplumber로 시도합니다.")
            else:
                logger.warning(f"PyPDF2 오류 발생 ({str(e)}). pdfplumber로 시도합니다.")
        
        # 방법 2: pdfplumber 시도 (fallback)
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if text.strip():
                logger.info("pdfplumber로 텍스트 추출 성공")
                return text
            else:
                raise ValueError("pdfplumber failed to extract text")
                
        except ImportError:
            logger.error("pdfplumber가 설치되지 않았습니다. 'pip install pdfplumber'를 실행하세요.")
            raise
        except Exception as e:
            logger.error(f"pdfplumber 오류 발생: {str(e)}")
            # 방법 3: pymupdf (fitz) 시도 (최종 fallback)
            try:
                import fitz  # pymupdf
                text = ""
                doc = fitz.open(pdf_path)
                for page in doc:
                    page_text = page.get_text()
                    if page_text:
                        text += page_text + "\n"
                doc.close()
                
                if text.strip():
                    logger.info("pymupdf로 텍스트 추출 성공")
                    return text
                else:
                    raise ValueError("pymupdf failed to extract text")
                    
            except ImportError:
                logger.error("pymupdf가 설치되지 않았습니다. 'pip install pymupdf'를 실행하세요.")
                raise
            except Exception as e2:
                logger.error(f"모든 PDF 라이브러리 실패: PyPDF2, pdfplumber, pymupdf 모두 실패")
                raise Exception(f"PDF 텍스트 추출 실패: {str(e2)}")
    
    def extract_case_number(self, text: str, pdf_path: Path = None) -> Optional[str]:
        """
        사건번호를 추출합니다.
        
        Args:
            text: PDF 텍스트
            pdf_path: PDF 파일 경로 (파일명에서 사건번호 추출 시도)
            
        Returns:
            사건번호 (예: "2023도11234")
        """
        # 1. 파일명에서 사건번호 추출 시도 (우선순위 1)
        if pdf_path:
            filename = pdf_path.stem  # 확장자 제거
            # 패턴: "판례_2012노856", "2010도12928", "판례-2012노856", "2016고합209" 등
            filename_patterns = [
                r'(\d{4}고합\d+)',  # 하급심 형사합의: 2016고합209
                r'(\d{4}고단\d+)',  # 하급심 형사단독: 2016고단123
                r'(\d{4}고기\d+)',  # 하급심 형사기소: 2016고기456
                r'(\d{4}초기\d+)',  # 하급심 형사기소: 2016초기1295
                r'(\d{4}[도나가다라마바사아자차카타노]\d+)',  # 2012노856, 2010도12928
                r'판례[_-]?(\d{4}[도나가다라마바사아자차카타노]\d+)',  # 판례_2012노856
            ]
            
            for pattern in filename_patterns:
                match = re.search(pattern, filename)
                if match:
                    case_number = match.group(1)
                    logger.info(f"파일명에서 사건번호 추출: {case_number}")
                    return case_number
        
        # 2. PDF 텍스트에서 사건번호 추출 (우선순위 2)
        # 사건번호 패턴: 연도 + 법원코드 + 번호
        # 예: "2023도11234", "2023가단12345", "2023나12345", "2012노856"
        # 하급심: "2016고합209", "2016고단123", "2016고기456", "2016초기1295"
        patterns = [
            r'(\d{4}노\d+)',  # 항소: 2012노856 (파일명과 일치하는 경우 우선)
            r'(\d{4}도\d+)',  # 형사: 2023도11234
            r'(\d{4}고합\d+)',  # 형사합의: 2016고합209 (하급심)
            r'(\d{4}고단\d+)',  # 형사단독: 2016고단123 (하급심)
            r'(\d{4}고기\d+)',  # 형사기소: 2016고기456 (하급심)
            r'(\d{4}초기\d+)',  # 형사기소: 2016초기1295 (하급심)
            r'(\d{4}가단\d+)',  # 가사: 2023가단12345
            r'(\d{4}나\d+)',  # 민사: 2023나12345
            r'(\d{4}다\d+)',  # 행정: 2023다12345
            r'(\d{4}라\d+)',  # 특허: 2023라12345
            r'(\d{4}마\d+)',  # 조세: 2023마12345
            r'(\d{4}바\d+)',  # 선거: 2023바12345
            r'(\d{4}사\d+)',  # 지방자치: 2023사12345
            r'(\d{4}아\d+)',  # 노동: 2023아12345
            r'(\d{4}자\d+)',  # 해상: 2023자12345
            r'(\d{4}차\d+)',  # 건설: 2023차12345
            r'(\d{4}카\d+)',  # 금융: 2023카12345
            r'(\d{4}타\d+)',  # 기타: 2023타12345
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text[:2000])  # 앞부분에서 검색
            if match:
                case_number = match.group(1)
                logger.info(f"텍스트에서 사건번호 추출: {case_number}")
                return case_number
        
        logger.warning("사건번호를 찾을 수 없습니다.")
        return None
    
    def extract_court(self, text: str, case_number: Optional[str] = None) -> str:
        """
        법원명을 추출합니다.
        
        Args:
            text: PDF 텍스트
            case_number: 사건번호 (법원 추론에 사용)
            
        Returns:
            법원명 (기본값: "대법원")
        """
        # 사건번호로 법원 추론
        if case_number:
            # "노"는 고등법원 항소사건
            if "노" in case_number:
                # 고등법원 패턴 찾기
                high_court_patterns = [
                    r'서울고등법원',
                    r'부산고등법원',
                    r'대전고등법원',
                    r'대구고등법원',
                    r'광주고등법원',
                ]
                for pattern in high_court_patterns:
                    match = re.search(pattern, text[:2000])
                    if match:
                        court = match.group(0)
                        logger.info(f"사건번호와 텍스트로 법원명 추출: {court}")
                        return court
                # 고등법원을 찾지 못하면 기본값
                logger.info("고등법원을 찾을 수 없어 기본값 '대법원'을 사용합니다.")
                return "대법원"
        
        # 법원명 패턴
        courts = [
            "대법원 전원합의체",
            "대법원",
            "서울고등법원",
            "부산고등법원",
            "대전고등법원",
            "대구고등법원",
            "광주고등법원",
            "서울중앙지방법원",
            "서울동부지방법원",
            "서울서부지방법원",
            "서울남부지방법원",
            "서울북부지방법원",
            "고등군사법원",
            "광주지방법원",
            "대구지법",
            "부산지법",
            "대전지법",
            "인천지법",
            "울산지방법원",
            "의정부지방법원",
            "청주지방법원",
            "천안지방법원",
            "춘천지방법원",
            "충주지방법원",
            "전주지방법원",
            "전남지방법원",
            "전북지방법원",
            "제주지방법원",
            "제주도지방법원",
            "제주도지방법원"
        ]
        
        for court in courts:
            if court in text[:2000]:  # 앞부분에서 검색 범위 확대
                logger.info(f"법원명 추출: {court}")
                return court
        
        logger.info("법원명을 찾을 수 없어 기본값 '대법원'을 사용합니다.")
        return "대법원"
    
    def extract_year(self, text: str, case_number: Optional[str] = None, judgment_date: Optional[str] = None) -> Optional[int]:
        """
        판결 연도를 추출합니다.
        
        Args:
            text: PDF 텍스트
            case_number: 사건번호 (연도 추출에 사용)
            judgment_date: 판결일 (YYYY-MM-DD 형식, 우선순위 1)
            
        Returns:
            연도 (예: 2023)
        """
        # 1. 판결일에서 연도 추출 (최우선)
        if judgment_date:
            match = re.match(r'(\d{4})', judgment_date)
            if match:
                year = int(match.group(1))
                if 2000 <= year <= datetime.now().year:
                    logger.info(f"판결일에서 연도 추출: {year}")
                    return year
        
        # 2. 사건번호에서 연도 추출
        if case_number:
            match = re.match(r'(\d{4})', case_number)
            if match:
                year = int(match.group(1))
                if 2000 <= year <= datetime.now().year:
                    logger.info(f"사건번호에서 연도 추출: {year}")
                    return year
        
        # 3. 텍스트에서 판결일 패턴으로 연도 검색
        date_patterns = [
            r'(\d{4})\.\s*\d{1,2}\.\s*\d{1,2}\.\s*선고',  # 2017. 2. 17. 선고
            r'(\d{4})년\s*\d{1,2}월\s*\d{1,2}일',  # 2023년 1월 1일
            r'판결\s*:\s*(\d{4})',  # 판결: 2023
            r'선고\s*:\s*(\d{4})',  # 선고: 2023
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text[:3000])  # 검색 범위 확대
            if match:
                year = int(match.group(1))
                if 2000 <= year <= datetime.now().year:
                    logger.info(f"텍스트에서 연도 추출: {year}")
                    return year
        
        # 현재 연도 사용
        current_year = datetime.now().year
        logger.warning(f"연도를 찾을 수 없어 현재 연도 {current_year}를 사용합니다.")
        return current_year
    
    def extract_judgment_date(self, text: str) -> Optional[str]:
        """
        판결일을 추출합니다.
        
        Args:
            text: PDF 텍스트
            
        Returns:
            판결일 (YYYY-MM-DD 형식) 또는 None
        """
        # 판결일 패턴: "2010. 12. 9." 또는 "2010년 12월 9일"
        date_patterns = [
            r'(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.',  # 2010. 12. 9.
            r'(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일',  # 2010년 12월 9일
            r'판결일[:\s]*(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})',  # 판결일: 2010. 12. 9
            r'선고일[:\s]*(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})',  # 선고일: 2010. 12. 9
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text[:3000])
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3))
                
                if 2000 <= year <= datetime.now().year and 1 <= month <= 12 and 1 <= day <= 31:
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    logger.info(f"판결일 추출: {date_str}")
                    return date_str
        
        logger.warning("판결일을 찾을 수 없습니다.")
        return None
    
    def extract_panji_items(self, text: str) -> List[str]:
        """
        판시사항을 추출합니다.
        
        Args:
            text: PDF 텍스트
            
        Returns:
            판시사항 리스트
        """
        panji_items = []
        
        # 【판시사항】 섹션 찾기
        panji_pattern = r'【?\s*판시사항\s*】?[:\s]*\n?(.+?)(?=\n\n|\n【|$)'
        match = re.search(panji_pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:
            panji_section = match.group(1)
            
            # [1], [2] 등으로 번호가 매겨진 항목 추출
            item_pattern = r'\[(\d+)\]\s*(.+?)(?=\n\s*\[|\n\n|$)'
            items = re.findall(item_pattern, panji_section, re.DOTALL)
            
            for num, content in items:
                item_text = f"[{num}] {content.strip()}"
                # 너무 긴 경우 앞부분만 사용
                if len(item_text) > 500:
                    item_text = item_text[:500] + "..."
                panji_items.append(item_text)
            
            if panji_items:
                logger.info(f"판시사항 {len(panji_items)}개 추출 완료")
            else:
                # 번호가 없는 경우 전체 섹션을 하나의 항목으로
                panji_text = panji_section.strip()
                if len(panji_text) > 1000:
                    panji_text = panji_text[:1000] + "..."
                if panji_text:
                    panji_items.append(panji_text)
                    logger.info("판시사항 1개 추출 완료 (번호 없음)")
        else:
            # 고등법원 판결의 경우 판시사항 섹션이 없을 수 있음
            # 텍스트에서 판시사항 패턴 직접 찾기 시도
            # "판시사항", "판시", "요지" 등의 키워드가 있는 문장 찾기
            panji_keywords = ['판시사항', '판시', '요지']
            found_any = False
            
            for keyword in panji_keywords:
                if keyword in text[:1000]:
                    found_any = True
                    break
            
            if not found_any:
                logger.debug("판시사항 섹션을 찾을 수 없습니다. (고등법원 판결의 경우 정상일 수 있습니다)")
            else:
                logger.warning("판시사항 섹션을 찾을 수 없습니다.")
        
        return panji_items
    
    def extract_reference_articles(self, text: str) -> List[str]:
        """
        참조조문을 추출합니다.
        
        Args:
            text: PDF 텍스트
            
        Returns:
            참조조문 리스트
        """
        articles = []
        seen_articles = set()  # 중복 제거용
        
        # 【참조조문】 섹션 찾기
        ref_pattern = r'【?\s*참조조문\s*】?[:\s]*\n?(.+?)(?=\n\n|\n【|$)'
        match = re.search(ref_pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:
            ref_section = match.group(1)
            
            # [1], [2] 등으로 번호가 매겨진 항목 추출
            item_pattern = r'\[(\d+)\]\s*(.+?)(?=\n\s*\[|\n\n|$)'
            items = re.findall(item_pattern, ref_section, re.DOTALL)
            
            for num, content in items:
                article_text = content.strip()
                if article_text and article_text not in seen_articles:
                    articles.append(article_text)
                    seen_articles.add(article_text)
            
            if not articles:
                # 번호가 없는 경우 조문 패턴으로 추출
                article_patterns = [
                    r'형법\s*제\d+조',
                    r'특정경제범죄\s*가중처벌\s*등에\s*관한\s*법률\s*제\d+조',
                    r'형사소송법\s*제\d+조',
                    r'민법\s*제\d+조',
                    r'제\d+조',
                ]
                
                for pattern in article_patterns:
                    matches = re.findall(pattern, ref_section)
                    for match_text in matches:
                        if match_text not in seen_articles:
                            articles.append(match_text)
                            seen_articles.add(match_text)
            
            if articles:
                logger.info(f"참조조문 {len(articles)}개 추출 완료")
        else:
            # 섹션이 없는 경우 텍스트 전체에서 조문 패턴 찾기
            article_patterns = [
                r'형법\s*제\d+조',
                r'특정경제범죄\s*가중처벌\s*등에\s*관한\s*법률\s*제\d+조',
                r'형사소송법\s*제\d+조',
            ]
            
            for pattern in article_patterns:
                matches = re.findall(pattern, text)
                for match_text in matches:
                    if match_text not in seen_articles:
                        articles.append(match_text)
                        seen_articles.add(match_text)
            
            if articles:
                logger.info(f"참조조문 {len(articles)}개 추출 완료 (텍스트에서 직접 추출)")
            else:
                logger.debug("참조조문을 찾을 수 없습니다. (고등법원 판결의 경우 정상일 수 있습니다)")
        
        return articles
    
    def extract_reference_cases(self, text: str) -> List[str]:
        """
        참조판례를 추출합니다.
        
        Args:
            text: PDF 텍스트
            
        Returns:
            참조판례 리스트
        """
        cases = []
        seen_cases = set()  # 중복 제거용
        
        # 【참조판례】 섹션 찾기
        ref_pattern = r'【?\s*참조판례\s*】?[:\s]*\n?(.+?)(?=\n\n|\n【|$)'
        match = re.search(ref_pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:
            ref_section = match.group(1)
            
            # 판례 패턴: "대법원 2007. 4. 19. 선고 2005도7288 전원합의체 판결"
            case_patterns = [
                r'대법원\s*\d{4}\.\s*\d{1,2}\.\s*\d{1,2}\.\s*선고\s*\d{4}[도나가다라마바사아자차카타]\d+\s*[^/]+',
                r'대법원\s*\d{4}\.\s*\d{1,2}\.\s*\d{1,2}\.\s*선고\s*\d{4}[도나가다라마바사아자차카타]\d+',
                r'서울고등법원\s*\d{4}\.\s*\d{1,2}\.\s*\d{1,2}\.\s*선고\s*\d{4}[도나가다라마바사아자차카타]\d+',
                r'부산고등법원\s*\d{4}\.\s*\d{1,2}\.\s*\d{1,2}\.\s*선고\s*\d{4}[도나가다라마바사아자차카타]\d+',
            ]
            
            for pattern in case_patterns:
                matches = re.findall(pattern, ref_section)
                for case in matches:
                    case_clean = case.strip()
                    if case_clean and case_clean not in seen_cases:
                        cases.append(case_clean)
                        seen_cases.add(case_clean)
            
            if cases:
                logger.info(f"참조판례 {len(cases)}개 추출 완료")
        else:
            # 섹션이 없는 경우 텍스트 전체에서 판례 패턴 찾기
            case_patterns = [
                r'대법원\s*\d{4}\.\s*\d{1,2}\.\s*\d{1,2}\.\s*선고\s*\d{4}[도나가다라마바사아자차카타]\d+',
                r'서울고등법원\s*\d{4}\.\s*\d{1,2}\.\s*\d{1,2}\.\s*선고\s*\d{4}[도나가다라마바사아자차카타]\d+',
            ]
            
            for pattern in case_patterns:
                matches = re.findall(pattern, text)
                for case in matches:
                    case_clean = case.strip()
                    if case_clean and case_clean not in seen_cases:
                        cases.append(case_clean)
                        seen_cases.add(case_clean)
            
            if cases:
                logger.info(f"참조판례 {len(cases)}개 추출 완료 (텍스트에서 직접 추출)")
            else:
                logger.debug("참조판례를 찾을 수 없습니다. (고등법원 판결의 경우 정상일 수 있습니다)")
        
        return cases
    
    def extract_holding(self, text: str, judgment_section: str = "") -> str:
        """
        판결 요지를 추출하고 정리합니다.
        하급심 판례의 경우 판결 요지 섹션이 없을 수 있으므로,
        판단 섹션의 요약을 사용합니다.
        
        Args:
            text: PDF 텍스트
            judgment_section: 판단 섹션 내용 (하급심 판례용)
            
        Returns:
            정리된 판결 요지
        """
        # 판결 요지 섹션 찾기
        holding_patterns = [
            r'【?\s*판결\s*요지\s*】?[:\s]*\n?(.+?)(?=\n\n|\n【|$)',
            r'【?\s*요\s*지\s*】?[:\s]*\n?(.+?)(?=\n\n|\n【|$)',
        ]
        
        for pattern in holding_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                holding = match.group(1).strip()
                # 정제
                holding = self.clean_section_content(holding)
                if holding:
                    # 너무 긴 경우 앞부분만 사용
                    if len(holding) > 1000:
                        holding = holding[:1000] + "..."
                    logger.info(f"판결 요지 추출 완료 (길이: {len(holding)})")
                    return holding
        
        # 하급심 판례: 판결 요지가 없을 경우 판단 섹션의 요약 사용
        if judgment_section:
            # 판단 섹션의 첫 부분을 요지로 사용 (최대 500자)
            holding = judgment_section.strip()
            holding = self.clean_section_content(holding)
            if holding:
                # 첫 문단 또는 첫 3-5문장 추출
                sentences = re.split(r'[。.\n]', holding)
                if len(sentences) > 1:
                    # 첫 3-5문장을 요지로 사용
                    holding_summary = '. '.join(sentences[:5]).strip()
                    if len(holding_summary) > 500:
                        holding_summary = holding_summary[:500] + "..."
                    logger.info(f"판단 섹션에서 판결 요지 추출 완료 (길이: {len(holding_summary)})")
                    return holding_summary
                elif len(holding) > 500:
                    holding = holding[:500] + "..."
                    logger.info(f"판단 섹션에서 판결 요지 추출 완료 (길이: {len(holding)})")
                    return holding
        
        logger.warning("판결 요지를 찾을 수 없습니다.")
        return ""
    
    def extract_case_overview(self, text: str) -> str:
        """
        사건 개요를 추출하고 정리합니다.
        
        Args:
            text: PDF 텍스트
            
        Returns:
            정리된 사건 개요 내용
        """
        # 【사건 개요】 또는 【전문】 섹션 찾기
        overview_patterns = [
            r'【?\s*사건\s*개요\s*】?[:\s]*\n?(.+?)(?=\n\n|\n【|$)',
            r'【?\s*전문\s*】?[:\s]*\n?(.+?)(?=\n\n|\n【|$)',
        ]
        
        for pattern in overview_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                overview = match.group(1).strip()
                
                # 피고인, 상고인, 변호인, 원심판결 정보 추출
                extracted_info = {}
                
                # 【피고인】, 【상고인】, 【변호인】, 【원심판결】 패턴으로 추출
                info_patterns = [
                    (r'【피\s*고\s*인】\s*(.+?)(?=\n【|$)', '피고인'),
                    (r'【상\s*고\s*인】\s*(.+?)(?=\n【|$)', '상고인'),
                    (r'【변\s*호\s*인】\s*(.+?)(?=\n【|$)', '변호인'),
                    (r'【원심\s*판결】\s*(.+?)(?=\n【|$)', '원심판결'),
                    (r'【주\s*문】\s*(.+?)(?=\n【|$)', '주문'),
                ]
                
                for pattern, label in info_patterns:
                    info_match = re.search(pattern, overview, re.DOTALL | re.IGNORECASE)
                    if info_match:
                        info_content = info_match.group(1).strip()
                        info_content = self.clean_section_content(info_content)
                        if info_content and len(info_content) > 3:  # 너무 짧은 내용 제외
                            extracted_info[label] = info_content
                
                # 추출된 정보를 구조화
                if extracted_info:
                    overview_parts = []
                    for label, content in extracted_info.items():
                        overview_parts.append(f"{label}: {content}")
                    result = "\n".join(overview_parts)
                    result = self.clean_section_content(result)
                    logger.info("사건 개요 추출 완료")
                    return result
                else:
                    # 패턴을 찾지 못한 경우 전체 섹션 정제 후 반환
                    cleaned_overview = self.clean_section_content(overview)
                    if cleaned_overview and len(cleaned_overview) > 20:
                        logger.info("사건 개요 추출 완료 (전체 섹션)")
                        return cleaned_overview
        
        logger.warning("사건 개요 섹션을 찾을 수 없습니다.")
        return ""
    
    def extract_judgment_section(self, text: str) -> str:
        """
        판단 섹션을 추출하고 정리합니다.
        하급심 판례의 경우 판단 섹션이 매우 길 수 있습니다.
        
        Args:
            text: PDF 텍스트
            
        Returns:
            정리된 판단 내용
        """
        # 판단 섹션 찾기 (여러 패턴 시도, 하급심 패턴 포함)
        judgment_patterns = [
            r'【?\s*판\s*단\s*】?[:\s]*\n?(.+?)(?=\n\n|\n【|$)',
            r'【?\s*이\s*유\s*】?[:\s]*\n?(.+?)(?=\n\n|\n【|$)',
            r'【?\s*당심\s*의\s*판단\s*】?[:\s]*\n?(.+?)(?=\n\n|\n【|$)',
            r'【?\s*판\s*단\s*및\s*이\s*유\s*】?[:\s]*\n?(.+?)(?=\n\n|\n【|$)',  # 하급심 패턴
            r'【?\s*이\s*유\s*】?\s*[:\s]*\n?(.+?)(?=\n\n|\n【|$)',  # 하급심: 이유만 있는 경우
        ]
        
        for pattern in judgment_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                judgment = match.group(1).strip()
                # 정제
                judgment = self.clean_section_content(judgment)
                if judgment and len(judgment) > 50:  # 최소 길이 확인
                    # 하급심 판례는 판단이 매우 길 수 있으므로 최대 5000자까지 허용
                    if len(judgment) > 5000:
                        # 문장 단위로 자르기
                        sentences = re.split(r'[。.\n]', judgment)
                        judgment = '. '.join(sentences[:100])  # 최대 100문장
                        if len(judgment) > 5000:
                            judgment = judgment[:5000] + "..."
                    logger.info(f"판단 섹션 추출 완료 (길이: {len(judgment)})")
                    return judgment
        
        # 판단 섹션을 찾지 못한 경우, "【판단】" 또는 "【이유】" 키워드 이후의 텍스트 사용
        # (하급심 판례는 섹션 헤더가 없을 수 있음)
        judgment_keywords = ['판단', '이유', '당심의 판단']
        for keyword in judgment_keywords:
            keyword_pos = text.find(keyword)
            if keyword_pos > 0:
                # 키워드 이후의 텍스트 추출 (최대 5000자)
                potential_judgment = text[keyword_pos + len(keyword):keyword_pos + 5000].strip()
                potential_judgment = self.clean_section_content(potential_judgment)
                if potential_judgment and len(potential_judgment) > 100:
                    logger.info(f"키워드 '{keyword}' 이후 텍스트에서 판단 섹션 추출 완료 (길이: {len(potential_judgment)})")
                    return potential_judgment
        
        return ""
    
    def extract_issue_section(self, text: str) -> str:
        """
        쟁점 섹션을 추출하고 정리합니다.
        
        Args:
            text: PDF 텍스트
            
        Returns:
            정리된 쟁점 내용
        """
        issue_match = re.search(
            r'【?\s*쟁\s*점\s*】?[:\s]*\n?(.+?)(?=\n\n|\n【|$)',
            text,
            re.DOTALL | re.IGNORECASE
        )
        if issue_match:
            issue = issue_match.group(1).strip()
            issue = self.clean_section_content(issue)
            if issue and len(issue) > 20:
                return issue
        return ""
    
    def extract_content(self, text: str, judgment_section: str = "") -> str:
        """
        판례 내용을 추출하고 정리합니다.
        하급심 판례의 경우 판단 섹션이 매우 중요합니다.
        
        Args:
            text: PDF 텍스트
            judgment_section: 이미 추출된 판단 섹션 (중복 추출 방지)
            
        Returns:
            정리된 판례 내용
        """
        # 각 섹션을 개별적으로 추출
        sections_dict = {}
        
        # 1. 사건 개요 추출
        overview = self.extract_case_overview(text)
        if overview:
            sections_dict["overview"] = overview
        
        # 2. 쟁점 추출
        issue = self.extract_issue_section(text)
        if issue:
            sections_dict["issue"] = issue
        
        # 3. 판단 추출 (이미 추출된 경우 재사용, 없으면 새로 추출)
        if judgment_section:
            judgment = judgment_section
        else:
            judgment = self.extract_judgment_section(text)
        if judgment:
            sections_dict["judgment"] = judgment
        
        # 4. 판결 요지 추출 (판단 섹션을 사용하여 요지 생성)
        holding = self.extract_holding(text, judgment if judgment else "")
        if holding:
            sections_dict["holding"] = holding
        
        # 섹션들을 구조화된 형식으로 정리
        if sections_dict:
            formatted_content = self.format_content_sections(sections_dict)
            if formatted_content:
                return formatted_content
        
        # 섹션을 찾지 못한 경우 전체 텍스트 사용 (처음 5000자)
        content = text[:5000].strip()
        content = self.clean_section_content(content)
        logger.warning("주요 섹션을 찾지 못해 전체 텍스트 일부를 사용합니다.")
        return content
    
    def clean_content(self, content: str) -> str:
        """내용 정제"""
        # 불필요한 공백 제거
        content = re.sub(r'\s+', ' ', content)
        # 줄바꿈 정리
        content = re.sub(r'\n\s*\n+', '\n\n', content)
        # 앞뒤 공백 제거
        content = content.strip()
        return content
    
    def format_content_sections(self, sections: Dict[str, str]) -> str:
        """
        추출된 섹션들을 구조화된 형식으로 정리합니다.
        
        Args:
            sections: 섹션별 내용 딕셔너리
                {
                    "overview": "...",
                    "issue": "...",
                    "judgment": "...",
                    "holding": "..."
                }
        
        Returns:
            정리된 content 문자열
        """
        formatted_parts = []
        
        # 1. 사건 개요
        if sections.get("overview"):
            overview = self.clean_section_content(sections["overview"])
            if overview:
                formatted_parts.append(f"【사건 개요】\n{overview}")
        
        # 2. 쟁점
        if sections.get("issue"):
            issue = self.clean_section_content(sections["issue"])
            if issue:
                formatted_parts.append(f"【쟁점】\n{issue}")
        
        # 3. 판단
        if sections.get("judgment"):
            judgment = self.clean_section_content(sections["judgment"])
            if judgment:
                formatted_parts.append(f"【판단】\n{judgment}")
        
        # 4. 판결 요지
        if sections.get("holding"):
            holding = self.clean_section_content(sections["holding"])
            if holding:
                formatted_parts.append(f"【판결 요지】\n{holding}")
        
        if formatted_parts:
            return "\n\n".join(formatted_parts)
        
        return ""
    
    def clean_section_content(self, content: str) -> str:
        """
        섹션 내용을 정제합니다.
        
        Args:
            content: 원본 섹션 내용
            
        Returns:
            정제된 내용
        """
        if not content:
            return ""
        
        # 1. 불필요한 헤더/푸터 제거
        # 법제처, 국가법령정보센터 등 제거
        content = re.sub(r'법제처\s*\d+\s*국가법령정보센터[^\n]*', '', content)
        content = re.sub(r'국가법령정보센터[^\n]*', '', content)
        content = re.sub(r'\"[^\"]*\"\s*\(판례[^)]*\)', '', content)
        content = re.sub(r'\(판례[^)]*\)', '', content)
        
        # 2. 섹션 헤더 중복 제거
        content = re.sub(r'^【?\s*사건\s*개요\s*】?[:\s]*\n?', '', content, flags=re.IGNORECASE | re.MULTILINE)
        content = re.sub(r'^【?\s*쟁\s*점\s*】?[:\s]*\n?', '', content, flags=re.IGNORECASE | re.MULTILINE)
        content = re.sub(r'^【?\s*판\s*단\s*】?[:\s]*\n?', '', content, flags=re.IGNORECASE | re.MULTILINE)
        content = re.sub(r'^【?\s*판결\s*요지\s*】?[:\s]*\n?', '', content, flags=re.IGNORECASE | re.MULTILINE)
        
        # 3. 불완전한 섹션 제거
        # "【피 고 인】" 같은 불완전한 섹션만 있는 경우 제거
        content = re.sub(r'^【[^】]+】\s*$', '', content, flags=re.MULTILINE)
        # "【피 고 인】 피고인" 같은 단순 반복 제거
        content = re.sub(r'【피\s*고\s*인】\s*피고인\s*', '', content, flags=re.IGNORECASE)
        
        # 4. 문장 부호 정리
        # 연속된 마침표 제거 (.. -> .)
        content = re.sub(r'\.{2,}', '.', content)
        # 마침표 앞 공백 제거 (단, 숫자 뒤는 제외)
        content = re.sub(r'([^0-9])\s+\.', r'\1.', content)
        # 마침표 뒤 공백 정리 (한 칸만, 줄바꿈 제외)
        content = re.sub(r'\.\s+([^\n])', r'. \1', content)
        # 연속된 공백을 하나로
        content = re.sub(r' {2,}', ' ', content)
        
        # 5. 날짜 형식 정리
        # "2008. 9. 8. 경" -> "2008. 9. 8.경"
        content = re.sub(r'(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.\s+경', r'\1. \2. \3.경', content)
        # "2008. 9. 8." -> "2008. 9. 8."
        content = re.sub(r'(\d{4})\.\s+(\d{1,2})\.\s+(\d{1,2})\.', r'\1. \2. \3.', content)
        # "2011. 1. 경" -> "2011. 1.경"
        content = re.sub(r'(\d{4})\.\s*(\d{1,2})\.\s+경', r'\1. \2.경', content)
        
        # 6. 항목 표시 정리 (가., 나., 다. 등)
        # "가 피해자" -> "가. 피해자"
        content = re.sub(r'\b([가-힣])\s+([가-힣])', r'\1. \2', content)
        # 단, 이미 마침표가 있는 경우는 제외
        content = re.sub(r'([가-힣])\.\s*\.', r'\1.', content)
        
        # 6. 불필요한 공백 정리
        content = re.sub(r'[ \t]+', ' ', content)  # 탭과 공백을 하나의 공백으로
        content = re.sub(r'\n[ \t]+', '\n', content)  # 줄 시작 공백 제거
        content = re.sub(r'[ \t]+\n', '\n', content)  # 줄 끝 공백 제거
        content = re.sub(r'\n{3,}', '\n\n', content)  # 3개 이상 줄바꿈을 2개로
        
        # 7. 불필요한 텍스트 패턴 제거
        # "법제처 3" 같은 패턴
        content = re.sub(r'법제처\s*\d+', '', content)
        # 페이지 번호 같은 패턴
        content = re.sub(r'\n\s*\d+\s*\n', '\n', content)
        
        # 8. 문장이 이상하게 끊어진 경우 수정
        # "사실을. 오인하거나" -> "사실을 오인하거나"
        content = re.sub(r'([가-힣])\s*\.\s*([가-힣])', r'\1 \2', content)
        
        # 9. 앞뒤 공백 제거
        content = content.strip()
        
        # 10. 너무 짧은 내용 제거 (10자 미만)
        if len(content) < 10:
            return ""
        
        return content
    
    def extract_keywords(self, text: str, sub_category: str = "") -> list[str]:
        """
        키워드를 추출합니다.
        
        Args:
            text: PDF 텍스트
            sub_category: 하위 카테고리
            
        Returns:
            키워드 리스트
        """
        keywords = []
        
        # 하위 카테고리를 키워드에 추가
        if sub_category:
            keywords.append(sub_category)
        
        # 일반적인 법률 키워드
        common_keywords = [
            "사기", "절도", "강도", "살인", "폭행", "협박",
            "초범", "재범", "집행유예", "실형", "벌금",
            "피해회복", "반성", "양형", "가중처벌",
        ]
        
        for keyword in common_keywords:
            if keyword in text and keyword not in keywords:
                keywords.append(keyword)
        
        return keywords[:5]  # 최대 5개
    
    def determine_category(self, text: str) -> tuple[str, str]:
        """
        카테고리와 하위 카테고리를 결정합니다.
        
        Args:
            text: PDF 텍스트
            
        Returns:
            (category, sub_category) 튜플
        """
        # 형사 관련 키워드
        criminal_keywords = {
            "사기": ["사기", "편취", "기망"],
            "절도": ["절도", "절취"],
            "강도": ["강도", "강취"],
            "살인": ["살인", "고의"],
            "폭행": ["폭행", "상해"],
            "초범": ["초범", "전과"],
            "집행유예": ["집행유예", "유예"],
        }
        
        # 민사 관련 키워드
        civil_keywords = {
            "계약": ["계약", "해제", "해지"],
            "손해배상": ["손해배상", "배상"],
            "임대차": ["임대차", "임차"],
        }
        
        # 형사 판례인지 확인
        for sub_cat, keywords in criminal_keywords.items():
            if any(kw in text[:2000] for kw in keywords):
                return ("형사", sub_cat)
        
        # 민사 판례인지 확인
        for sub_cat, keywords in civil_keywords.items():
            if any(kw in text[:2000] for kw in keywords):
                return ("민사", sub_cat)
        
        # 기본값
        return ("형사", "")
    
    def create_case_json(
        self,
        court: str,
        case_number: Optional[str],
        year: int,
        content: str,
        holding: str,
        category: str,
        sub_category: str,
        keywords: list[str],
        judgment_date: Optional[str] = None,
        panji_items: Optional[List[str]] = None,
        reference_articles: Optional[List[str]] = None,
        reference_cases: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        판례 데이터를 JSON 형식으로 변환합니다.
        
        Args:
            court: 법원명
            case_number: 사건번호
            year: 판결 연도
            content: 판례 내용
            holding: 판결 요지
            category: 카테고리
            sub_category: 하위 카테고리
            keywords: 키워드 리스트
            judgment_date: 판결일 (YYYY-MM-DD)
            panji_items: 판시사항 리스트
            reference_articles: 참조조문 리스트
            reference_cases: 참조판례 리스트
            
        Returns:
            JSON 형식의 판례 데이터
        """
        # ID 생성
        if case_number:
            doc_id = f"case-{case_number}"
        else:
            doc_id = f"case-{court}-{year}-{sub_category or 'unknown'}"
        
        # 제목 생성
        if case_number:
            title = f"{court} {case_number} 판결"
        else:
            title = f"{court} {year}년 {sub_category or ''} 판결"
        
        # 메타데이터 구성
        metadata = {
            "court": court,
            "year": year,
            "case_number": case_number or "",
            "keywords": keywords,
            "holding": holding,
            "updated_at": datetime.now().strftime("%Y-%m-%d"),
        }
        
        # 판결일 추가
        if judgment_date:
            metadata["judgment_date"] = judgment_date
        
        # 판시사항 추가
        if panji_items:
            metadata["panji_items"] = panji_items
        
        # 참조조문 추가
        if reference_articles:
            metadata["reference_articles"] = reference_articles
        
        # 참조판례 추가
        if reference_cases:
            metadata["reference_cases"] = reference_cases
        
        return {
            "id": doc_id,
            "category": category,
            "sub_category": sub_category,
            "type": "case",
            "title": title,
            "content": content,
            "metadata": metadata,
        }
    
    def save_case(self, case_data: Dict[str, Any]) -> Path:
        """
        판례를 JSON 파일로 저장합니다.
        
        Args:
            case_data: 판례 데이터
            
        Returns:
            저장된 파일 경로
        """
        # 파일명: "case-2023도11234.json"
        filename = f"{case_data['id']}.json"
        file_path = self.output_dir / filename
        
        # JSON 파일 저장
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(case_data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def parse_and_save(self, pdf_path: Path) -> Optional[Path]:
        """
        PDF를 파싱하여 JSON 파일로 저장합니다.
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            저장된 파일 경로
        """
        logger.info(f"판례 PDF 파싱 시작: {pdf_path}")
        
        # PDF 텍스트 추출
        text = self.parse_pdf_text(pdf_path)
        
        # 정보 추출
        case_number = self.extract_case_number(text, pdf_path)
        court = self.extract_court(text, case_number)
        judgment_date = self.extract_judgment_date(text)
        year = self.extract_year(text, case_number, judgment_date)  # 판결일 우선 사용
        judgment_section = self.extract_judgment_section(text)  # 판단 섹션 먼저 추출
        holding = self.extract_holding(text, judgment_section)  # 판단 섹션을 요지 추출에 사용
        content = self.extract_content(text, judgment_section)  # 판단 섹션을 content 추출에 사용
        category, sub_category = self.determine_category(text)
        keywords = self.extract_keywords(text, sub_category)
        panji_items = self.extract_panji_items(text)
        reference_articles = self.extract_reference_articles(text)
        reference_cases = self.extract_reference_cases(text)
        
        logger.info(f"추출된 정보:")
        logger.info(f"  - 법원: {court}")
        logger.info(f"  - 사건번호: {case_number or '없음'}")
        logger.info(f"  - 연도: {year}")
        logger.info(f"  - 판결일: {judgment_date or '없음'}")
        logger.info(f"  - 카테고리: {category} > {sub_category}")
        logger.info(f"  - 판시사항: {len(panji_items)}개")
        logger.info(f"  - 참조조문: {len(reference_articles)}개")
        logger.info(f"  - 참조판례: {len(reference_cases)}개")
        
        # JSON 데이터 생성
        case_data = self.create_case_json(
            court=court,
            case_number=case_number,
            year=year,
            content=content,
            holding=holding,
            category=category,
            sub_category=sub_category,
            keywords=keywords,
            judgment_date=judgment_date,
            panji_items=panji_items if panji_items else None,
            reference_articles=reference_articles if reference_articles else None,
            reference_cases=reference_cases if reference_cases else None,
        )
        
        # 파일 저장
        file_path = self.save_case(case_data)
        logger.info(f"저장 완료: {file_path}")
        
        return file_path


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="판례 PDF를 JSON으로 변환")
    parser.add_argument(
        "path",
        type=Path,
        help="PDF 파일 경로 또는 폴더 경로"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/collected/cases"),
        help="출력 디렉토리 (기본값: data/collected/cases)"
    )
    parser.add_argument(
        "--f",
        "--folder",
        dest="folder_mode",
        action="store_true",
        help="폴더 모드: 지정된 폴더의 모든 PDF 파일을 처리"
    )
    
    args = parser.parse_args()
    
    if not args.path.exists():
        logger.error(f"경로를 찾을 수 없습니다: {args.path}")
        return
    
    parser_obj = CasePDFParser(args.output_dir)
    
    # 폴더 모드인지 확인
    if args.folder_mode or args.path.is_dir():
        # 폴더 모드: 모든 PDF 파일 찾기
        pdf_files = list(args.path.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"폴더에 PDF 파일이 없습니다: {args.path}")
            return
        
        logger.info(f"총 {len(pdf_files)}개의 PDF 파일을 찾았습니다.")
        print(f"\n📁 폴더 모드: {len(pdf_files)}개 파일 처리 시작\n")
        
        success_count = 0
        error_count = 0
        error_files = []
        
        for idx, pdf_file in enumerate(pdf_files, 1):
            print(f"[{idx}/{len(pdf_files)}] 처리 중: {pdf_file.name}")
            try:
                saved_file = parser_obj.parse_and_save(pdf_file)
                success_count += 1
                print(f"  ✅ 완료: {saved_file.name}\n")
            except Exception as e:
                error_count += 1
                error_files.append(pdf_file.name)
                logger.error(f"  ❌ 오류 발생 ({pdf_file.name}): {str(e)}")
                print(f"  ❌ 오류: {str(e)}\n")
        
        # 결과 요약
        print("\n" + "="*60)
        print(f"📊 처리 완료 요약")
        print("="*60)
        print(f"✅ 성공: {success_count}개")
        print(f"❌ 실패: {error_count}개")
        print(f"📁 저장 위치: {args.output_dir}")
        
        if error_files:
            print(f"\n⚠️  실패한 파일:")
            for file in error_files:
                print(f"  - {file}")
        print("="*60)
        
    else:
        # 단일 파일 모드
        if not args.path.is_file():
            logger.error(f"PDF 파일이 아닙니다: {args.path}")
            return
        
        saved_file = parser_obj.parse_and_save(args.path)
        
        if saved_file:
            print(f"\n✅ 변환 완료!")
            print(f"📁 저장 위치: {args.output_dir}")
            print(f"📄 생성된 파일: {saved_file}")
        else:
            print("\n❌ 변환 실패")


if __name__ == "__main__":
    main()

