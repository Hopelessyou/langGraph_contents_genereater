"""형법 PDF를 조문별 JSON 파일로 변환하는 스크립트"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
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
    
    def extract_law_name(self, text: str) -> str:
        """법률명 추출"""
        # PDF 첫 부분에서 법률명 추출
        # 예: "형법(법률)(제20908호)(20250408).pdf" -> "형법"
        patterns = [
            r"형법",
            r"형사소송법",
            r"민법",
            r"민사소송법",
        ]
        
        for pattern in patterns:
            if re.search(pattern, text[:500]):
                return pattern
        
        return "형법"  # 기본값
    
    def extract_articles(self, text: str) -> List[Dict[str, Any]]:
        """
        텍스트에서 조문을 추출합니다.
        
        Args:
            text: PDF에서 추출한 텍스트
            
        Returns:
            조문 리스트
        """
        articles = []
        
        # 조문 패턴: "제X조" 또는 "제X조(제목)"
        # 예: "제1조(범죄의 성립과 처벌)", "제347조(사기)"
        article_pattern = r'제(\d+)조(?:\(([^)]+)\))?'
        
        # 조문으로 분할
        parts = re.split(article_pattern, text)
        
        current_article_num = None
        current_title = None
        current_content = ""
        
        for i, part in enumerate(parts):
            # 조문 번호인 경우
            if part.isdigit():
                # 이전 조문 저장
                if current_article_num is not None:
                    articles.append({
                        "number": current_article_num,
                        "title": current_title,
                        "content": current_content.strip()
                    })
                
                current_article_num = part
                current_content = ""
                # 다음 부분이 제목인지 확인
                if i + 1 < len(parts) and parts[i + 1] and not parts[i + 1].isdigit():
                    if not parts[i + 1].startswith("제"):
                        current_title = parts[i + 1].strip("()")
                    else:
                        current_title = None
                else:
                    current_title = None
            elif part and not part.startswith("제") and current_article_num:
                # 조문 내용
                current_content += part + "\n"
        
        # 마지막 조문 저장
        if current_article_num is not None:
            articles.append({
                "number": current_article_num,
                "title": current_title,
                "content": current_content.strip()
            })
        
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
        
        # 법률명 추출
        law_name = self.extract_law_name(text)
        logger.info(f"법률명: {law_name}")
        
        # 개정일 추출 (파일명에서)
        if not updated_at:
            match = re.search(r'\((\d{8})\)', pdf_path.name)
            if match:
                date_str = match.group(1)
                updated_at = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        
        # 조문 추출
        articles = self.extract_articles(text)
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

