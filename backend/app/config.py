from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    app_name: str = "Real-Time Multimodal Brand Guardian System"
    app_version: str = "0.1.0"
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    gemini_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")
    chroma_collection_name: str = Field(
        default="brand-guardian-memory",
        alias="CHROMA_COLLECTION_NAME",
    )
    chroma_persist_directory: str = Field(
        default="./chroma_db",
        alias="CHROMA_PERSIST_DIRECTORY",
    )
    enable_fake_mode: bool = Field(default=False, alias="ENABLE_FAKE_MODE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
settings = Settings()
