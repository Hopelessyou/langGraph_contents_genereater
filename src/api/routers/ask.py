"""질의응답 API"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, AsyncIterator
from datetime import datetime
import json

from ...rag import (
    HybridRetriever,
    LLMManager,
    SessionManager,
    VectorStore,
    EmbeddingGenerator,
)

router = APIRouter()

# 전역 인스턴스
_vector_store = None
_embedding_gen = None
_retriever = None
_llm_manager = None
_session_manager = None


def get_services():
    """서비스 인스턴스 가져오기"""
    global _vector_store, _embedding_gen, _retriever, _llm_manager, _session_manager
    
    if _retriever is None:
        _vector_store = VectorStore()
        _embedding_gen = EmbeddingGenerator()
        _retriever = HybridRetriever(_vector_store, _embedding_gen)
        _llm_manager = LLMManager()
        _session_manager = SessionManager()
    
    return _retriever, _llm_manager, _session_manager


class AskRequest(BaseModel):
    """질의응답 요청"""
    query: str = Field(..., description="질문")
    session_id: Optional[str] = Field(None, description="세션 ID (대화 연속성)")
    stream: bool = Field(default=False, description="스트리밍 응답 여부")
    document_types: Optional[List[str]] = Field(
        None,
        description="문서 타입 필터"
    )


class Message(BaseModel):
    """메시지"""
    role: str
    content: str


class AskResponse(BaseModel):
    """질의응답 응답"""
    query: str
    response: str
    session_id: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: str


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    질의응답
    
    사용자의 질문에 대해 RAG 기반으로 답변을 생성합니다.
    """
    try:
        retriever, llm_manager, session_manager = get_services()
        
        # 세션 가져오기 또는 생성
        if request.session_id:
            session = session_manager.get_session(request.session_id)
            if not session:
                session = session_manager.create_session(request.session_id)
        else:
            session = session_manager.create_session()
        
        # 이전 대화 히스토리 가져오기
        history = session.get_history(max_turns=3)
        context_from_history = session.get_context_string(max_turns=3)
        
        # 검색 수행
        search_result = retriever.search(
            query=request.query,
            n_results=5,
            document_types=request.document_types,
        )
        
        # 컨텍스트 구성
        context = search_result.get("context", "")
        if context_from_history:
            context = f"이전 대화:\n{context_from_history}\n\n관련 문서:\n{context}"
        
        # LLM 응답 생성
        if request.stream:
            # 스트리밍은 별도 엔드포인트로 처리
            pass
        
        response_text = llm_manager.generate_response(
            context=context,
            query=request.query,
            document_types=request.document_types,
        )
        
        # 세션에 메시지 추가
        session.add_message("user", request.query)
        session.add_message("assistant", response_text)
        
        # 출처 정보 추출
        sources = [
            {
                "id": r.get("id", ""),
                "title": r.get("metadata", {}).get("title", ""),
                "type": r.get("metadata", {}).get("type", ""),
            }
            for r in search_result.get("results", [])[:3]
        ]
        
        return AskResponse(
            query=request.query,
            response=response_text,
            session_id=session.session_id,
            sources=sources,
            timestamp=datetime.now().isoformat(),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"답변 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/ask/stream")
async def ask_question_stream(request: AskRequest):
    """
    스트리밍 질의응답
    
    실시간으로 스트리밍 응답을 반환합니다.
    """
    try:
        retriever, llm_manager, session_manager = get_services()
        
        # 세션 가져오기 또는 생성
        if request.session_id:
            session = session_manager.get_session(request.session_id)
            if not session:
                session = session_manager.create_session(request.session_id)
        else:
            session = session_manager.create_session()
        
        # 검색 수행
        search_result = retriever.search(
            query=request.query,
            n_results=5,
            document_types=request.document_types,
        )
        
        # 컨텍스트 구성
        context = search_result.get("context", "")
        history = session.get_context_string(max_turns=3)
        if history:
            context = f"이전 대화:\n{history}\n\n관련 문서:\n{context}"
        
        # 스트리밍 응답 생성
        async def generate_stream() -> AsyncIterator[str]:
            async for chunk in llm_manager.generate_response_async(
                context=context,
                query=request.query,
                document_types=request.document_types,
            ):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # 세션에 메시지 추가
            full_response = ""  # 실제로는 청크를 모아야 함
            session.add_message("user", request.query)
            session.add_message("assistant", full_response)
            
            yield f"data: {json.dumps({'done': True})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"스트리밍 응답 생성 중 오류가 발생했습니다: {str(e)}"
        )

