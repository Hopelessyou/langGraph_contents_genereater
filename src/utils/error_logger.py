"""에러 로깅 및 알림"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
import json
from pathlib import Path

from config.settings import settings

logger = logging.getLogger(__name__)


class ErrorLogger:
    """에러 로거"""
    
    def __init__(self, error_log_file: Optional[Path] = None):
        self.error_log_file = (
            error_log_file or Path(settings.data_dir) / "logs" / "errors.jsonl"
        )
        self.error_log_file.parent.mkdir(parents=True, exist_ok=True)
        self.error_count = 0
        self.error_threshold = 10  # 임계값
    
    def log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        severity: str = "error",
    ):
        """
        에러를 로깅합니다.
        
        Args:
            error: 예외 객체
            context: 추가 컨텍스트 정보
            severity: 심각도 (error, warning, critical)
        """
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
        }
        
        # JSONL 형식으로 로깅
        try:
            with open(self.error_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(error_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"에러 로깅 실패: {str(e)}")
        
        # 로그 레벨에 따라 기록
        if severity == "critical":
            logger.critical(f"심각한 오류: {str(error)}", exc_info=error)
        elif severity == "error":
            logger.error(f"오류: {str(error)}", exc_info=error)
        else:
            logger.warning(f"경고: {str(error)}")
        
        # 에러 카운트 증가
        self.error_count += 1
        
        # 임계값 초과 시 알림
        if self.error_count >= self.error_threshold:
            self._send_alert()
    
    def _send_alert(self):
        """알림 전송 (기본 구현)"""
        logger.warning(
            f"에러 임계값 초과: {self.error_count}건의 에러가 발생했습니다."
        )
        # 실제로는 이메일, 슬랙 등으로 알림 전송
        self.error_count = 0  # 리셋
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        최근 에러 요약을 반환합니다.
        
        Args:
            hours: 조회할 시간 범위
            
        Returns:
            에러 요약
        """
        # 실제 구현 시 JSONL 파일을 읽어서 분석
        return {
            "total_errors": self.error_count,
            "period_hours": hours,
        }

