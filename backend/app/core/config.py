import os
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_ENV: Literal["development", "production", "testing"] = "development"
    MOCK_MODEL: bool = True
    
    # Hugging Face Settings
    HF_TOKEN: str | None = None
    HF_ADAPTER_REPO: str | None = None
    BASE_MODEL_ID: str = "defog/sqlcoder-7b-2"
    
    # Inference parameters
    DEVICE: str = "cpu"
    MAX_NEW_TOKENS: int = 512
    TEMPERATURE: float = 0.0
    TOP_P: float = 0.95
    
    # Recovery config
    RECOVERY_MAX_RETRIES: int = 2
    
    # Database config
    DEMO_DB_PATH: str = Field(
        default=os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data", "demo", "ecommerce.duckdb"
        )
    )

    # CORS config
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"

settings = Settings()

