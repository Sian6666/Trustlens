from app.services.detector import analyze_content, calibrated_confidence


def test_high_risk_otp_link_message():
    result = analyze_content("Urgent: your bank OTP is 123456. Verify your account at http://bit.ly/x")

    assert result["risk_score"] >= 70
    assert result["risk_level"] == "high"
    assert "otp" in result["suspicious_phrases"]
    assert result["detector_reasons"][0]["weight"] >= 20


def test_low_risk_plain_message():
    result = analyze_content("Hi, the team meeting is at 4 PM today.")

    assert result["risk_score"] < 40
    assert result["risk_level"] == "low"


def test_untrusted_brand_like_url_increases_risk():
    result = analyze_content("Please update your account at http://secure-bank-verify-92.example/pay now")

    labels = {reason["label"] for reason in result["detector_reasons"]}
    assert "brand-like untrusted domain" in labels
    assert "non-HTTPS link" in labels
    assert result["risk_score"] >= 40


def test_confidence_is_bounded():
    assert 0.35 <= calibrated_confidence(0, 0) <= 0.98
    assert 0.35 <= calibrated_confidence(100, 10) <= 0.98
