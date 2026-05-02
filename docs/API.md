# TrustLens API

Base URL: `/api`

All protected endpoints require:

```http
Authorization: Bearer <jwt>
```

## Auth

### POST `/auth/signup`

Create a user.

```json
{
  "name": "Ada",
  "email": "ada@example.com",
  "password": "strong-password"
}
```

### POST `/auth/login`

Authenticate a user.

```json
{
  "email": "ada@example.com",
  "password": "strong-password"
}
```

Returns:

```json
{
  "access_token": "...",
  "user": {
    "id": 1,
    "name": "Ada",
    "email": "ada@example.com"
  }
}
```

### GET `/auth/me`

Returns the current authenticated user.

## Submissions

### POST `/submissions`

Analyze and store pasted content.

```json
{
  "content": "Your bank OTP expires now. Click http://bit.ly/example",
  "source": "sms",
  "category": "bank"
}
```

### GET `/submissions`

Query params:

- `page`: default `1`
- `per_page`: default `10`, max `50`
- `category`: optional
- `min_risk`: optional integer `0-100`

### GET `/submissions/:id`

Returns one submission.

### GET `/submissions/search?q=...`

Fast lookup for existing submissions. Supports pagination with `page` and `per_page`.

## Community

### POST `/submissions/:id/votes`

```json
{
  "vote_type": "scam"
}
```

Allowed values:

- `scam`
- `safe`
- `upvote`
- `downvote`

## Dashboard

### GET `/dashboard/trending?category=bank`

Returns most reported scams.

### GET `/dashboard/risk-trends`

Returns average risk score by day.

## Realtime

Socket.IO namespace: `/`

Events emitted by server:

- `submission:new`: emitted when content is submitted and analyzed
- `vote:new`: emitted when a community vote is recorded

## Operations

### GET `/health`

Liveness check for the API process.

```json
{
  "status": "ok",
  "service": "trustlens-api"
}
```

### GET `/ready`

Readiness check for database and cache dependencies.

```json
{
  "status": "ok",
  "checks": {
    "database": "ok",
    "cache": "ok"
  }
}
```
