"""대화 세션 및 히스토리 관리"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


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
        self.sessions: Dict[str, ConversationSession] = {}
        self.max_sessions = max_sessions
        self.session_timeout_minutes = session_timeout_minutes
    
    def create_session(self, session_id: Optional[str] = None) -> ConversationSession:
        """새 세션 생성"""
        session = ConversationSession(session_id=session_id)
        self.sessions[session.session_id] = session
        
        # 세션 수 제한
        if len(self.sessions) > self.max_sessions:
            self._cleanup_old_sessions()
        
        logger.debug(f"세션 생성: {session.session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """세션 가져오기"""
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
        return list(self.sessions.keys())

