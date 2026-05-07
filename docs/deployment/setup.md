# Setup Guide

## Prerequisites

- Python 3.11+
- Docker + Docker Compose
- Twilio account with a phone number
- Deepgram API key
- ElevenLabs API key
- AI Engine API key
- Azure Cognitive Services account
- PostgreSQL 15+
- Redis 7+

---

## Local Development Setup

### 1. Clone and install

```bash
git clone https://github.com/your-org/voicebank-ai
cd voicebank-ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your API keys (see Environment Variables page)
```

### 3. Start dependencies

```bash
docker-compose up -d postgres redis
```

### 4. Run database migrations

```bash
alembic upgrade head
```

### 5. Seed a test user

```bash
python scripts/seed_user.py --name "John Smith" --pin 123456
```

### 6. Expose local server (Twilio needs a public URL)

```bash
ngrok http 8000
# Copy the https URL — add to Twilio webhook config
```

### 7. Start the API

```bash
uvicorn app.main:app --reload --port 8000
```

### 8. Configure Twilio webhook

In the Twilio Console → Phone Numbers → your number:
- Voice webhook (HTTP POST): `https://your-ngrok-url/webhook/call/incoming`

### 9. Make a test call

Call your Twilio number. You should hear the greeting.

---

## Docker Compose (Full Stack)

```bash
docker-compose up --build
```

This starts: FastAPI app, PostgreSQL, Redis

---

## Running Tests

```bash
pytest tests/ -v
pytest tests/test_auth.py -v          # Auth flow tests
pytest tests/test_intent.py -v        # Intent routing tests
pytest tests/test_call_flow.py -v     # End-to-end call simulation
```

---

## Production Deployment (AWS ECS)

1. Build and push Docker image to ECR
2. Create ECS service with 2+ tasks for redundancy
3. Set up Application Load Balancer
4. RDS PostgreSQL (Multi-AZ)
5. ElastiCache Redis cluster
6. S3 bucket for recordings and PDFs
7. CloudFront for React dashboard
8. Update Twilio webhooks to production ALB URL
9. Set all environment variables in ECS task definition

```bash
# Build and push
docker build -t voicebank-ai .
docker tag voicebank-ai:latest $ECR_URL/voicebank-ai:latest
docker push $ECR_URL/voicebank-ai:latest

# Deploy
aws ecs update-service --cluster voicebank --service voicebank-api --force-new-deployment
```
