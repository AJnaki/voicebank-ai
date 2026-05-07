from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    public_base_url: str = "http://localhost:8000"

    database_url: str = "postgresql+asyncpg://voicebank:voicebank@localhost:5432/voicebank"
    redis_url: str = "redis://localhost:6379/0"

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"

    ai_engine_api_key: str = ""
    ai_model: str = "claude-sonnet-4-6"

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    azure_speech_key: str = ""
    azure_speech_region: str = "eastus"

    bank_name: str = "First National Bank"
    agent_transfer_number: str = "+10000000000"
    audio_ttl_seconds: int = 300

    sendgrid_api_key: str = ""
    email_from: str = "noreply@voicebank.ai"

    otp_ttl_seconds: int = 300
    fund_transfer_otp_threshold: float = 500.0

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
