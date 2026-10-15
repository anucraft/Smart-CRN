from app.models import Customer, Order, Product
from app.services import woo_sync_service
from tests.fixtures import FakeWooClient


def test_full_sync_creates_everything(app):
    summary = woo_sync_service.sync(FakeWooClient())
    assert summary["results"]["products"]["created"] == 1
    assert summary["results"]["orders"]["created"] == 3
    assert Product.query.count() == 1
    assert Order.query.count() == 3
    # registered customer (Maya) + guest checkout customer
    assert Customer.query.count() == 2
    maya = Customer.query.filter_by(email="maya@example.com").one()  # e-mail normalised to lower-case
    assert maya.woo_id == 5 and maya.orders.count() == 2


def test_sync_is_idempotent(app):
    woo_sync_service.sync(FakeWooClient())
    second = woo_sync_service.sync(FakeWooClient())
    assert second["results"]["orders"]["created"] == 0
    assert second["results"]["orders"]["updated"] == 3
    assert Order.query.count() == 3 and Customer.query.count() == 2


def test_order_items_link_to_products(app):
    woo_sync_service.sync(FakeWooClient())
    order = Order.query.filter_by(woo_id=101).one()
    assert order.items[0].product.sku == "B1"


def test_derived_statuses(app):
    woo_sync_service.sync(FakeWooClient())
    done, pending = Order.query.filter_by(woo_id=101).one(), Order.query.filter_by(woo_id=102).one()
    assert (done.payment_status, done.shipping_status) == ("paid", "delivered")
    assert (pending.payment_status, pending.shipping_status) == ("pending", "awaiting_payment")


def test_sync_endpoint_requires_configuration(client, auth_headers):
    resp = client.post("/api/woocommerce/sync/all", headers=auth_headers)
    assert resp.status_code == 400
    assert "not configured" in resp.get_json()["error"].lower()


def test_sync_endpoint_unknown_resource(client, auth_headers):
    assert client.post("/api/woocommerce/sync/banana", headers=auth_headers).status_code == 404
