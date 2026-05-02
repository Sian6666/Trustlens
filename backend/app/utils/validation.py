import re
from html import escape

from email_validator import EmailNotValidError, validate_email
from flask import abort

ALLOWED_CATEGORIES = {"general", "bank", "job", "otp", "crypto", "delivery", "tax", "health"}
ALLOWED_SOURCES = {"email", "sms", "whatsapp", "message", "social"}
ALLOWED_VOTES = {"scam", "safe", "upvote", "downvote"}


def sanitize_text(value, max_length=5000):
    if not isinstance(value, str):
        abort(400, "Expected text input")
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", value).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned:
        abort(400, "Content cannot be empty")
    if len(cleaned) > max_length:
        abort(400, f"Content exceeds {max_length} characters")
    return escape(cleaned, quote=False)


def normalize_for_search(value):
    return re.sub(r"\s+", " ", value.lower()).strip()


def parse_category(value):
    category = (value or "general").lower().strip()
    return category if category in ALLOWED_CATEGORIES else "general"


def parse_source(value):
    source = (value or "message").lower().strip()
    return source if source in ALLOWED_SOURCES else "message"


def validate_email_address(email):
    try:
        return validate_email(email, check_deliverability=False).normalized.lower()
    except EmailNotValidError:
        abort(400, "Invalid email address")


def validate_password(password):
    if not isinstance(password, str) or len(password) < 8:
        abort(400, "Password must be at least 8 characters")
    return password
