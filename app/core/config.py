from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
 
BASE_DIR = Path(__file__).resolve().parent.parent.parent
 
class Settings(BaseSettings):
    PROJECT_NAME: str = "Adaptive Onboarding Engine"
 
    GROQ_API_KEY: str
    PINECONE_API_KEY: str
    WEB_BASE_URL: str
    # CLOUDINARY_CLOUD_NAME: str
    # CLOUDINARY_API_KEY: str
    # CLOUDINARY_API_SECRET: str
 
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )
 
settings = Settings()