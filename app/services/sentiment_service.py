import re

ANGRY_PATTERNS = [
    r"\b(furious|outraged|livid|ridiculous|unacceptable|disgrace|terrible|horrible|awful)\b",
    r"\b(useless|incompetent|pathetic|scam|fraud|liar|idiot)\b",
    r"(this is a joke|what the hell|are you kidding)",
]
FRUSTRATED_PATTERNS = [
    r"\b(again|still|already|keep|keeps|every time|always|never works|doesn't work)\b",
    r"\b(frustrated|annoyed|upset|unhappy|fed up|sick of)\b",
    r"\b(how many times|told you|waiting|forever|ridiculous)\b",
]
CONFUSED_PATTERNS = [
    r"\b(don't understand|confused|what do you mean|can you explain|not sure|unclear)\b",
    r"\b(how does|what is|what are|what's the difference|explain)\b",
]
SATISFIED_PATTERNS = [
    r"\b(thank|thanks|great|perfect|excellent|wonderful|appreciate|helpful)\b",
    r"\b(that's all|that's it|that works|sounds good|got it)\b",
]

_COMPILED = {
    "angry": [re.compile(p, re.IGNORECASE) for p in ANGRY_PATTERNS],
    "frustrated": [re.compile(p, re.IGNORECASE) for p in FRUSTRATED_PATTERNS],
    "confused": [re.compile(p, re.IGNORECASE) for p in CONFUSED_PATTERNS],
    "satisfied": [re.compile(p, re.IGNORECASE) for p in SATISFIED_PATTERNS],
}


def detect_sentiment(text: str) -> str:
    """
    Fast keyword-based sentiment detection.
    Returns: angry | frustrated | confused | satisfied | neutral
    """
    if not text:
        return "neutral"
    for label in ("angry", "frustrated", "confused", "satisfied"):
        if any(p.search(text) for p in _COMPILED[label]):
            return label
    return "neutral"


def should_offer_agent(sentiment_log: list[str], failed_intents: int = 0) -> bool:
    """True when we should proactively offer a live agent."""
    if not sentiment_log:
        return False

    # 2+ consecutive angry/frustrated
    consecutive = 0
    for s in reversed(sentiment_log):
        if s in ("angry", "frustrated"):
            consecutive += 1
        else:
            break
    if consecutive >= 2:
        return True

    # confused + 2 failed intents
    if "confused" in sentiment_log[-3:] and failed_intents >= 2:
        return True

    return False


ESCALATION_OFFER = (
    "I want to make sure I'm helping you the best I can. "
    "Would you like me to connect you with a team member right now?"
)
