def test_health_and_ready(client):
    assert client.get("/health").status_code == 200
    assert client.get("/ready").status_code == 200


def test_signup_login_and_me(client):
    signup = client.post(
        "/api/auth/signup",
        json={"name": "Grace", "email": "grace@example.com", "password": "strong-password"},
    )
    assert signup.status_code == 201

    login = client.post(
        "/api/auth/login",
        json={"email": "grace@example.com", "password": "strong-password"},
    )
    assert login.status_code == 200
    token = login.get_json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.get_json()["user"]["email"] == "grace@example.com"


def test_submission_search_vote_and_dashboard(client, auth_headers):
    created = client.post(
        "/api/submissions",
        headers=auth_headers,
        json={
            "content": "Urgent OTP 123456. Verify account at http://bit.ly/fake now!",
            "source": "sms",
            "category": "bank",
        },
    )
    assert created.status_code == 201
    submission = created.get_json()["submission"]
    assert submission["risk_level"] == "high"

    search = client.get("/api/submissions/search?q=otp", headers=auth_headers)
    assert search.status_code == 200
    assert search.get_json()["total"] == 1

    vote = client.post(
        f"/api/submissions/{submission['id']}/votes",
        headers=auth_headers,
        json={"vote_type": "scam"},
    )
    assert vote.status_code == 201
    assert vote.get_json()["submission"]["scam_votes"] == 1

    trending = client.get("/api/dashboard/trending?category=bank")
    assert trending.status_code == 200
    assert len(trending.get_json()["items"]) == 1
