"""알림 시스템"""

from typing import Dict, Any, Optional, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AlertSystem:
    """알림 시스템"""
    
    def __init__(self):
        self.alert_handlers: List[Callable] = []
        self.alert_history: List[Dict[str, Any]] = []
    
    def register_handler(self, handler: Callable):
        """알림 핸들러 등록"""
        self.alert_handlers.append(handler)
    
    def send_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "warning",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        알림 전송
        
        Args:
            alert_type: 알림 타입 (error, performance, threshold 등)
            message: 알림 메시지
            severity: 심각도 (info, warning, error, critical)
            metadata: 추가 메타데이터
        """
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "severity": severity,
            "message": message,
            "metadata": metadata or {},
        }
        
        self.alert_history.append(alert)
        
        # 최근 100개만 유지
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]
        
        # 핸들러 호출
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"알림 핸들러 실행 실패: {str(e)}")
        
        # 로그 기록
        log_level = getattr(logging, severity.upper(), logging.WARNING)
        logger.log(log_level, f"[{alert_type}] {message}")
    
    def send_error_alert(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """에러 알림 전송"""
        self.send_alert(
            alert_type="error",
            message=f"에러 발생: {str(error)}",
            severity="error",
            metadata={"error_type": type(error).__name__, "context": context or {}},
        )
    
    def send_performance_alert(
        self,
        metric: str,
        value: float,
        threshold: float,
    ):
        """성능 임계값 알림 전송"""
        self.send_alert(
            alert_type="performance",
            message=f"{metric}이 임계값({threshold})을 초과했습니다: {value}",
            severity="warning",
            metadata={"metric": metric, "value": value, "threshold": threshold},
        )
    
    def send_data_update_alert(
        self,
        update_type: str,
        count: int,
        details: Optional[Dict[str, Any]] = None,
    ):
        """데이터 업데이트 알림 전송"""
        self.send_alert(
            alert_type="data_update",
            message=f"{update_type}: {count}건 처리됨",
            severity="info",
            metadata={"update_type": update_type, "count": count, "details": details or {}},
        )


class ThresholdMonitor:
    """임계값 모니터"""
    
    def __init__(self, alert_system: AlertSystem):
        self.alert_system = alert_system
        self.thresholds = {
            "response_time": 5.0,  # 5초
            "error_rate": 0.1,  # 10%
            "vector_db_document_count": 100000,  # 최대 문서 수
        }
    
    def check_threshold(
        self,
        metric: str,
        value: float,
    ):
        """
        임계값 확인
        
        Args:
            metric: 메트릭 이름
            value: 현재 값
        """
        threshold = self.thresholds.get(metric)
        if threshold and value > threshold:
            self.alert_system.send_performance_alert(metric, value, threshold)
    
    def set_threshold(self, metric: str, value: float):
        """임계값 설정"""
        self.thresholds[metric] = value

