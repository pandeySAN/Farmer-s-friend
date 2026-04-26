from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "FarmerAI"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Auth — generate with: python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Gemini (Google)
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Weather (free tier available at openweathermap.org)
    OPENWEATHER_API_KEY: str

    # Vector memory (free tier: 1 index at pinecone.io)
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX: str = "farmer-memory"

    # Cache & sessions
    REDIS_URL: str = "redis://localhost:6379"

    # Optional: WhatsApp alerts via Twilio
    TWILIO_SID: str = ""
    TWILIO_TOKEN: str = ""
    TWILIO_WHATSAPP_FROM: str = ""

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
