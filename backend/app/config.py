"""
Application Configuration
-------------------------
Loads configuration from environment variables or .env file with safe defaults.
"""

from typing import List
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "Siddha AI - Digital Neerkuri & Neikuri Platform"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'siddha_ai.db'}"

    # ML Artifacts path
    ML_MODEL_PATH: str = str(BASE_DIR / "ml" / "model_bundle.joblib")
    ML_METADATA_PATH: str = str(BASE_DIR / "ml" / "metadata.json")

    # Disclaimer
    DISCLAIMER: str = (
        "Siddha AI is an academic engineering prototype trained on synthetic research data. "
        "It is designed solely to demonstrate digital parameter extraction and explainable ML, "
        "and is NOT intended for clinical diagnosis or treatment."
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
