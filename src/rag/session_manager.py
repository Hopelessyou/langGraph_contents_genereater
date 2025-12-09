"""대화 세션 및 히스토리 관리"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import logging
import json

from config.settings import settings

logger = logging.getLogger(__name__)

# Redis 지원 (선택적)
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


class ConversationSession:
    """대화 세션"""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.history: List[Dict[str, str]] = []
        self.metadata: Dict[str, Any] = {}
    
    def add_message(self, role: str, content: str):
        """메시지 추가"""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        self.updated_at = datetime.now()
    
    def get_history(self, max_turns: Optional[int] = None) -> List[Dict[str, str]]:
        """히스토리 반환"""
        if max_turns:
            return self.history[-max_turns:]
        return self.history.copy()
    
    def get_context_string(self, max_turns: int = 5) -> str:
        """컨텍스트 문자열 생성"""
        recent_history = self.get_history(max_turns=max_turns)
        context_parts = []
        
        for msg in recent_history:
            role = msg["role"]
            content = msg["content"]
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)


class SessionManager:
    """세션 관리자"""
    
    def __init__(self, max_sessions: int = 1000, session_timeout_minutes: int = 30):
        self.max_sessions = max_sessions
        self.session_timeout_minutes = session_timeout_minutes
        
        # Redis 사용 여부 결정
        self.use_redis = False
        self.redis_client = None
        self.sessions: Dict[str, ConversationSession] = {}
        
        if settings.redis_url and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                )
                # 연결 테스트
                self.redis_client.ping()
                self.use_redis = True
                logger.info(f"Redis 세션 저장소 연결 성공: {settings.redis_url}")
            except Exception as e:
                logger.warning(f"Redis 연결 실패, 메모리 저장소 사용: {str(e)}")
                self.use_redis = False
        else:
            if settings.redis_url and not REDIS_AVAILABLE:
                logger.warning("Redis URL이 설정되었지만 redis 패키지가 설치되지 않았습니다. 메모리 저장소를 사용합니다.")
            else:
                logger.info("메모리 세션 저장소 사용")
    
    def create_session(self, session_id: Optional[str] = None) -> ConversationSession:
        """새 세션 생성"""
        session = ConversationSession(session_id=session_id)
        
        if self.use_redis:
            self._save_session_to_redis(session)
        else:
            self.sessions[session.session_id] = session
            # 세션 수 제한
            if len(self.sessions) > self.max_sessions:
                self._cleanup_old_sessions()
        
        logger.debug(f"세션 생성: {session.session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """세션 가져오기"""
        if self.use_redis:
            session = self._load_session_from_redis(session_id)
        else:
            session = self.sessions.get(session_id)
        
        if session:
            # 타임아웃 확인
            timeout_delta = datetime.now() - session.updated_at
            if timeout_delta.total_seconds() > self.session_timeout_minutes * 60:
                logger.debug(f"세션 타임아웃: {session_id}")
                self.delete_session(session_id)
                return None
        
        return session
    
    def delete_session(self, session_id: str):
        """세션 삭제"""
        if self.use_redis:
            try:
                self.redis_client.delete(f"session:{session_id}")
                logger.debug(f"세션 삭제 (Redis): {session_id}")
            except Exception as e:
                logger.error(f"Redis 세션 삭제 실패: {str(e)}")
        else:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.debug(f"세션 삭제: {session_id}")
    
    def _cleanup_old_sessions(self):
        """오래된 세션 정리"""
        # 업데이트 시간 기준으로 정렬
        sorted_sessions = sorted(
            self.sessions.items(),
            key=lambda x: x[1].updated_at,
        )
        
        # 오래된 세션 삭제 (절반)
        to_remove = len(sorted_sessions) // 2
        for session_id, _ in sorted_sessions[:to_remove]:
            self.delete_session(session_id)
        
        logger.info(f"오래된 세션 {to_remove}개 정리 완료")
    
    def get_all_sessions(self) -> List[str]:
        """모든 세션 ID 반환"""
        if self.use_redis:
            try:
                keys = self.redis_client.keys("session:*")
                return [key.replace("session:", "") for key in keys]
            except Exception as e:
                logger.error(f"Redis 세션 목록 조회 실패: {str(e)}")
                return []
        else:
            return list(self.sessions.keys())
    
    def update_session(self, session: ConversationSession):
        """세션 업데이트 (Redis 사용 시 저장)"""
        if self.use_redis:
            self._save_session_to_redis(session)
        # 메모리 모드에서는 이미 sessions 딕셔너리에 있으므로 별도 저장 불필요
    
    def _save_session_to_redis(self, session: ConversationSession):
        """세션을 Redis에 저장"""
        try:
            session_data = {
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "history": session.history,
                "metadata": session.metadata,
            }
            # TTL 설정 (초 단위)
            ttl = self.session_timeout_minutes * 60
            self.redis_client.setex(
                f"session:{session.session_id}",
                ttl,
                json.dumps(session_data, ensure_ascii=False)
            )
        except Exception as e:
            logger.error(f"Redis 세션 저장 실패: {str(e)}")
            # Redis 실패 시 메모리로 폴백
            self.sessions[session.session_id] = session
    
    def _load_session_from_redis(self, session_id: str) -> Optional[ConversationSession]:
        """Redis에서 세션 로드"""
        try:
            data = self.redis_client.get(f"session:{session_id}")
            if not data:
                return None
            
            session_data = json.loads(data)
            session = ConversationSession(session_id=session_data["session_id"])
            session.created_at = datetime.fromisoformat(session_data["created_at"])
            session.updated_at = datetime.fromisoformat(session_data["updated_at"])
            session.history = session_data["history"]
            session.metadata = session_data["metadata"]
            
            return session
        except Exception as e:
            logger.error(f"Redis 세션 로드 실패: {str(e)}")
            return None

