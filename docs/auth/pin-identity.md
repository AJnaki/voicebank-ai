# PIN & Identity Verification

## Name Matching Strategy

Raw speech-to-text output is imperfect. The name matching pipeline uses multiple techniques to handle real-world speech:

```python
# Pipeline:
# 1. Deepgram transcript → "john smyth"
# 2. Normalize: strip punctuation, lowercase → "john smyth"
# 3. Exact match against DB → No match
# 4. Fuzzy match (Levenshtein distance ≤ 2) → "john smith" [score: 95]
# 5. Phonetic match (Soundex/Metaphone) → fallback for heavy accents
# 6. If score ≥ 80: accept with confidence
# 7. If 60–79: ask confirming question
# 8. If < 60: "I couldn't find that name" → retry or agent
```

### Confirming Question Example

When multiple accounts share similar names:

> *"I found a John Smith. Are you calling about the account ending in 4821? Say yes or no."*

---

## PIN Security

| Requirement | Implementation |
|---|---|
| Storage | bcrypt hash (cost factor 12), never plaintext |
| Collection | Twilio DTMF only — never spoken, never in transcript |
| Length | 4–8 digits (bank-configurable) |
| Attempts | Max 3 before lockout |
| Lockout | Instant transfer to agent, flag in DB |
| Reset | Only via authenticated branch visit or video KYC |

### PIN Verification Code Flow

```python
async def verify_pin(user_id: int, entered_pin: str, session: CallSession) -> bool:
    user = await db.get_user(user_id)
    
    if user.pin_attempts >= 3:
        await escalate_to_agent(session, reason="account_locked")
        return False
    
    if bcrypt.checkpw(entered_pin.encode(), user.pin_hash):
        await db.reset_pin_attempts(user_id)
        session.auth.pin_verified = True
        return True
    else:
        await db.increment_pin_attempts(user_id)
        remaining = 3 - (user.pin_attempts + 1)
        if remaining == 0:
            await escalate_to_agent(session, reason="max_attempts")
        return False
```

---

## Multi-Factor Score

At the end of authentication, a combined risk score is computed:

```
risk_score = 0

if name_verified:       risk_score += 30
if pin_verified:        risk_score += 50
if biometric >= 85:     risk_score += 20
elif biometric >= 60:   risk_score += 10

# Risk levels:
# 80–100: low_risk    → full access
# 60–79:  medium_risk → limited transfers, flag for review
# < 60:   high_risk   → read-only access, agent notified
```

This allows the bank to configure different access tiers based on how confident the authentication was.
