# Authentication Flow

## Three-Layer Security

VoiceBank AI uses three stacked authentication factors, designed to feel effortless to the caller while being bank-grade secure.

```
Layer 1: Identity        Layer 2: Knowledge       Layer 3: Biometric
──────────────────       ──────────────────       ──────────────────
First + Last Name    →   6-Digit PIN          →   Voice Print Match
(who you are)            (what you know)           (how you sound)
```

---

## Step-by-Step

### Step 1 — Greeting & Name Collection

The system plays a branded greeting immediately on call connection:

> *"Welcome to [Bank Name]. I'm your virtual assistant. To get started, please say your first and last name."*

- Deepgram captures the speech in real-time
- Name is normalized (trimmed, title-cased, accent-agnostic matching)
- Fuzzy matching handles slight mispronunciation (e.g., "Jonathon" → "Jonathan")
- Lookup against enrolled users in PostgreSQL

**Edge cases handled:**

| Scenario | Response |
|---|---|
| Name not found | "I couldn't find that name. Please try again or press 0 for an agent." |
| Multiple matches | "Are you John Smith calling from account ending in 4821? Say yes or no." |
| Background noise | "I didn't catch that clearly. Could you repeat your name?" |

---

### Step 2 — PIN Entry

Once name is matched:

> *"Thank you, John. Please enter your 6-digit PIN using your keypad."*

- PIN collected via Twilio DTMF (keypad) — never spoken aloud
- Stored as bcrypt hash in database — never in plaintext
- 3 attempts allowed before account lockout and agent escalation
- PIN can be 4–8 digits (bank-configurable)

---

### Step 3 — Voice Biometric (Background)

While the PIN is being entered and verified, the first 15 seconds of call audio is simultaneously sent to Azure Speaker Recognition.

- Runs **passively** — caller doesn't know it's happening
- Returns a confidence score (0–100)
- Score is stored against the session, not used to block access on its own
- Used for: fraud flagging, risk scoring, post-call review triggers

**Confidence thresholds:**

| Score | Action |
|---|---|
| 85–100 | Biometric verified — low risk session |
| 60–84 | Partial match — session proceeds, soft flag for review |
| Below 60 | Mismatch flagged — manager alerted, session still proceeds |
| No enrollment | Skip biometric, prompt for enrollment at end of call |

---

## Session State After Auth

```json
{
  "call_sid": "CA1234567890abcdef",
  "user_id": 1042,
  "user_name": "John Smith",
  "account_number": "****4821",
  "auth": {
    "name_verified": true,
    "pin_verified": true,
    "biometric_score": 91,
    "biometric_verified": true,
    "fully_authenticated": true
  },
  "risk_level": "low",
  "session_start": "2026-05-06T10:23:00Z"
}
```

---

## Lockout & Recovery

- **3 failed PINs** → session locked, immediate transfer to live agent
- **Account locked** → agent must manually unlock after identity verification
- **Suspicious biometric** → manager alert, session continues normally (caller unaware)
- **Voice enrollment** → offered at end of a successful authenticated call

---

## Enrollment Flow (First-Time Biometric Setup)

```
At end of successful call:
────────────────────────────────────────────────────────────
"John, would you like to set up voice recognition for faster
 access in the future? Just say 'yes' to begin."

→ Caller says yes
→ "Please say the following phrase three times:
   'My voice is my password at First National Bank'"
→ Azure collects 3 samples, builds voice print
→ Stored linked to user_id 1042
→ "Perfect! Voice recognition is now active on your account."
```
