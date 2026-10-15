"""WooCommerce webhook verification and dispatch."""
import base64
import hashlib
import hmac

from ..extensions import db
from . import woo_sync_service as sync

HANDLERS = {
    "customer.created": sync.upsert_customer,
    "customer.updated": sync.upsert_customer,
    "order.created": sync.upsert_order,
    "order.updated": sync.upsert_order,
    "product.created": sync.upsert_product,
    "product.updated": sync.upsert_product,
}


def verify_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    """WooCommerce signs the raw body: base64(HMAC-SHA256(body, secret))."""
    if not secret or not signature:
        return False
    digest = hmac.new(secret.encode(), raw_body, hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode()
    return hmac.compare_digest(expected, signature)


def handle_event(topic: str, payload: dict) -> str:
    handler = HANDLERS.get(topic)
    if handler is None:
        return "ignored"  # e.g. *.deleted: we keep history on purpose
    handler(payload)
    db.session.commit()
    return "processed"
