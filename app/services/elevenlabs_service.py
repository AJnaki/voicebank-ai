import asyncio
import uuid
from typing import Optional

from elevenlabs.client import ElevenLabs

from app.config import get_settings
from app.db.redis_client import fetch_audio, store_audio

settings = get_settings()

_client: Optional[ElevenLabs] = None


def _get_client() -> ElevenLabs:
    global _client
    if _client is None:
        _client = ElevenLabs(api_key=settings.elevenlabs_api_key)
    return _client


def _generate_sync(text: str, voice_id: str) -> bytes:
    client = _get_client()
    audio_generator = client.generate(
        text=text,
        voice=voice_id,
        model="eleven_turbo_v2_5",
    )
    return b"".join(audio_generator)


async def tts_url(text: str, voice_id: Optional[str] = None) -> str:
    """Generate TTS audio and return a URL Twilio can play."""
    vid = voice_id or settings.elevenlabs_voice_id
    loop = asyncio.get_event_loop()
    audio_bytes = await loop.run_in_executor(None, _generate_sync, text, vid)

    audio_id = str(uuid.uuid4())
    await store_audio(audio_id, audio_bytes, settings.audio_ttl_seconds)

    return f"{settings.public_base_url}/audio/{audio_id}"


async def get_audio_bytes(audio_id: str) -> Optional[bytes]:
    return await fetch_audio(audio_id)
