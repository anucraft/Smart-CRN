from datetime import datetime, timezone


def utcnow() -> datetime:
    """Naive UTC 'now'. We store every timestamp as naive UTC for simplicity."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def parse_woo_datetime(value):
    """WooCommerce returns ISO strings like '2024-05-01T10:30:00' (we use the *_gmt fields)."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "")).replace(tzinfo=None)
    except ValueError:
        return None


def iso(dt):
    return dt.isoformat() if dt else None
