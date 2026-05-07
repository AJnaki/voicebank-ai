from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.config import get_settings
from app.db.database import create_tables
from app.db.redis_client import get_redis
from app.services.elevenlabs_service import get_audio_bytes
from app.webhooks.twilio_webhooks import router as twilio_router
from app.webhooks.outbound_webhooks import router as outbound_router
from app.webhooks.analytics import router as analytics_router
from app.webhooks.agent_copilot import router as copilot_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    get_redis()
    yield


app = FastAPI(
    title="VoiceBank AI",
    description="AI Voice Assistant Platform for Banking",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(twilio_router)
app.include_router(outbound_router)
app.include_router(analytics_router)
app.include_router(copilot_router)


@app.get("/health")
async def health():
    return {"status": "ok", "bank": settings.bank_name, "env": settings.app_env, "phase": 3}


@app.get("/audio/{audio_id}")
async def serve_audio(audio_id: str):
    audio_bytes: Optional[bytes] = await get_audio_bytes(audio_id)
    if audio_bytes is None:
        raise HTTPException(status_code=404, detail="Audio not found or expired")
    return Response(content=audio_bytes, media_type="audio/mpeg")
