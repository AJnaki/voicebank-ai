import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.db.redis_client import load_session
from app.services.summary_service import generate_agent_briefing

router = APIRouter(prefix="/ws", tags=["agent-copilot"])


@router.websocket("/agent-copilot/{call_sid}")
async def agent_copilot(websocket: WebSocket, call_sid: str):
    """
    WebSocket endpoint for the live agent co-pilot screen.
    Sends the caller's full context + AI briefing on connect,
    then streams transcript updates every 3 seconds.
    """
    await websocket.accept()

    session = await load_session(call_sid)
    if session is None:
        await websocket.send_json({"error": "Session not found"})
        await websocket.close()
        return

    briefing = await generate_agent_briefing(session)

    await websocket.send_json({
        "type": "session_context",
        "caller_name": session.user_name,
        "account_number": session.account_number,
        "auth_risk": session.auth.risk_level,
        "biometric_score": session.auth.biometric_score,
        "intents": session.intent_log,
        "last_sentiment": session.sentiment_log[-1] if session.sentiment_log else "neutral",
        "briefing": briefing,
        "transcript": [t.model_dump() for t in session.transcript[-10:]],
    })

    try:
        while True:
            # Poll for session updates every 3 seconds
            await asyncio.sleep(3)
            updated = await load_session(call_sid)
            if updated is None:
                await websocket.send_json({"type": "call_ended"})
                break
            # Send only new transcript turns
            new_turns = updated.transcript[len(session.transcript):]
            if new_turns:
                await websocket.send_json({
                    "type": "transcript_update",
                    "turns": [t.model_dump() for t in new_turns],
                    "current_sentiment": (
                        updated.sentiment_log[-1] if updated.sentiment_log else "neutral"
                    ),
                })
                session = updated
    except WebSocketDisconnect:
        pass
