"""검색 쿼리 로깅"""

from typing import Dict, Any, Optional
from datetime import datetime
import json
import logging
from pathlib import Path

from config.settings import settings

logger = logging.getLogger(__name__)


class QueryLogger:
    """검색 쿼리 로거"""
    
    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = log_file or Path(settings.data_dir) / "logs" / "queries.jsonl"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_query(
        self,
        query: str,
        results_count: int,
        response_time: float,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        검색 쿼리를 로깅합니다.
        
        Args:
            query: 검색 쿼리
            results_count: 결과 개수
            response_time: 응답 시간 (초)
            metadata: 추가 메타데이터
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "results_count": results_count,
            "response_time": response_time,
            "metadata": metadata or {},
        }
        
        # JSONL 형식으로 로깅
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"쿼리 로깅 실패: {str(e)}")
        
        # 일반 로그에도 기록
        logger.info(
            f"검색 쿼리: '{query}' - 결과 {results_count}건, 응답 시간 {response_time:.3f}초"
        )
    
    def log_ask_query(
        self,
        query: str,
        session_id: Optional[str],
        response_length: int,
        response_time: float,
        token_usage: Optional[Dict[str, int]] = None,
    ):
        """
        질의응답 쿼리를 로깅합니다.
        
        Args:
            query: 질문
            session_id: 세션 ID
            response_length: 응답 길이
            response_time: 응답 시간
            token_usage: 토큰 사용량
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "ask",
            "query": query,
            "session_id": session_id,
            "response_length": response_length,
            "response_time": response_time,
            "token_usage": token_usage or {},
        }
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"질의응답 로깅 실패: {str(e)}")
        
        logger.info(
            f"질의응답: '{query[:50]}...' - 응답 {response_length}자, "
            f"응답 시간 {response_time:.3f}초"
        )

