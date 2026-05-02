# Resume and Interview Story

## One-Line Pitch

TrustLens is a real-time scam intelligence platform that lets users report suspicious messages, receive explainable risk scores, validate reports through community voting, and monitor live threat trends.

## Resume Bullet

Built TrustLens, a full-stack trust-and-safety platform using React, Flask, PostgreSQL, Redis, JWT auth, and Socket.IO; implemented explainable scam-risk scoring, authenticated reporting, community validation, cached dashboards, search, rate limiting, Docker deployment, health checks, tests, and CI.

## Interview Talking Points

- Product: chose scam and misinformation detection because it maps to real trust-and-safety problems at large platforms.
- Backend: designed REST endpoints for auth, submissions, voting, search, dashboard summaries, and health checks.
- Realtime: used Socket.IO to broadcast new reports and vote changes to connected dashboards.
- Data: modeled users, submissions, detector reasons, and votes with uniqueness constraints.
- Performance: cached dashboard summaries in Redis and invalidated them on writes.
- Security: added JWT-protected writes, password hashing, CORS control, rate limits, sanitization, and security headers.
- System design: documented scale-up path for queues, full-text search, Redis pub/sub, model evaluation, and abuse prevention.
- Quality: added pytest coverage for detector behavior, auth flow, submissions, voting, search, dashboard, and health endpoints.

## Honest Limitations To Say Out Loud

- The detector is explainable rules-based scoring, not a trained ML model.
- Search uses simple database filtering today; larger data volumes should move to PostgreSQL full-text search or a search service.
- JWT revocation and refresh-token rotation are not yet implemented.

Being honest about these limitations is a strength. It shows you understand production boundaries instead of overselling a demo.
