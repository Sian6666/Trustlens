import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_HOURS", "8")))
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///trustlens.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ]
    REDIS_URL = os.getenv("REDIS_URL", "")
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    DEBUG = os.getenv("FLASK_ENV") == "development"
    SOCKETIO_ASYNC_MODE = os.getenv("SOCKETIO_ASYNC_MODE", "eventlet")


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-app-secret-with-at-least-32-bytes"
    JWT_SECRET_KEY = "test-jwt-secret-with-at-least-32-bytes"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    RATELIMIT_ENABLED = False
    SOCKETIO_ASYNC_MODE = "threading"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
