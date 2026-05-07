# Phase 3 — Intelligence & Scale

**Goal:** Layer intelligence features on top of the working product, scale to multi-bank, and deliver the analytics dashboard that makes VoiceBank AI a platform rather than a single integration.

**Timeline:** 5–7 weeks  
**Status:** ⬜ Upcoming

---

## Deliverables

| # | Deliverable | Description |
|---|---|---|
| 3.1 | Sentiment detection | Real-time caller emotion detection → auto-escalation |
| 3.2 | Outbound proactive calls | AI calls customer for fraud alerts, low balance, due dates |
| 3.3 | Multi-language support | Auto-detect language, respond in caller's language |
| 3.4 | Manager analytics dashboard | React web portal with call insights |
| 3.5 | Fraud alert response flow | Caller responds to a flagged transaction live |
| 3.6 | Context-aware conversation | Remembers context across turns within the call |
| 3.7 | Post-call SMS summary | Caller receives SMS summary of what was done |
| 3.8 | Multi-bank white-labeling | Config-driven: each bank gets own number, voice, brand |
| 3.9 | Compliance recording | Encrypted call recording, searchable transcripts |
| 3.10 | Agent co-pilot | Live agent sees AI-suggested responses during handoff |

---

## Sentiment Detection

Uses a lightweight NLP model running in FastAPI to classify each transcript chunk:

```python
# Runs every 30 seconds of call audio
sentiments = ["neutral", "satisfied", "frustrated", "angry", "confused"]

# Escalation triggers:
if sentiment in ["angry", "frustrated"] and consecutive_count >= 2:
    → Offer agent: "I can hear this is frustrating. Would you like me to connect you to a team member?"

if sentiment == "confused" and failed_intents >= 2:
    → Simplify: re-explain options, offer agent
```

Sentiment history per call is logged and surfaced in the dashboard for quality review.

---

## Outbound Proactive Calls

The AI initiates calls to customers. Use cases:

| Trigger | Message |
|---|---|
| Fraud detected on card | "We noticed a suspicious transaction of $340 at a merchant in Spain. Did you make this purchase?" |
| Balance below threshold | "Your account balance has dropped below $100. Would you like to review your recent transactions?" |
| Loan EMI due in 3 days | "Your loan EMI of $350 is due on May 9th. Would you like to make the payment now?" |
| Cheque cleared | "Your cheque number 004521 has cleared successfully." |

```python
# Twilio outbound call initiation
client.calls.create(
    to="+1234567890",       # customer's registered number
    from_=BANK_NUMBER,
    url="https://api.voicebank.ai/outbound/fraud-alert",
    status_callback="https://api.voicebank.ai/webhook/call/status"
)
```

---

## Multi-Language Support

```python
# Language detection on first 5 seconds of speech via Deepgram
# Supported languages (Phase 3 launch):
LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "ar": "Arabic",
    "hi": "Hindi",
    "bn": "Bengali",
}

# Flow:
# 1. Deepgram detects language automatically
# 2. AI Engine system prompt switches to detected language
# 3. ElevenLabs voice switches to language-native voice
# 4. Bank can configure which languages to enable
```

---

## Analytics Dashboard

React portal accessible by bank managers. Built with Recharts.

### Dashboard Sections

**Overview (Today)**
- Total calls today
- Average handle time
- Containment rate (% resolved without agent)
- Calls currently active

**Intent Analytics**
- Top 10 intents by volume (bar chart)
- Intent resolution rate per category
- Intents that failed → fell through to agent

**Sentiment Trends**
- Hourly sentiment breakdown (line chart)
- Frustrated call spike alerts
- Calls escalated due to sentiment

**Authentication Analytics**
- Auth success / failure rate
- Biometric score distribution
- Lockout events

**Agent Handoff**
- Volume of transfers per hour
- Average time before caller requested agent
- Top reasons for agent transfer

---

## White-Label Config (Per Bank)

Each bank is fully configured without code changes:

```yaml
# bank_config/first_national.yml
bank_id: first_national
display_name: "First National Bank"
phone_number: "+18005551234"
voice_id: "eleven_labs_voice_id_abc123"   # Custom ElevenLabs voice
greeting: "Welcome to First National Bank."
language_default: "en"
languages_enabled: ["en", "es"]
pin_length: 6
biometric_threshold: 70
agent_transfer_number: "+18005554321"
features:
  fund_transfer: true
  bill_payment: true
  loan_enquiry: true
  card_block: true
  outbound_calls: true
  sentiment_escalation: true
```

---

## Post-Call SMS Summary

At the end of every call, a brief SMS is sent to the caller's registered number:

```
First National Bank
─────────────────────
Call summary (May 6, 2026 10:24 AM)

✓ Balance checked: $12,450.75
✓ Statement emailed to j***@gmail.com
✓ Card ending 4821 blocked

Questions? Call 1-800-555-1234
```

---

## Definition of Done

- [ ] Sentiment detection correctly triggers escalation offer in test calls
- [ ] Outbound call system tested with 3 trigger types
- [ ] 3+ languages tested end-to-end
- [ ] Dashboard renders all 5 sections with real call data
- [ ] Multi-bank config: 2 banks run independently from same deployment
- [ ] Post-call SMS delivered within 30 seconds of call end
- [ ] Compliance recordings encrypted and stored in S3
- [ ] Agent co-pilot shows live suggestions during a transferred call
- [ ] Load test: 50 concurrent calls without degraded latency
