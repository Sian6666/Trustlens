# Deployment Guide

## Local Docker Deployment

```powershell
cd "C:\Users\bhuva\Documents\build-a-production-ready-full-stack"
Copy-Item backend\.env.example backend\.env
docker compose up --build
```

## Production Shape

Recommended production topology:

- Static frontend hosted on Vercel, Netlify, Cloudflare Pages, or an object-storage CDN.
- Flask API hosted on Render, Fly.io, Railway, ECS, Cloud Run, or another container platform.
- Managed PostgreSQL for durable data.
- Managed Redis for cache and future Socket.IO pub/sub.
- TLS terminated by the platform edge or reverse proxy.

## Required Environment Variables

Backend:

```ini
FLASK_ENV=production
SECRET_KEY=<strong-random-secret>
JWT_SECRET_KEY=<strong-random-jwt-secret>
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:5432/<db>
REDIS_URL=redis://<host>:6379/0
CORS_ORIGINS=https://<frontend-domain>
RATELIMIT_STORAGE_URI=redis://<host>:6379/1
SOCKETIO_ASYNC_MODE=eventlet
```

Frontend:

```ini
VITE_API_URL=https://<api-domain>/api
VITE_SOCKET_URL=https://<api-domain>
```

## Release Checklist

1. Run backend tests: `pytest -q`.
2. Run frontend build: `npm run build`.
3. Confirm `/health` returns `200`.
4. Confirm `/ready` returns `200` after database and cache are connected.
5. Verify signup, login, submit, search, vote, and realtime feed in the deployed app.
6. Rotate any secrets used during testing.
