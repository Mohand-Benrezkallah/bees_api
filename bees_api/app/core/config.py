from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Bee API"
    API_V1_STR: str = "/graphql"
    
    # Database configuration
    DATABASE_URL: str
    
    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Static files and image uploads
    STATIC_FILES_DIR: str = "app/images"
    UPLOAD_DIR: str = "app/images"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()