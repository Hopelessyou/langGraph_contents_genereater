"""설정 관리"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # OpenAI API
    openai_api_key: str = ""
    
    # Vector Database
    vector_db_type: str = "chroma"  # chroma, pinecone, faiss
    chroma_persist_directory: str = "./data/vector_db"
    
    # Pinecone (Optional)
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: str = "ibs-legal-ai"
    
    # LLM Settings
    llm_model: str = "gpt-4-turbo-preview"
    embedding_model: str = "text-embedding-3-large"
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    # Data Settings
    data_dir: str = "./data"
    processed_data_dir: str = "./data/processed"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    @property
    def chroma_persist_path(self) -> Path:
        """Chroma DB 저장 경로"""
        return Path(self.chroma_persist_directory)
    
    @property
    def data_path(self) -> Path:
        """데이터 디렉토리 경로"""
        return Path(self.data_dir)
    
    @property
    def processed_data_path(self) -> Path:
        """처리된 데이터 디렉토리 경로"""
        return Path(self.processed_data_dir)


# 전역 설정 인스턴스
settings = Settings()

