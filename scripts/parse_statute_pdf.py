"""형법 PDF를 조문별 JSON 파일로 변환하는 스크립트"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


class StatutePDFParser:
    """형법 PDF 파서"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def parse_pdf_text(self, pdf_path: Path) -> str:
        """
        PDF 파일을 텍스트로 변환합니다.
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            PDF 텍스트 내용
        """
        try:
            import PyPDF2
        except ImportError:
            logger.error("PyPDF2가 설치되지 않았습니다. 'pip install PyPDF2'를 실행하세요.")
            raise
        
        text = ""
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        return text
    
    def extract_law_name(self, text: str, pdf_path: Path = None) -> str:
        """
        법률명 추출 (파일명 우선, 텍스트 내용 보조)
        
        Args:
            text: PDF 텍스트 내용
            pdf_path: PDF 파일 경로 (선택)
            
        Returns:
            법률명
        """
        # 1. 파일명에서 법률명 추출 시도
        if pdf_path:
            filename = pdf_path.stem  # 확장자 제거
            # 예: "형법(법률)(제20908호)(20250408)" -> "형법"
            # 예: "특정경제범죄 가중처벌 등에 관한 법률(법률)(제15256호)(20180320)" -> "특정경제범죄 가중처벌 등에 관한 법률"
            
            # "(법률)" 이전 부분 추출
            match = re.match(r'^(.+?)(?:\(법률\)|\(제\d+호\))', filename)
            if match:
                law_name = match.group(1).strip()
                if law_name:
                    logger.info(f"파일명에서 법률명 추출: {law_name}")
                    return law_name
        
        # 2. PDF 텍스트 첫 부분에서 법률명 추출 시도
        # 일반적인 법률명 패턴
        common_patterns = [
            r"형법",
            r"형사소송법",
            r"민법",
            r"민사소송법",
            r"특정경제범죄\s*가중처벌",
            r"특정범죄\s*가중처벌",
        ]
        
        for pattern in common_patterns:
            match = re.search(pattern, text[:1000])
            if match:
                law_name = match.group(0).strip()
                logger.info(f"텍스트에서 법률명 추출: {law_name}")
                return law_name
        
        # 3. 텍스트 첫 줄에서 법률명 추출 시도
        first_lines = text[:500].split('\n')
        for line in first_lines[:5]:
            line = line.strip()
            if line and len(line) > 2 and len(line) < 100:
                # "법률" 또는 "법"으로 끝나는 경우
                if line.endswith("법") or line.endswith("법률"):
                    logger.info(f"첫 줄에서 법률명 추출: {line}")
                    return line
        
        # 기본값
        logger.warning("법률명을 추출할 수 없어 기본값 '형법'을 사용합니다.")
        return "형법"
    
    def extract_articles(self, text: str, law_name: str = None) -> List[Dict[str, Any]]:
        """
        텍스트에서 조문을 추출합니다.
        
        Args:
            text: PDF에서 추출한 텍스트
            law_name: 법률명 (필터링에 사용)
            
        Returns:
            조문 리스트 (중복 제거됨)
        """
        articles = []
        seen_numbers = set()  # 중복 조문 번호 추적
        
        # 조문 패턴: "제X조" 또는 "제X조(제목)"
        # 예: "제1조(범죄의 성립과 처벌)", "제347조(사기)"
        article_pattern = r'제(\d+)조(?:\(([^)]+)\))?'
        
        # finditer를 사용하여 더 안정적으로 조문 추출
        matches = list(re.finditer(article_pattern, text))
        
        if not matches:
            logger.warning("조문을 찾을 수 없습니다.")
            return articles
        
        # 실제 조문인지 참조인지 판단하는 함수
        def is_actual_article(match_idx: int) -> bool:
            """조문이 실제 조문인지 다른 법률 참조인지 판단"""
            match = matches[match_idx]
            start_pos = match.start()
            article_num = int(match.group(1))
            article_title = match.group(2) if match.group(2) else None
            
            # 조문 번호가 1-50 사이면 거의 확실히 실제 조문 (범위 확대)
            if 1 <= article_num <= 50:
                # 다만 다른 법률 참조 패턴이 바로 앞에 있으면 제외
                context_before = text[max(0, start_pos - 80):start_pos]
                other_law_patterns = [
                    r'「[^」]+」\s*제\d+조',  # 「형법」제347조
                    r'\[[^\]]+\]\s*제\d+조',  # [형법]제347조
                    r'법\s*제\d+조',  # 형법 제347조 (법률명 뒤에 바로 조문)
                ]
                for pattern in other_law_patterns:
                    if re.search(pattern, context_before):
                        logger.debug(f"제{article_num}조: 다른 법률 참조 패턴 발견 (컨텍스트: {context_before[-30:]})")
                        return False
                return True
            
            # 조문 번호가 큰 경우 (50 초과) 더 신중하게 확인
            if article_num > 50:
                context_before = text[max(0, start_pos - 150):start_pos]
                context_after = text[start_pos:min(len(text), start_pos + 150)]
                
                # 다른 법률명이 바로 앞에 있는 경우 필터링
                other_law_patterns = [
                    r'「[^」]+」\s*제\d+조',  # 「형법」제347조
                    r'\[[^\]]+\]\s*제\d+조',  # [형법]제347조
                    r'법\s*제\d+조',  # 형법 제347조
                ]
                
                for pattern in other_law_patterns:
                    if re.search(pattern, context_before + context_after):
                        logger.debug(f"제{article_num}조: 다른 법률 참조로 판단")
                        return False
                
                # 줄 시작 부분 확인
                line_start = text[max(0, start_pos - 300):start_pos].rfind('\n')
                line_text = text[line_start + 1:start_pos + 100] if line_start >= 0 else text[:start_pos + 100]
                
                # 줄 시작 부분에 "제X조"가 있고 제목이 있으면 실제 조문
                if re.match(r'^\s*제\d+조\(', line_text):
                    logger.debug(f"제{article_num}조: 줄 시작에 제목이 있어 실제 조문으로 판단")
                    return True
                
                # 줄 시작 부분에 "제X조"가 있고, 그 뒤에 실제 내용이 있으면 실제 조문
                # (제목이 없어도 실제 조문일 수 있음)
                if re.match(r'^\s*제\d+조', line_text):
                    # 다음 100자 내에 실제 내용이 있는지 확인
                    after_match = text[start_pos:min(len(text), start_pos + 200)]
                    # 숫자, 한글, 특수문자가 섞여 있으면 실제 내용으로 판단
                    if re.search(r'[가-힣]{3,}|[①②③④⑤]|①|②|③', after_match):
                        logger.debug(f"제{article_num}조: 줄 시작에 있고 내용이 있어 실제 조문으로 판단")
                        return True
                
                # 그 외에는 참조일 가능성이 높지만, 너무 엄격하게 필터링하지 않음
                # 조문 번호가 100 이하이고 제목이 있으면 실제 조문으로 간주
                if article_num <= 100 and article_title:
                    logger.debug(f"제{article_num}조: 제목이 있어 실제 조문으로 판단")
                    return True
                
                logger.debug(f"제{article_num}조: 참조로 판단 (조문 번호가 크고 제목/내용이 불명확)")
                    return False
            
            return True
        
        # 실제 조문만 필터링
        actual_matches = []
        filtered_out = []
        for i, match in enumerate(matches):
            article_num = match.group(1)
            if is_actual_article(i):
                actual_matches.append((i, match))
            else:
                filtered_out.append(article_num)
        
        logger.info(f"전체 조문 매치 수: {len(matches)}, 실제 조문 수: {len(actual_matches)}")
        if filtered_out:
            logger.debug(f"필터링된 조문 번호: {', '.join(filtered_out[:10])}{'...' if len(filtered_out) > 10 else ''}")
        
        if not actual_matches:
            logger.warning("실제 조문을 찾을 수 없습니다.")
            return articles
        
        # 각 실제 조문과 그 다음 조문 사이의 내용 추출
        for idx, (i, match) in enumerate(actual_matches):
            article_num = match.group(1)
            article_title = match.group(2) if match.group(2) else None
            match_end = match.end()
            
            # 중복 조문 번호 체크
            if article_num in seen_numbers:
                logger.warning(f"중복 조문 번호 건너뛰기: 제{article_num}조 (이미 추출됨)")
                continue
            
            # 다음 실제 조문의 시작 위치 찾기
            if idx + 1 < len(actual_matches):
                next_idx, next_match = actual_matches[idx + 1]
                end_pos = next_match.start()
            else:
                # 마지막 조문인 경우 텍스트 끝까지
                end_pos = len(text)
            
            # 조문 내용 추출
            content = text[match_end:end_pos].strip()
            
            # 내용 정제: 불필요한 앞부분 제거
            # 줄바꿈 후 시작하는 경우 첫 줄의 불필요한 부분 제거
            lines = content.split('\n')
            if len(lines) > 1:
                # 첫 줄이 너무 짧거나 불완전하면 제거
                first_line = lines[0].strip()
                if len(first_line) < 5 or re.match(r'^[의,)\s\d]+$', first_line):
                    content = '\n'.join(lines[1:]).strip()
            
            # "제X조"로 시작하는 부분 제거 (다음 조문이 포함된 경우)
            # 하지만 현재 조문 번호와 다른 조문만 제거
            next_article_match = re.search(r'제(\d+)조', content)
            if next_article_match:
                next_article_num = next_article_match.group(1)
                # 다음 조문 번호가 현재 조문 번호보다 크면 (실제 다음 조문)
                if int(next_article_num) > int(article_num):
                content = content[:next_article_match.start()].strip()
            
            # 내용 정제: 불필요한 접두사 제거
            # "의2", "의 2", "), " 같은 불완전한 시작 부분 제거
            content = re.sub(r'^[의,)\s]+', '', content)
            content = re.sub(r'^의\s*\d+', '', content)
            content = content.strip()
            
            # 내용이 너무 짧거나 비어있으면 건너뛰기 (기준 완화: 5자 이상)
            if len(content) < 5:
                logger.warning(f"내용이 너무 짧아 건너뛰기: 제{article_num}조 (길이: {len(content)}, 내용: {content[:50]})")
                continue
            
            # 내용이 단순히 숫자나 특수문자만 있는 경우 필터링
            if re.match(r'^[\d\s,\.\)]+$', content) and len(content) < 20:
                logger.warning(f"불완전한 내용으로 건너뛰기: 제{article_num}조 (내용: {content[:50]})")
                continue
            
            articles.append({
                "number": article_num,
                "title": article_title,
                "content": content
            })
            
            seen_numbers.add(article_num)
            logger.debug(f"조문 추출 성공: 제{article_num}조 (제목: {article_title or '없음'}, 내용 길이: {len(content)})")
        
        # 조문 번호 순서대로 정렬
        articles.sort(key=lambda x: int(x["number"]))
        
        # 추출된 조문 번호 목록 로깅
        extracted_numbers = [a["number"] for a in articles]
        logger.info(f"추출된 조문 수: {len(articles)} (중복 제거 후)")
        logger.info(f"추출된 조문 번호: {', '.join(extracted_numbers)}")
        
        # 누락된 조문 번호 확인 (1부터 최대 조문 번호까지)
        if articles:
            max_num = max(int(a["number"]) for a in articles)
            all_numbers = set(str(i) for i in range(1, max_num + 1))
            extracted_set = set(extracted_numbers)
            missing = sorted(all_numbers - extracted_set, key=int)
            if missing:
                logger.warning(f"누락된 조문 번호: {', '.join(missing)}")
        
        return articles
    
    def clean_content(self, content: str) -> str:
        """조문 내용 정제"""
        # 불필요한 공백 제거
        content = re.sub(r'\s+', ' ', content)
        # 줄바꿈 정리
        content = re.sub(r'\n\s*\n', '\n', content)
        # 앞뒤 공백 제거
        content = content.strip()
        return content
    
    def determine_category(self, article_num: str, law_name: str) -> tuple[str, str]:
        """
        조문 번호와 법률명으로 카테고리와 서브카테고리를 결정합니다.
        
        Args:
            article_num: 조문 번호
            law_name: 법률명
            
        Returns:
            (category, sub_category) 튜플
        """
        # 형법의 경우
        if law_name == "형법":
            num = int(article_num) if article_num.isdigit() else 0
            
            # 총칙 (1-72조)
            if 1 <= num <= 72:
                return ("형사", "총칙")
            # 각칙
            elif 130 <= num <= 250:
                return ("형사", "생명과 신체에 대한 죄")
            elif 250 <= num <= 280:
                return ("형사", "자유에 대한 죄")
            elif 329 <= num <= 361:
                return ("형사", "재산에 대한 죄")
            elif num == 347:
                return ("형사", "사기")
            elif 362 <= num <= 365:
                return ("형사", "장물")
            elif 366 <= num <= 372:
                return ("형사", "손괴")
            else:
                return ("형사", "")
        
        # 형사소송법의 경우
        elif law_name == "형사소송법":
            return ("형사", "소송절차")
        
        # 기본값
        return ("형사", "")
    
    def extract_topics(self, content: str, title: str) -> List[str]:
        """조문 내용에서 주제 키워드 추출"""
        topics = []
        
        # 제목에서 키워드 추출
        if title:
            keywords = ["사기", "살인", "절도", "강도", "강간", "횡령", "장물", "손괴"]
            for keyword in keywords:
                if keyword in title:
                    topics.append(keyword)
        
        # 내용에서 키워드 추출
        content_keywords = ["재물", "재산", "이익", "기망", "편취"]
        for keyword in content_keywords:
            if keyword in content:
                if keyword not in topics:
                    topics.append(keyword)
        
        return topics
    
    def create_statute_json(
        self,
        law_name: str,
        article_num: str,
        title: str,
        content: str,
        updated_at: str = None
    ) -> Dict[str, Any]:
        """
        조문 데이터를 JSON 형식으로 변환합니다.
        
        Args:
            law_name: 법률명
            article_num: 조문 번호
            title: 조문 제목
            content: 조문 내용
            updated_at: 개정일
            
        Returns:
            JSON 형식의 조문 데이터
        """
        category, sub_category = self.determine_category(article_num, law_name)
        topics = self.extract_topics(content, title)
        
        # ID 생성: "statute-형법-347"
        doc_id = f"statute-{law_name}-{article_num}"
        
        # 제목 생성: "형법 제347조(사기)"
        if title:
            full_title = f"{law_name} 제{article_num}조({title})"
        else:
            full_title = f"{law_name} 제{article_num}조"
        
        # 내용 정제
        cleaned_content = self.clean_content(content)
        
        return {
            "id": doc_id,
            "category": category,
            "sub_category": sub_category,
            "type": "statute",
            "title": full_title,
            "content": cleaned_content,
            "metadata": {
                "law_name": law_name,
                "article_number": article_num,
                "topics": topics,
                "source": "법제처",
                "updated_at": updated_at or datetime.now().strftime("%Y-%m-%d")
            }
        }
    
    def save_article(self, law_name: str, article_data: Dict[str, Any]) -> Path:
        """
        조문을 JSON 파일로 저장합니다.
        
        Args:
            law_name: 법률명
            article_data: 조문 데이터
            
        Returns:
            저장된 파일 경로
        """
        # 법률별 폴더 생성
        law_dir = self.output_dir / law_name
        law_dir.mkdir(parents=True, exist_ok=True)
        
        # 파일명: "statute-형법-347.json"
        filename = f"{article_data['id']}.json"
        file_path = law_dir / filename
        
        # JSON 파일 저장
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(article_data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def parse_and_save(self, pdf_path: Path, updated_at: str = None) -> List[Path]:
        """
        PDF를 파싱하여 조문별 JSON 파일로 저장합니다.
        
        Args:
            pdf_path: PDF 파일 경로
            updated_at: 개정일 (PDF 파일명에서 추출 시도)
            
        Returns:
            저장된 파일 경로 리스트
        """
        logger.info(f"PDF 파싱 시작: {pdf_path}")
        
        # PDF 텍스트 추출
        text = self.parse_pdf_text(pdf_path)
        
        # 법률명 추출 (파일명 우선)
        law_name = self.extract_law_name(text, pdf_path)
        logger.info(f"법률명: {law_name}")
        
        # 개정일 추출 (파일명에서)
        if not updated_at:
            match = re.search(r'\((\d{8})\)', pdf_path.name)
            if match:
                date_str = match.group(1)
                updated_at = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        
        # 조문 추출 (법률명 전달하여 필터링 가능)
        articles = self.extract_articles(text, law_name)
        logger.info(f"추출된 조문 수: {len(articles)}")
        
        # 각 조문을 JSON 파일로 저장
        saved_files = []
        for article in articles:
            article_data = self.create_statute_json(
                law_name=law_name,
                article_num=article["number"],
                title=article.get("title"),
                content=article["content"],
                updated_at=updated_at
            )
            
            file_path = self.save_article(law_name, article_data)
            saved_files.append(file_path)
            
            logger.debug(f"저장 완료: {file_path.name}")
        
        logger.info(f"총 {len(saved_files)}개 조문 파일 저장 완료")
        return saved_files


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="형법 PDF를 조문별 JSON으로 변환")
    parser.add_argument(
        "pdf_path",
        type=Path,
        help="PDF 파일 경로"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/collected/statutes"),
        help="출력 디렉토리 (기본값: data/collected/statutes)"
    )
    parser.add_argument(
        "--updated-at",
        type=str,
        help="개정일 (YYYY-MM-DD 형식, 파일명에서 자동 추출 시도)"
    )
    
    args = parser.parse_args()
    
    if not args.pdf_path.exists():
        logger.error(f"PDF 파일을 찾을 수 없습니다: {args.pdf_path}")
        return
    
    # 파서 생성 및 실행
    parser_obj = StatutePDFParser(args.output_dir)
    saved_files = parser_obj.parse_and_save(args.pdf_path, args.updated_at)
    
    print(f"\n✅ 변환 완료!")
    print(f"📁 저장 위치: {args.output_dir}")
    print(f"📄 생성된 파일 수: {len(saved_files)}")
    print(f"\n첫 5개 파일:")
    for file_path in saved_files[:5]:
        print(f"  - {file_path}")


if __name__ == "__main__":
    main()

