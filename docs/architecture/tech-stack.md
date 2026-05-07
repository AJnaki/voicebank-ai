# Technology Stack

## Stack at a Glance

| Layer | Technology | Why |
|---|---|---|
| Telephony | **Twilio** | Industry standard, SIP support, DTMF, recording, outbound |
| Speech-to-Text | **Deepgram** | Sub-300ms latency, financial vocab, accented English |
| Text-to-Speech | **ElevenLabs** | Most natural voice, custom voice cloning per bank |
| AI / NLU | **VoiceBank AI Engine** | Best intent classification + multi-turn conversation memory |
| Voice Biometrics | **Azure Speaker Recognition** | Passive voice print verification, GDPR compliant |
| Backend | **Python + FastAPI** | Async performance, easy WebSocket streaming |
| Database | **PostgreSQL** | Reliable, audit logs, JSONB for flexible call data |
| Cache / Sessions | **Redis** | In-memory call state, fast session lookup |
| Dashboard | **React + Recharts** | Manager analytics portal |
| Deployment | **Docker + AWS ECS** | Scalable, bank-grade infrastructure |
| CI/CD | **GitHub Actions** | Automated testing and deployment pipeline |

---

## Service Deep Dives

### Twilio
```python
# What Twilio gives us
- Inbound call webhooks (POST to our FastAPI)
- TwiML: play audio, gather speech/DTMF, redirect
- Conference rooms for agent transfer
- Call recording (stored S3)
- Outbound call initiation (proactive alerts)
- Phone number provisioning per bank
```

### Deepgram Streaming STT
```python
# Real-time streaming — no waiting for caller to finish
- Nova-2 model: best accuracy for conversational speech
- endpointing: detects when caller stops speaking (200ms)
- smart_format: capitalizes names, formats numbers/currency
- diarize: separates caller vs background noise
```

### AI Engine
```python
# System prompt per bank includes:
- Bank name, tone, available services
- Current authenticated user context
- Call history so far (within session)
- Instructions: classify intent, generate short spoken response
- Escalation triggers: frustration, 3 failed intents, explicit request
```

### ElevenLabs TTS
```python
# Per bank voice setup:
- Custom voice clone or pre-built professional voice
- Streaming audio chunks back to Twilio (low latency)
- SSML support: pacing, emphasis, pauses for natural speech
- Consistent voice = brand identity across all calls
```

### Azure Speaker Recognition
```python
# Two-phase flow:
# 1. Enrollment (one-time, during account setup or first call)
- Caller says a passphrase or has 30s of speech collected
- Voice print stored securely linked to user_id

# 2. Verification (every call, passive)
- First 10-15 seconds of call audio sent to Azure
- Returns confidence score 0-100
- < 70: flag for review but don't block
- >= 70: mark biometric_verified = True
```

---

## Infrastructure

```
                    ┌─────────────────────────────────┐
                    │          AWS Cloud               │
                    │                                  │
  Twilio ──────────▶│  ECS (FastAPI containers)        │
                    │      │                           │
                    │      ├── ElastiCache (Redis)     │
                    │      ├── RDS PostgreSQL          │
                    │      └── S3 (recordings, PDFs)  │
                    │                                  │
                    │  CloudFront (React Dashboard)    │
                    └─────────────────────────────────┘
                              │
                    External Services:
                    Deepgram · ElevenLabs · Azure · AI Engine API
                    Bank Core Banking REST API
```

---

## Cost Estimates (per bank, monthly)

| Service | Volume | Est. Cost |
|---|---|---|
| Twilio | 10,000 min/month | ~$120 |
| Deepgram | 10,000 min/month | ~$50 |
| ElevenLabs | 10,000 min/month | ~$100 |
| AI Engine API | 10,000 calls | ~$80 |
| Azure Speaker | 10,000 verifications | ~$15 |
| AWS (ECS + RDS) | Always-on | ~$150 |
| **Total** | | **~$515/month** |

!!! note "Pricing Note"
    This is a rough baseline. Volume discounts apply at scale. SaaS pricing to banks should be $1,500–$5,000/month depending on call volume tier, making margins strong.
