import httpx
from typing import Optional
from app.config import get_settings

settings = get_settings()

BASE_URL = "https://{region}.api.cognitive.microsoft.com/speaker/verification/v2.0/text-independent/profiles"


def _headers() -> dict:
    return {"Ocp-Apim-Subscription-Key": settings.azure_speech_key}


def _base() -> str:
    return BASE_URL.format(region=settings.azure_speech_region)


async def create_profile() -> Optional[str]:
    """Create a new voice profile. Returns profileId or None on failure."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(_base(), headers=_headers(), json={"locale": "en-US"})
    if resp.status_code == 200:
        return resp.json().get("profileId")
    return None


async def enroll(profile_id: str, audio_bytes: bytes) -> bool:
    """Submit audio for enrollment. Returns True when enrollment is complete."""
    url = f"{_base()}/{profile_id}/enrollments"
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            url,
            headers={**_headers(), "Content-Type": "audio/wav"},
            content=audio_bytes,
        )
    data = resp.json()
    return data.get("enrollmentStatus") == "Enrolled"


async def verify(profile_id: str, audio_bytes: bytes) -> int:
    """
    Verify caller against a stored profile.
    Returns confidence score 0-100, or -1 on error.
    """
    url = f"{_base()}/{profile_id}/verify"
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            url,
            headers={**_headers(), "Content-Type": "audio/wav"},
            content=audio_bytes,
        )
    if resp.status_code != 200:
        return -1
    data = resp.json()
    score = data.get("score", 0)
    return int(score * 100)


async def delete_profile(profile_id: str) -> bool:
    url = f"{_base()}/{profile_id}"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.delete(url, headers=_headers())
    return resp.status_code == 204


async def verify_from_recording_url(profile_id: str, recording_url: str) -> int:
    """Download a Twilio recording and run biometric verification against it."""
    async with httpx.AsyncClient(timeout=30) as client:
        audio_resp = await client.get(recording_url)
        if audio_resp.status_code != 200:
            return -1
        return await verify(profile_id, audio_resp.content)
