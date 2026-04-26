# 🌾 FarmerAI — AI-Powered Crop Planning Assistant

An intelligent multi-agent system built for Indian farmers. Combines real-time weather data, market prices, soil science, and Gemini AI to give personalized crop recommendations in Hindi and English.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, Tailwind CSS, shadcn/ui, Framer Motion |
| Backend | FastAPI, LangGraph, Python 3.11+ |
| AI | Gemini (gemini-1.5-flash) via Google AI Studio |
| Database | PostgreSQL 16 (via SQLAlchemy + Alembic) |
| Cache | Redis 7 |
| Vector Memory | Pinecone |
| Weather | OpenWeatherMap API |
| Market Data | data.gov.in Agmarknet API |
| Deployment | AWS (ECS Fargate + RDS + ElastiCache + CloudFront) |

## Quick Start

### 1. Clone and setup

```bash
git clone <your-repo>
cd farmer-ai
```

### 2. Configure environment

```bash
# Backend secrets
cp backend/.env.example backend/.env
# Edit backend/.env and fill in your API keys
```

### 3. Start with Docker

```bash
docker compose up --build
```

Visit:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

### 4. Run manually (development)

```bash
# Terminal 1 — Start DB + Redis
docker compose up postgres redis -d

# Terminal 2 — Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Terminal 3 — Frontend
cd frontend
npm install
npm run dev
```

## Project Structure

```
farmer-ai/
├── frontend/          # Next.js 14 app
│   └── src/
│       ├── app/       # App Router pages
│       ├── components/ # UI components
│       └── lib/       # API client, utils
├── backend/           # FastAPI + LangGraph
│   ├── app/
│   │   ├── agents/    # 5 AI agents + orchestrator
│   │   ├── core/      # Config, DB, security, deps
│   │   ├── routers/   # API endpoints
│   │   └── schemas/   # DB models + Pydantic schemas
│   └── ml_training/   # XGBoost + Prophet training scripts
└── docker-compose.yml
```

## Agent Pipeline

```
User Query
    │
    ▼
┌─────────────────────────────────────┐
│         LangGraph Orchestrator       │
│                                     │
│  ┌──────────┐    ┌───────────────┐  │
│  │ Weather  │    │    Memory     │  │  ← Run in parallel
│  │  Agent   │    │    Agent      │  │
│  └────┬─────┘    └───────┬───────┘  │
│       └──────┬───────────┘          │
│              ▼                      │
│  ┌──────────────┐  ┌─────────────┐  │
│  │     Crop     │  │   Market    │  │  ← Run in parallel
│  │    Agent     │  │    Agent    │  │
│  └──────┬───────┘  └──────┬──────┘  │
│         └────────┬─────────┘        │
│                  ▼                  │
│         ┌────────────────┐          │
│         │   Resource     │          │
│         │    Agent       │          │
│         └───────┬────────┘          │
│                 ▼                   │
│      ┌──────────────────┐           │
│      │  Gemini Reasoning │          │
│      │  (Final Answer)   │          │
│      └──────────────────┘           │
└─────────────────────────────────────┘
```

## API Keys Required

| Key | Where to get |
|-----|-------------|
| `GEMINI_API_KEY` | aistudio.google.com |
| `OPENWEATHER_API_KEY` | openweathermap.org (free tier) |
| `PINECONE_API_KEY` | pinecone.io (free tier, optional) |

## License

MIT
