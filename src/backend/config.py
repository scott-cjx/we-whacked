"""Configuration settings for the backend."""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "We Whacked API"
    app_version: str = "0.1.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Gemini AI settings
    gemini_api_key: str = "AIzaSyDKrCmPdSkGa1hYb-709RTaS4UVdeIXHD8"
    gemini_model: str = "gemini-2.5-flash-lite"
    
    class Config:
        """Pydantic config."""
        env_file = str(Path(__file__).parent / ".env")
        env_file_encoding = 'utf-8'


settings = Settings()
