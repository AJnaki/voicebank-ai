from app.models.call_session import CallSession
from app.db.redis_client import save_session


async def prepare_agent_handoff(session: CallSession, reason: str = "caller_request") -> str:
    """
    Marks the session as escalated and returns a summary string
    that can be passed to the live agent screen.
    """
    session.log_intent(f"escalate:{reason}")
    await save_session(session)

    lines = [
        f"Caller: {session.user_name}",
        f"Account: {session.account_number}",
        f"Auth: PIN {'✓' if session.auth.pin_verified else '✗'}, "
        f"Biometric score: {session.auth.biometric_score or 'N/A'}",
        f"Risk level: {session.auth.risk_level}",
        f"Intents this call: {', '.join(session.intent_log) or 'none'}",
        f"Reason for transfer: {reason}",
    ]
    return "\n".join(lines)
