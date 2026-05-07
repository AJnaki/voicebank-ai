from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

from app.config import get_settings
from app.db.database import create_tables
from app.db.redis_client import get_redis
from app.services.elevenlabs_service import get_audio_bytes
from app.webhooks.twilio_webhooks import router as twilio_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    get_redis()  # warm up connection
    yield


app = FastAPI(
    title="VoiceBank AI",
    description="AI Voice Assistant Platform for Banking",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(twilio_router)


@app.get("/health")
async def health():
    return {"status": "ok", "bank": settings.bank_name, "env": settings.app_env}


@app.get("/audio/{audio_id}")
async def serve_audio(audio_id: str):
    """Serve a pre-generated TTS audio clip to Twilio."""
    audio_bytes: Optional[bytes] = await get_audio_bytes(audio_id)
    if audio_bytes is None:
        raise HTTPException(status_code=404, detail="Audio not found or expired")
    return Response(content=audio_bytes, media_type="audio/mpeg")
