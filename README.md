# DataDialogue — Seamless Self-Service Data Intelligence

> **NatWest Hackathon** · Talk to Data · Multi-Agent AI Platform

Upload CSV or PDF files and ask questions in plain English. Get instant AI-powered answers with auto-generated charts, source citations, and a full audit trail.

---

## Quick Start

### Prerequisites
- Docker Desktop running
- An Anthropic API key

### Step 1 — Configure environment
```bash
cp .env.example .env
# Edit .env → set ANTHROPIC_API_KEY=sk-ant-...
```

### Step 2 — Build and run
```bash
make build   # Build all Docker images
make dev     # Start all 7 services
```

### Step 3 — Access
| Service   | URL                         |
|-----------|-----------------------------|
| App       | http://localhost             |
| API Docs  | http://localhost/docs        |
| MinIO     | http://localhost:9001        |

### Step 4 — Run migrations & seed
```bash
make migrate   # Run Alembic migrations
make seed      # Seed metric dictionary
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Nginx :80                            │
│         ┌──────────┐         ┌──────────────┐           │
│         │ React UI │  /api/  │ FastAPI      │           │
│         │ :5173    │ ──────► │ :8000        │           │
│         └──────────┘         └──────┬───────┘           │
│                                     │                    │
│                    ┌────────────────┤                    │
│                    ▼                ▼                    │
│             ┌────────────┐  ┌────────────┐              │
│             │ PostgreSQL │  │   Redis    │              │
│             │ + pgvector │  │   Cache    │              │
│             └────────────┘  └────────────┘              │
│                    │                                     │
│                    ▼                                     │
│             ┌────────────┐  ┌─────────────┐             │
│             │   MinIO    │  │ Celery      │             │
│             │   Storage  │  │ Worker      │             │
│             └────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────┘
```

## AI Agent Pipeline (LangGraph)

```
User Question
     │
     ▼
[Intent Classifier] ── classify intent + extract entities
     │
     ├── CSV ──► [SQL Agent] ──► [Execute SQL] ──► [Verifier]
     │                                                │
     └── PDF ──► [RAG Agent] ──► [Metric Augment] ──►│
                                                      │
                                                      ▼
                                              [Synthesiser]
                                                      │
                                                      ▼
                                    Plain-English Answer + Chart + Citations
```

## Tech Stack

| Layer     | Technology                               |
|-----------|------------------------------------------|
| Frontend  | React 18, TypeScript, Tailwind, Recharts |
| Backend   | FastAPI, SQLAlchemy, Alembic             |
| AI        | Anthropic Claude, LangGraph, DuckDB     |
| Search    | pgvector, sentence-transformers          |
| Storage   | PostgreSQL, Redis, MinIO                 |
| Infra     | Docker Compose, Nginx, Celery            |

## Makefile Commands

```bash
make build      # Build Docker images
make dev        # Start services (dev mode)
make down       # Stop all services
make migrate    # Run database migrations
make seed       # Seed metric dictionary
make test       # Run backend test suite
make logs       # Tail logs from all services
```

---

**Built for the NatWest Hackathon** · DataDialogue Team
