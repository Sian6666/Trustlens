# TrustLens

TrustLens is a production-oriented full stack platform for real-time scam and misinformation detection. It combines authenticated reporting, explainable risk scoring, community validation, searchable incident history, trend analytics, WebSocket live updates, rate limiting, caching, containerized deployment, health checks, automated tests, and CI.

## Why this project matters

Scam detection is a practical trust-and-safety problem: the system must classify risky content, explain the result to users, accept community feedback, and keep the dashboard responsive as reports arrive. TrustLens is designed to demonstrate product sense, backend API design, frontend implementation, security awareness, and system design tradeoffs in one coherent project.

## Core Features

- Authenticated signup, login, and protected write operations with JWT access tokens.
- Explainable detector with keyword, pattern, URL, urgency, impersonation, and payment-risk signals.
- Real-time Socket.IO feed for new submissions and community votes.
- Community voting with duplicate-vote protection.
- Search, pagination, category filtering, trending reports, and daily risk charts.
- Redis-backed dashboard cache with in-memory fallback for local development.
- Health and readiness endpoints for deployment platforms.
- Security headers, CORS restrictions, input sanitization, password hashing, and rate limits.
- Docker Compose for PostgreSQL, Redis, Flask API, and React frontend.
- Pytest API/unit tests and GitHub Actions CI.

## Stack

- Frontend: React, Vite, Recharts, Socket.IO client, lucide-react
- Backend: Flask, Flask-SocketIO, SQLAlchemy, Flask-JWT-Extended, Flask-Limiter
- Database: PostgreSQL in Docker, SQLite fallback for local development
- Cache: Redis in Docker, in-memory TTL fallback locally
- Deployment: Dockerfiles, Docker Compose, health endpoints
- Quality: Pytest, GitHub Actions

## Quick Start With Docker

```powershell
cd "C:\Users\bhuva\Documents\build-a-production-ready-full-stack"
Copy-Item backend\.env.example backend\.env
docker compose up --build
```

Open:

- Frontend: http://localhost:5173
- Backend API: http://localhost:5000
- Health: http://localhost:5000/health
- Readiness: http://localhost:5000/ready

## Local Development

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

## Tests

Backend:

```powershell
cd backend
pytest -q
```

Frontend build check:

```powershell
cd frontend
npm install
npm run build
```

## Environment

Backend configuration lives in `backend/.env`.

```ini
FLASK_ENV=development
SECRET_KEY=replace-this-secret
JWT_SECRET_KEY=replace-this-jwt-secret
DATABASE_URL=sqlite:///trustlens.db
REDIS_URL=
CORS_ORIGINS=http://localhost:5173
RATELIMIT_STORAGE_URI=memory://
SOCKETIO_ASYNC_MODE=eventlet
```

For Docker Compose, the backend receives PostgreSQL and Redis URLs from `docker-compose.yml`.

## Documentation

- [API](docs/API.md)
- [System Design](docs/SYSTEM_DESIGN.md)
- [Security](docs/SECURITY.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Resume and Interview Story](docs/RESUME_STORY.md)

## Production Checklist

- Replace default secrets and rotate them through a secret manager.
- Use managed PostgreSQL and Redis with backups enabled.
- Run behind TLS at a reverse proxy, load balancer, or platform edge.
- Restrict CORS origins to the deployed frontend domain.
- Add structured logs, request tracing, and metrics dashboards.
- Add a queue for asynchronous enrichment if detector latency grows.
- Add model evaluation data before calling the detector machine learning.
