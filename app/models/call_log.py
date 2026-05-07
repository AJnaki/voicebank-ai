from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String
from app.models.base import Base


class CallLog(Base):
    __tablename__ = "call_logs"

    id = Column(Integer, primary_key=True, index=True)
    call_sid = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    started_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    ended_at = Column(DateTime(timezone=True), nullable=True)
    auth_result = Column(JSON, nullable=True)
    transcript = Column(JSON, default=list, nullable=False)
    intent_log = Column(JSON, default=list, nullable=False)
    biometric_score = Column(Integer, nullable=True)
    # Phase 3 columns
    sentiment_log = Column(JSON, default=list, nullable=True)
    language = Column(String(10), default="en", nullable=True)
    recording_url = Column(String(500), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    escalated = Column(Boolean, default=False, nullable=True)
