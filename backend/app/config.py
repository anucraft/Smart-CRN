"""Central configuration. All secrets come from environment variables."""
import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB = "sqlite:///" + os.path.join(BASE_DIR, "smartcrm.db")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me-please-32chars")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key-change-me-32chars!")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_EXPIRES_HOURS", "12")))

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or DEFAULT_DB
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLite allows one writer at a time; wait up to 30s instead of failing
    # immediately with "database is locked" when a webhook and a sync overlap.
    SQLALCHEMY_ENGINE_OPTIONS = (
        {"connect_args": {"timeout": 30}} if SQLALCHEMY_DATABASE_URI.startswith("sqlite") else {}
    )

    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
    VIP_THRESHOLD = float(os.getenv("VIP_THRESHOLD", "500"))

    # Optional env fallbacks for WooCommerce (Settings page values win)
    WC_STORE_URL = os.getenv("WC_STORE_URL", "")
    WC_CONSUMER_KEY = os.getenv("WC_CONSUMER_KEY", "")
    WC_CONSUMER_SECRET = os.getenv("WC_CONSUMER_SECRET", "")
    WC_WEBHOOK_SECRET = os.getenv("WC_WEBHOOK_SECRET", "")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    WC_STORE_URL = ""
    WC_CONSUMER_KEY = ""
    WC_CONSUMER_SECRET = ""
    WC_WEBHOOK_SECRET = ""
