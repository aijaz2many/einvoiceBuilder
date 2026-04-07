from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "E-Invoice Builder API"
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # Security
    SECRET_KEY: str = "CHANGE_THIS_TO_A_SECURE_SECRET_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")

settings = Settings()
