import secrets
from app.db.redis_client import get_redis
from app.config import get_settings

settings = get_settings()


async def generate_otp(call_sid: str) -> str:
    code = f"{secrets.randbelow(900000) + 100000}"
    r = get_redis()
    await r.setex(f"otp:{call_sid}", settings.otp_ttl_seconds, code)
    return code


async def verify_otp(call_sid: str, entered: str) -> bool:
    r = get_redis()
    stored = await r.get(f"otp:{call_sid}")
    if stored and stored.strip() == entered.strip():
        await r.delete(f"otp:{call_sid}")
        return True
    return False


async def clear_otp(call_sid: str) -> None:
    r = get_redis()
    await r.delete(f"otp:{call_sid}")
