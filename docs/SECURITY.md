# Security Notes

## Implemented Controls

- Passwords are stored with Werkzeug password hashing.
- JWT authentication protects submissions, voting, search, and user profile endpoints.
- Flask-Limiter rate limits authentication and write-heavy endpoints.
- Inputs are sanitized, normalized, and length-limited before persistence.
- CORS is restricted by environment configuration.
- Security headers include `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, and `Permissions-Policy`.
- Community votes use a uniqueness constraint to reduce manipulation.
- Health and readiness endpoints separate liveness from dependency readiness.

## Threat Model

Primary risks:

- Credential stuffing against login.
- Spam submissions intended to poison trending data.
- Duplicate voting or coordinated voting abuse.
- Malicious links or HTML in user-submitted content.
- Secret leakage through committed `.env` files.

Mitigations:

- Rate limits reduce brute force and write abuse.
- Escaped text and React rendering reduce script injection risk.
- Vote uniqueness prevents simple repeated votes by one account.
- `.env`, databases, node modules, and build artifacts are ignored.
- Production deployments should use managed secrets and HTTPS only.

## Recommended Production Additions

- Refresh tokens and explicit token revocation.
- Email verification for account creation.
- Abuse heuristics for account age, IP reputation, and voting velocity.
- Structured audit logs for auth, submissions, and votes.
- Web application firewall or platform-level bot controls.
- A privacy review before storing real user-submitted messages.
