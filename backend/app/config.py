import os
import json
from typing import List, Union
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

class Settings(BaseSettings):
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # CORS Origins (JSON list parser fallback)
    CORS_ORIGINS: Union[str, List[str]] = os.getenv(
        "CORS_ORIGINS", 
        '["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]'
    )
    
    # DB URL - defaults to local sqlite db using async aiosqlite driver
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./stockvision.db")
    
    # Sentiment API Keys
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY", "")
    
    # ML settings
    LOOKBACK_STEPS: int = int(os.getenv("LOOKBACK_STEPS", 60))
    FORECAST_HORIZON: int = int(os.getenv("FORECAST_HORIZON", 1))
    MODEL_CHECKPOINT_DIR: str = os.getenv("MODEL_CHECKPOINT_DIR", "./checkpoints")
    
    # Redis cache url
    REDIS_URL: str = os.getenv("REDIS_URL", "")

    class Config:
        case_sensitive = True

    @property
    def parsed_cors_origins(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        try:
            return json.loads(self.CORS_ORIGINS)
        except Exception:
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
