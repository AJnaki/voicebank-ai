from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func, select, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.redis_client import get_redis
from app.models.call_log import CallLog

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def overview(db: AsyncSession = Depends(get_db)):
    today = datetime.now(timezone.utc).date()

    result = await db.execute(
        select(CallLog).where(func.date(CallLog.started_at) == today)
    )
    calls = result.scalars().all()

    total = len(calls)
    completed = [c for c in calls if c.ended_at is not None]
    durations = [c.duration_seconds for c in completed if c.duration_seconds]
    avg_duration = int(sum(durations) / len(durations)) if durations else 0
    escalated = sum(1 for c in calls if c.escalated)
    containment_rate = round((total - escalated) / total, 2) if total else 1.0

    # Count active sessions via Redis
    r = get_redis()
    active_keys = await r.keys("session:*")
    active = len(active_keys)

    all_intents: list[str] = []
    for c in calls:
        if c.intent_log:
            all_intents.extend(c.intent_log)
    top_intent = max(set(all_intents), key=all_intents.count) if all_intents else None

    return {
        "total_calls_today": total,
        "active_calls": active,
        "containment_rate": containment_rate,
        "avg_handle_time_seconds": avg_duration,
        "escalated_calls": escalated,
        "top_intent": top_intent,
    }


@router.get("/intents")
async def intent_analytics(days: int = 7, db: AsyncSession = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(select(CallLog).where(CallLog.started_at >= since))
    calls = result.scalars().all()

    intent_counts: dict[str, dict] = {}
    for c in calls:
        if not c.intent_log:
            continue
        escalated = c.escalated or False
        for intent in c.intent_log:
            if intent not in intent_counts:
                intent_counts[intent] = {"intent": intent, "count": 0, "escalated": 0}
            intent_counts[intent]["count"] += 1
            if escalated:
                intent_counts[intent]["escalated"] += 1

    return sorted(intent_counts.values(), key=lambda x: x["count"], reverse=True)


@router.get("/sentiment")
async def sentiment_trends(hours: int = 24, db: AsyncSession = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    result = await db.execute(select(CallLog).where(CallLog.started_at >= since))
    calls = result.scalars().all()

    buckets: dict[str, dict] = {}
    for c in calls:
        if not c.sentiment_log or not c.started_at:
            continue
        hour_key = c.started_at.strftime("%Y-%m-%dT%H:00")
        if hour_key not in buckets:
            buckets[hour_key] = {"hour": hour_key, "neutral": 0, "satisfied": 0,
                                  "frustrated": 0, "angry": 0, "confused": 0}
        for s in c.sentiment_log:
            if s in buckets[hour_key]:
                buckets[hour_key][s] += 1

    return sorted(buckets.values(), key=lambda x: x["hour"])


@router.get("/calls")
async def recent_calls(limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CallLog).order_by(CallLog.started_at.desc()).limit(limit)
    )
    calls = result.scalars().all()
    return [
        {
            "call_sid": c.call_sid,
            "user_id": c.user_id,
            "started_at": c.started_at.isoformat() if c.started_at else None,
            "duration_seconds": c.duration_seconds,
            "intent_log": c.intent_log or [],
            "sentiment_log": c.sentiment_log or [],
            "language": c.language or "en",
            "escalated": c.escalated or False,
            "biometric_score": c.biometric_score,
            "recording_url": c.recording_url,
        }
        for c in calls
    ]


@router.get("/auth")
async def auth_metrics(days: int = 7, db: AsyncSession = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(select(CallLog).where(CallLog.started_at >= since))
    calls = result.scalars().all()

    total = len(calls)
    pin_success = sum(1 for c in calls if c.auth_result and c.auth_result.get("pin_verified"))
    lockouts = sum(1 for c in calls if c.auth_result and not c.auth_result.get("pin_verified"))
    scores = [c.biometric_score for c in calls if c.biometric_score is not None]
    avg_biometric = int(sum(scores) / len(scores)) if scores else 0

    return {
        "total_auth_attempts": total,
        "pin_success_count": pin_success,
        "lockout_count": lockouts,
        "success_rate": round(pin_success / total, 2) if total else 0,
        "avg_biometric_score": avg_biometric,
    }
