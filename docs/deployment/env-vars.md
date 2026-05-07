# Environment Variables

Copy `.env.example` to `.env` and fill in all values before running.

## Required Variables

```bash
# ── App ──────────────────────────────────────────────────────────
APP_ENV=development                  # development | staging | production
SECRET_KEY=your-random-secret-key    # Used for session signing

# ── Database ─────────────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/voicebank
REDIS_URL=redis://localhost:6379/0

# ── Twilio ───────────────────────────────────────────────────────
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+18005551234

# ── Deepgram (Speech-to-Text) ────────────────────────────────────
DEEPGRAM_API_KEY=your_deepgram_key

# ── ElevenLabs (Text-to-Speech) ──────────────────────────────────
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=default_voice_id   # Override per bank in bank config

# ── AI Engine ────────────────────────────────────────────────────
AI_ENGINE_API_KEY=your_ai_engine_key
AI_MODEL=sonnet-4-6

# ── Azure Speaker Recognition ────────────────────────────────────
AZURE_SPEECH_KEY=your_azure_key
AZURE_SPEECH_REGION=eastus             # e.g. eastus, westeurope

# ── AWS (Production only) ────────────────────────────────────────
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=voicebank-recordings

# ── Email (Statement dispatch) ───────────────────────────────────
SENDGRID_API_KEY=your_sendgrid_key
EMAIL_FROM=noreply@voicebank.ai

# ── SMS (Post-call summary) ──────────────────────────────────────
# Uses Twilio SMS — no extra key needed

# ── Bank Config ──────────────────────────────────────────────────
BANK_CONFIG_PATH=./bank_config/first_national.yml
```

## `.env.example`

This file is committed to the repo (with no real values) so developers know what to fill in:

```bash
APP_ENV=development
SECRET_KEY=change-me

DATABASE_URL=postgresql+asyncpg://voicebank:voicebank@localhost:5432/voicebank
REDIS_URL=redis://localhost:6379/0

TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

DEEPGRAM_API_KEY=
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=

AI_ENGINE_API_KEY=
AI_MODEL=

AZURE_SPEECH_KEY=
AZURE_SPEECH_REGION=eastus

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
S3_BUCKET_NAME=

SENDGRID_API_KEY=
EMAIL_FROM=

BANK_CONFIG_PATH=./bank_config/default.yml
```

!!! warning "Never commit `.env`"
    The `.env` file with real keys must never be committed to git. It is in `.gitignore` by default.
