"""Read/write key-value settings, with environment variables as fallback."""
import json

from flask import current_app

from ..extensions import db
from ..models import Setting

WOO_KEYS = ("store_url", "consumer_key", "consumer_secret", "webhook_secret")
_ENV_FALLBACK = {
    "store_url": "WC_STORE_URL",
    "consumer_key": "WC_CONSUMER_KEY",
    "consumer_secret": "WC_CONSUMER_SECRET",
    "webhook_secret": "WC_WEBHOOK_SECRET",
}


def get_setting(key, default=""):
    row = db.session.get(Setting, key)
    return row.value if row and row.value is not None else default


def set_setting(key, value):
    row = db.session.get(Setting, key)
    if row is None:
        row = Setting(key=key)
        db.session.add(row)
    row.value = value
    db.session.commit()


def get_woo_config() -> dict:
    cfg = {}
    for key in WOO_KEYS:
        cfg[key] = get_setting(f"woo_{key}") or current_app.config.get(_ENV_FALLBACK[key], "")
    return cfg


def woo_is_configured() -> bool:
    cfg = get_woo_config()
    return bool(cfg["store_url"] and cfg["consumer_key"] and cfg["consumer_secret"])


def mask(value: str) -> str:
    if not value:
        return ""
    return value[:4] + "•" * 8 if len(value) > 4 else "•" * len(value)


def get_last_sync():
    raw = get_setting("last_sync")
    return json.loads(raw) if raw else None


def set_last_sync(summary: dict):
    set_setting("last_sync", json.dumps(summary))
