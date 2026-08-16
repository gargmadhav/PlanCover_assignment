import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "GMC Document Intelligence System"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    
    # LLM Provider: 'gemini', 'groq', or 'mock'
    LLM_PROVIDER: str = "gemini"
    MODEL_NAME: str = "gemini-2.5-flash"
    
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    TOP_K_CHUNKS: int = 5
    
    OCR_FALLBACK_MIN_TEXT_CHARS: int = 30
    MAX_UPLOAD_SIZE_MB: int = 25
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
