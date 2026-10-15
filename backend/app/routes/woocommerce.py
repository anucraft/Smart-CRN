import json

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from ..models import Customer, Order, Product
from ..services import settings_service, webhook_service, woo_sync_service
from ..services.woo_client import WooCommerceError, client_from_config
from ..utils.responses import error

bp = Blueprint("woocommerce", __name__, url_prefix="/api/woocommerce")


@bp.get("/status")
@jwt_required()
def status():
    return jsonify({
        "configured": settings_service.woo_is_configured(),
        "last_sync": settings_service.get_last_sync(),
        "counts": {
            "customers": Customer.query.count(),
            "orders": Order.query.count(),
            "products": Product.query.count(),
        },
    })


@bp.post("/test-connection")
@jwt_required()
def test_connection():
    try:
        client_from_config(settings_service.get_woo_config()).test_connection()
    except WooCommerceError as exc:
        return error(str(exc), 400)
    return jsonify({"ok": True, "message": "Connected to WooCommerce."})


@bp.post("/sync/<resource>")
@jwt_required()
def sync(resource):
    """resource = customers | orders | products | all"""
    if resource != "all" and resource not in woo_sync_service.RESOURCES:
        return error("Unknown resource. Use customers, orders, products or all.", 404)
    try:
        client = client_from_config(settings_service.get_woo_config())
        summary = woo_sync_service.sync(client, None if resource == "all" else [resource])
    except WooCommerceError as exc:
        return error(str(exc), 400)
    return jsonify(summary)


@bp.post("/webhook")
def webhook():
    """PUBLIC endpoint (WooCommerce cannot send a JWT); protected by the HMAC signature."""
    secret = settings_service.get_woo_config()["webhook_secret"]
    if not secret:
        return error("Webhook secret is not configured.", 503)
    raw = request.get_data()  # must be the exact bytes WooCommerce signed
    if not webhook_service.verify_signature(raw, request.headers.get("X-WC-Webhook-Signature", ""), secret):
        return error("Invalid signature.", 401)

    try:
        payload = json.loads(raw)
    except ValueError:
        return jsonify({"status": "pong"})  # WooCommerce's form-encoded ping when a webhook is saved
    if not isinstance(payload, dict) or "id" not in payload:
        return jsonify({"status": "ignored"})

    topic = request.headers.get("X-WC-Webhook-Topic", "")
    try:
        result = webhook_service.handle_event(topic, payload)
    except Exception:  # return 500 so WooCommerce retries; log for debugging
        current_app.logger.exception("Webhook processing failed for topic %s", topic)
        from ..extensions import db
        db.session.rollback()
        return error("Processing failed.", 500)
    return jsonify({"status": result, "topic": topic})
