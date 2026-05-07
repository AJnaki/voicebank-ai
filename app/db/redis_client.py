import json
from typing import Optional
import redis.asyncio as aioredis
from app.config import get_settings
from app.models.call_session import CallSession

settings = get_settings()

_redis: Optional[aioredis.Redis] = None

SESSION_TTL = 3600  # 1 hour — max call duration


def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def save_session(session: CallSession) -> None:
    r = get_redis()
    await r.setex(f"session:{session.call_sid}", SESSION_TTL, session.model_dump_json())


async def load_session(call_sid: str) -> Optional[CallSession]:
    r = get_redis()
    raw = await r.get(f"session:{call_sid}")
    if raw is None:
        return None
    return CallSession.model_validate_json(raw)


async def delete_session(call_sid: str) -> None:
    r = get_redis()
    await r.delete(f"session:{call_sid}")


async def store_audio(audio_id: str, audio_bytes: bytes, ttl: int) -> None:
    r = get_redis()
    await r.setex(f"audio:{audio_id}", ttl, audio_bytes)


async def fetch_audio(audio_id: str) -> Optional[bytes]:
    r = get_redis()
    return await r.get(f"audio:{audio_id}")
