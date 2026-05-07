from rapidfuzz import fuzz, process
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


async def find_user_by_spoken_name(
    spoken: str, db: AsyncSession, threshold: int = 75
) -> tuple[User | None, int]:
    """
    Returns (user, confidence_score) or (None, 0).
    confidence_score 90+ = auto-accept, 75-89 = ask confirming question, <75 = not found.
    """
    result = await db.execute(select(User))
    users = result.scalars().all()

    if not users:
        return None, 0

    spoken_lower = spoken.strip().lower()

    candidates = {u.id: u.full_name.lower() for u in users}
    best_id, best_score, _ = process.extractOne(
        spoken_lower,
        candidates,
        scorer=fuzz.token_sort_ratio,
    )

    if best_score < threshold:
        return None, best_score

    matched = next(u for u in users if u.id == best_id)
    return matched, best_score
