from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class AuthState(BaseModel):
    name_verified: bool = False
    pin_verified: bool = False
    biometric_score: Optional[int] = None
    biometric_verified: bool = False
    fully_authenticated: bool = False
    pin_attempts: int = 0

    @property
    def risk_level(self) -> str:
        score = 0
        if self.name_verified:
            score += 30
        if self.pin_verified:
            score += 50
        if self.biometric_score is not None:
            if self.biometric_score >= 85:
                score += 20
            elif self.biometric_score >= 60:
                score += 10
        if score >= 80:
            return "low"
        if score >= 60:
            return "medium"
        return "high"


class TranscriptTurn(BaseModel):
    role: str  # "caller" or "assistant"
    text: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class CallSession(BaseModel):
    call_sid: str
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    account_number: Optional[str] = None
    auth: AuthState = Field(default_factory=AuthState)
    transcript: list[TranscriptTurn] = []
    intent_log: list[str] = []
    bank_name: str = "First National Bank"
    started_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    # Phase 2: tracks actions awaiting OTP or voice confirmation
    pending_action: Optional[str] = None
    pending_data: dict = Field(default_factory=dict)
    # Phase 3: intelligence & scale
    sentiment_log: list[str] = []
    language: str = "en"
    escalated: bool = False

    def add_turn(self, role: str, text: str) -> None:
        self.transcript.append(TranscriptTurn(role=role, text=text))

    def log_intent(self, intent: str) -> None:
        self.intent_log.append(intent)

    def set_pending(self, action: str, **data) -> None:
        self.pending_action = action
        self.pending_data = data

    def clear_pending(self) -> None:
        self.pending_action = None
        self.pending_data = {}

    def log_sentiment(self, sentiment: str) -> None:
        self.sentiment_log.append(sentiment)

    def consecutive_negative_sentiment(self) -> int:
        """Count trailing consecutive frustrated/angry turns."""
        count = 0
        for s in reversed(self.sentiment_log):
            if s in ("frustrated", "angry"):
                count += 1
            else:
                break
        return count
