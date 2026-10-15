from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ..services import settings_service as svc
from ..utils.responses import error

bp = Blueprint("settings", __name__, url_prefix="/api/settings")


def _public_view():
    cfg = svc.get_woo_config()
    return {
        "store_url": cfg["store_url"],
        "consumer_key": svc.mask(cfg["consumer_key"]),
        "has_consumer_secret": bool(cfg["consumer_secret"]),
        "has_webhook_secret": bool(cfg["webhook_secret"]),
        "webhook_url": request.url_root.rstrip("/") + "/api/woocommerce/webhook",
        "configured": svc.woo_is_configured(),
    }


@bp.get("")
@jwt_required()
def get_settings():
    return jsonify(_public_view())


@bp.put("")
@jwt_required()
def update_settings():
    data = request.get_json(silent=True) or {}
    store_url = (data.get("store_url") or "").strip()
    if store_url and not store_url.startswith(("http://", "https://")):
        return error("Store URL must start with http:// or https://", 400)
    if store_url:
        svc.set_setting("woo_store_url", store_url.rstrip("/"))
    # Secrets: empty/missing means "keep the current value".
    for field in ("consumer_key", "consumer_secret", "webhook_secret"):
        value = (data.get(field) or "").strip()
        if value:
            svc.set_setting(f"woo_{field}", value)
    return jsonify(_public_view())
