"""Settings — LinkedIn Pipeline"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ── LLM ────────────────────────────────────────────────────────────
    gemini_api_key: str = Field(default="")
    gemini_model: str = "gemini-2.5-flash-lite"
    groq_api_key: str = Field(default="")
    groq_model: str = "llama-3.3-70b-versatile"
    active_llm: str = "gemini"
    llm_timeout_seconds: int = 30

    # ── LinkedIn OAuth2 ────────────────────────────────────────────────
    # Long-lived access token (valid 2 months, refresh manually)
    linkedin_access_token: str = Field(default="")
    linkedin_person_urn: str = Field(default="")  # urn:li:person:XXXXXXX

    # ── Telegram notifications ─────────────────────────────────────────
    telegram_bot_token: str = Field(default="")
    telegram_allowed_user_id: str = Field(default="")

    class Config:
        env_file = ".env"
        extra = "ignore"
