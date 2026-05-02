import math
import re
from urllib.parse import urlparse

KEYWORD_RULES = {
    "urgent": (12, "pressure"),
    "verify your account": (24, "credential theft"),
    "password": (12, "credential theft"),
    "otp": (24, "credential theft"),
    "one time password": (24, "credential theft"),
    "kyc": (18, "identity verification"),
    "blocked": (16, "account lockout"),
    "suspended": (16, "account lockout"),
    "claim now": (18, "reward bait"),
    "limited time": (12, "pressure"),
    "gift card": (20, "payment diversion"),
    "crypto": (15, "investment fraud"),
    "investment": (12, "investment fraud"),
    "work from home": (12, "job fraud"),
    "processing fee": (18, "advance fee"),
    "refund": (8, "refund lure"),
    "lottery": (20, "reward bait"),
    "winner": (14, "reward bait"),
    "double your money": (24, "unrealistic return"),
    "risk free": (16, "unrealistic return"),
    "act now": (12, "pressure"),
    "click here": (8, "link lure"),
}

PATTERN_RULES = [
    (re.compile(r"https?://(?:bit\.ly|tinyurl\.com|t\.co|goo\.gl|cutt\.ly|is\.gd|buff\.ly)/\S+", re.I), 24, "shortened link", "link obfuscation"),
    (re.compile(r"\b\d{4,8}\b.*\b(otp|code|pin)\b|\b(otp|code|pin)\b.*\b\d{4,8}\b", re.I), 26, "credential or OTP request", "credential theft"),
    (re.compile(r"\b(?:wire|transfer|upi|bank)\b.*\b(?:now|immediately|urgent)\b", re.I), 22, "urgent payment language", "payment diversion"),
    (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), 4, "email address present", "contact artifact"),
    (re.compile(r"\b(?:password|login|account)\b.*\b(?:verify|confirm|update)\b", re.I), 24, "account verification pressure", "credential theft"),
    (re.compile(r"\b(?:guaranteed|risk free|double your money|100% profit)\b", re.I), 22, "unrealistic financial promise", "investment fraud"),
    (re.compile(r"\b(?:remote job|part time|salary|recruiter)\b.*\b(?:fee|deposit|registration)\b", re.I), 22, "job fee request", "job fraud"),
    (re.compile(r"\b(?:customs|parcel|delivery)\b.*\b(?:fee|pay|blocked|failed)\b", re.I), 18, "delivery payment pressure", "delivery fraud"),
]

TRUSTED_DOMAINS = {
    "amazon.com",
    "apple.com",
    "google.com",
    "microsoft.com",
    "paypal.com",
}

URL_PATTERN = re.compile(r"https?://[^\s<>()]+", re.I)


def analyze_content(content):
    text = content.lower()
    score = 0
    phrases = []
    reasons = []
    categories = {}

    for phrase, (weight, category) in KEYWORD_RULES.items():
        if phrase in text:
            score += weight
            phrases.append(phrase)
            add_reason(reasons, categories, "keyword", phrase, weight, category)

    for pattern, weight, label, category in PATTERN_RULES:
        if pattern.search(content):
            score += weight
            phrases.append(label)
            add_reason(reasons, categories, "pattern", label, weight, category)

    url_findings = analyze_urls(content)
    for finding in url_findings:
        score += finding["weight"]
        phrases.append(finding["label"])
        add_reason(reasons, categories, "url", finding["label"], finding["weight"], finding["category"])

    if len(content) < 40 and any(term in text for term in ("otp", "link", "urgent", "pay")):
        score += 10
        add_reason(reasons, categories, "heuristic", "short high-pressure message", 10, "pressure")

    if count_exclamation_pressure(content) >= 2:
        score += 6
        add_reason(reasons, categories, "heuristic", "repeated urgency punctuation", 6, "pressure")

    score = min(100, score)
    return {
        "risk_score": score,
        "risk_level": risk_level(score),
        "suspicious_phrases": sorted(set(phrases)),
        "detector_reasons": sorted(reasons, key=lambda item: item["weight"], reverse=True),
    }


def add_reason(reasons, categories, reason_type, label, weight, category):
    categories[category] = categories.get(category, 0) + weight
    reasons.append(
        {
            "type": reason_type,
            "label": label,
            "weight": weight,
            "category": category,
            "explanation": explain_reason(reason_type, label, category),
        }
    )


def analyze_urls(content):
    findings = []
    for raw_url in URL_PATTERN.findall(content):
        parsed = urlparse(raw_url)
        host = parsed.netloc.lower().split(":")[0]
        if not host:
            continue
        if host.count("-") >= 2 or any(char.isdigit() for char in host.split(".")[0]):
            findings.append({"label": "suspicious domain shape", "weight": 8, "category": "link obfuscation"})
        if not is_trusted_domain(host) and any(brand in host for brand in ("bank", "pay", "secure", "verify")):
            findings.append({"label": "brand-like untrusted domain", "weight": 16, "category": "impersonation"})
        if parsed.scheme != "https":
            findings.append({"label": "non-HTTPS link", "weight": 8, "category": "link safety"})
    return findings


def is_trusted_domain(host):
    return any(host == domain or host.endswith(f".{domain}") for domain in TRUSTED_DOMAINS)


def count_exclamation_pressure(content):
    return len(re.findall(r"!|now|immediately|urgent", content, re.I))


def explain_reason(reason_type, label, category):
    return f"{label} increased risk because it is commonly associated with {category}."


def risk_level(score):
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def calibrated_confidence(score, reason_count):
    signal = score / 100 + math.log1p(reason_count) / 5
    return round(min(0.98, max(0.35, signal)), 2)
