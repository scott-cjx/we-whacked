"""Configuration settings for the backend."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "We Whacked API"
    app_version: str = "0.1.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        """Pydantic config."""
        env_file = ".env"


settings = Settings()
