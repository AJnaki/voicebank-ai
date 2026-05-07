# Phase 1 — Foundation

**Goal:** A working end-to-end voice call that greets, authenticates, and routes to the right handler — with a live agent fallback.

**Timeline:** 3–4 weeks  
**Status:** 🔵 Current Phase

---

## Deliverables

| # | Deliverable | Description |
|---|---|---|
| 1.1 | Twilio integration | Receive inbound calls, play TTS, collect DTMF |
| 1.2 | Deepgram STT | Real-time speech-to-text streaming |
| 1.3 | ElevenLabs TTS | Natural voice responses played back via Twilio |
| 1.4 | Greeting flow | Welcome message + name collection |
| 1.5 | Name matching | Fuzzy + phonetic match against DB |
| 1.6 | PIN verification | DTMF collection + bcrypt verification |
| 1.7 | Voice biometrics | Azure enrollment + passive verification |
| 1.8 | Intent routing | AI Engine classifies intent → routes to handler |
| 1.9 | Mock bank API | Hardcoded responses for balance, transactions |
| 1.10 | Live agent transfer | Twilio Conference with transcript handoff |
| 1.11 | Session management | Redis: per-call state, auth flags, history |
| 1.12 | Call logging | PostgreSQL: full transcript, intent log, auth result |

---

## Project Structure

```
voicebank-ai/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Environment variables
│   ├── models/
│   │   ├── user.py              # User DB model
│   │   └── call_session.py      # Session state model
│   ├── services/
│   │   ├── twilio_service.py    # TwiML generation, call control
│   │   ├── deepgram_service.py  # STT streaming
│   │   ├── elevenlabs_service.py# TTS generation
│   │   ├── ai_engine_service.py # Intent classification + response
│   │   ├── azure_speaker.py     # Voice biometrics
│   │   └── bank_api.py          # Mock bank API (Phase 1) / Real (Phase 2)
│   ├── handlers/
│   │   ├── auth_handler.py      # Name + PIN + biometric flow
│   │   ├── intent_handler.py    # Routes intent to correct handler
│   │   ├── balance_handler.py
│   │   ├── transaction_handler.py
│   │   └── agent_handler.py     # Live agent escalation
│   ├── db/
│   │   ├── database.py          # PostgreSQL connection
│   │   └── redis_client.py      # Redis session store
│   └── webhooks/
│       └── twilio_webhooks.py   # Twilio POST webhook endpoints
├── tests/
│   ├── test_auth.py
│   ├── test_intent.py
│   └── test_call_flow.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Key Endpoints (Phase 1)

```
POST /webhook/call/incoming       ← Twilio calls this on new inbound call
POST /webhook/call/gather-name    ← Twilio sends STT result after name prompt
POST /webhook/call/gather-pin     ← Twilio sends DTMF digits after PIN prompt
POST /webhook/call/intent         ← Twilio sends STT after main prompt
POST /webhook/call/status         ← Twilio call status updates (ended, etc.)
GET  /health                      ← Health check
```

---

## Definition of Done

- [ ] Call connects and hears personalized greeting
- [ ] Name correctly identified from speech (tested with 10+ names)
- [ ] PIN verified via keypad (3-attempt lockout works)
- [ ] Voice biometric runs passively and logs score
- [ ] At least 5 intents correctly classified from natural speech
- [ ] "Talk to someone" successfully transfers with transcript
- [ ] All call events logged to PostgreSQL
- [ ] Redis session cleaned up after call ends
- [ ] Unit tests covering auth flow and intent routing
- [ ] Docker Compose runs full stack locally

---

## Mock Bank API (Phase 1 Data)

During Phase 1 the bank API is mocked with realistic hardcoded data so the full voice flow can be tested end-to-end before any real bank integration.

```python
MOCK_ACCOUNTS = {
    1042: {
        "name": "John Smith",
        "account_number": "****4821",
        "balance": 12450.75,
        "currency": "USD",
        "transactions": [
            {"date": "2026-05-05", "description": "Amazon", "amount": -89.99},
            {"date": "2026-05-04", "description": "Salary Deposit", "amount": 3500.00},
            {"date": "2026-05-03", "description": "Netflix", "amount": -15.99},
        ]
    }
}
```
