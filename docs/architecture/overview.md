# System Architecture Overview

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        VOICEBANK AI PLATFORM                        │
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐  │
│  │  Twilio  │───▶│ FastAPI  │───▶│ AI Engine│───▶│  Bank Core   │  │
│  │ Telephony│    │ Backend  │    │   AI     │    │  Banking API │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────────┘  │
│       │               │                                             │
│       │          ┌────┴────┐                                        │
│       │          │Deepgram │  (Speech-to-Text)                      │
│       │          └─────────┘                                        │
│       │          ┌────────────┐                                     │
│       │          │ ElevenLabs │  (Text-to-Speech)                   │
│       │          └────────────┘                                     │
│       │          ┌──────────────────┐                               │
│       │          │ Azure Speaker ID │  (Voice Biometrics)           │
│       │          └──────────────────┘                               │
│       │                                                             │
│  ┌────▼──────────────────────────────────────────────────────────┐  │
│  │                      PostgreSQL                               │  │
│  │   Sessions │ Users │ Call Logs │ Intent History │ Analytics  │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Twilio
Handles all telephony: inbound call reception, outbound call initiation, DTMF fallback (press 1, 2 if caller prefers), call recording, and SIP trunk integration with bank's existing phone infrastructure.

### FastAPI Backend
The central orchestrator. Manages call sessions, coordinates all service calls (STT, TTS, AI, biometrics), maintains state per call, routes intents to bank API handlers, and streams audio back to Twilio.

### Deepgram (Speech-to-Text)
Real-time streaming transcription. Chosen for sub-300ms latency, high accuracy on accented English, and financial terminology support.

### AI Engine
The intelligence layer. Receives transcript + call context, classifies intent, generates natural responses, handles multi-turn conversation memory within the call, and decides escalation triggers.

### ElevenLabs (Text-to-Speech)
Converts the AI Engine's text responses to natural speech. Each bank gets a custom voice profile — consistent brand identity across all calls.

### Azure Speaker Recognition
Enrolls caller voice print during onboarding. On future calls, verifies identity passively during the greeting phrase — no extra friction.

### PostgreSQL
Stores: enrolled users, call sessions, full transcripts, intent logs, voice print enrollment status, analytics aggregates.

### React Dashboard
Bank manager portal: live call monitoring, daily/weekly analytics, intent heatmaps, sentiment trends, unresolved query reports.
