import base64
import hashlib
import hmac
import json

from app.models import Activity, Order
from app.services import settings_service
from tests.fixtures import order

SECRET = "whsec_test"


def sign(body: bytes, secret=SECRET):
    return base64.b64encode(hmac.new(secret.encode(), body, hashlib.sha256).digest()).decode()


def post(client, payload, topic="order.created", secret=SECRET):
    body = json.dumps(payload).encode()
    return client.post("/api/woocommerce/webhook", data=body, content_type="application/json",
                       headers={"X-WC-Webhook-Signature": sign(body, secret), "X-WC-Webhook-Topic": topic})


def test_rejects_when_secret_missing(client):
    assert client.post("/api/woocommerce/webhook", json={"id": 1}).status_code == 503


def test_rejects_bad_signature(client):
    settings_service.set_setting("woo_webhook_secret", SECRET)
    assert post(client, order(1, 0, "a@b.test"), secret="wrong").status_code == 401


def test_order_created_webhook(client):
    settings_service.set_setting("woo_webhook_secret", SECRET)
    resp = post(client, order(201, 0, "new@shop.test", "processing", "45.00"))
    assert resp.status_code == 200 and resp.get_json()["status"] == "processed"
    assert Order.query.filter_by(woo_id=201).one().customer.email == "new@shop.test"


def test_order_updated_logs_status_change(client):
    settings_service.set_setting("woo_webhook_secret", SECRET)
    post(client, order(202, 0, "u@shop.test", "pending"))
    post(client, order(202, 0, "u@shop.test", "completed"), topic="order.updated")
    assert Order.query.filter_by(woo_id=202).one().status == "completed"
    assert Activity.query.filter_by(type="order.status_changed").count() == 1


def test_duplicate_delivery_is_harmless(client):
    settings_service.set_setting("woo_webhook_secret", SECRET)
    post(client, order(203, 0, "d@shop.test"))
    post(client, order(203, 0, "d@shop.test"))
    assert Order.query.filter_by(woo_id=203).count() == 1


def test_unknown_topic_ignored(client):
    settings_service.set_setting("woo_webhook_secret", SECRET)
    assert post(client, {"id": 9}, topic="order.deleted").get_json()["status"] == "ignored"


def test_form_encoded_ping(client):
    settings_service.set_setting("woo_webhook_secret", SECRET)
    body = b"webhook_id=3"
    resp = client.post("/api/woocommerce/webhook", data=body, content_type="application/x-www-form-urlencoded",
                       headers={"X-WC-Webhook-Signature": sign(body)})
    assert resp.status_code == 200 and resp.get_json()["status"] == "pong"
