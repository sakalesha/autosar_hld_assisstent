import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AUTOSAR HLD Document Analysis Assistant"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/autosar_hld.db") # Defaulting to local sqlite for dev if Neon URL not provided
    UPLOAD_DIR: str = "data/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    MAX_UPLOAD_SIZE_BYTES: int = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    
    
    class Config:
        env_file = ".env"

settings = Settings()

