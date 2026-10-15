import pytest

from app.services import woo_sync_service
from tests.fixtures import FakeWooClient


@pytest.fixture()
def synced(app):
    woo_sync_service.sync(FakeWooClient())


def test_list_and_search_customers(client, auth_headers, synced):
    data = client.get("/api/customers", headers=auth_headers).get_json()
    assert data["total"] == 2
    found = client.get("/api/customers?q=maya", headers=auth_headers).get_json()
    assert found["total"] == 1 and found["items"][0]["orders_count"] == 2
    assert found["items"][0]["total_spent"] == 60.0  # pending order excluded from spend


def test_segment_filter(client, auth_headers, synced):
    prospects = client.get("/api/customers?segment=prospect", headers=auth_headers).get_json()
    assert prospects["total"] == 0
    returning = client.get("/api/customers?segment=returning", headers=auth_headers).get_json()
    assert returning["total"] == 1


def test_customer_detail_notes_timeline(client, auth_headers, synced):
    cid = client.get("/api/customers?q=maya", headers=auth_headers).get_json()["items"][0]["id"]
    detail = client.get(f"/api/customers/{cid}", headers=auth_headers).get_json()
    assert len(detail["recent_orders"]) == 2

    assert client.post(f"/api/customers/{cid}/notes", json={"body": "  "}, headers=auth_headers).status_code == 400
    created = client.post(f"/api/customers/{cid}/notes", json={"body": "Prefers email"}, headers=auth_headers)
    assert created.status_code == 201 and created.get_json()["author"] == "Owner"

    notes = client.get(f"/api/customers/{cid}/notes", headers=auth_headers).get_json()["items"]
    assert [n["body"] for n in notes] == ["Prefers email"]
    types = {a["type"] for a in client.get(f"/api/customers/{cid}/timeline", headers=auth_headers).get_json()["items"]}
    assert {"customer.created", "order.created", "note.added"} <= types

    nid = notes[0]["id"]
    assert client.delete(f"/api/customers/{cid}/notes/{nid}", headers=auth_headers).status_code == 204


def test_customer_404(client, auth_headers):
    assert client.get("/api/customers/999", headers=auth_headers).status_code == 404


def test_orders_list_search_detail(client, auth_headers, synced):
    all_orders = client.get("/api/orders", headers=auth_headers).get_json()
    assert all_orders["total"] == 3
    assert client.get("/api/orders?status=pending", headers=auth_headers).get_json()["total"] == 1
    assert client.get("/api/orders?q=guest@example.com", headers=auth_headers).get_json()["total"] == 1
    oid = client.get("/api/orders?q=101", headers=auth_headers).get_json()["items"][0]["id"]
    detail = client.get(f"/api/orders/{oid}", headers=auth_headers).get_json()
    assert detail["items"][0]["quantity"] == 2 and detail["payment_status"] == "paid"


def test_summary_and_charts(client, auth_headers, synced):
    s = client.get("/api/analytics/summary", headers=auth_headers).get_json()
    assert s["total_customers"] == 2 and s["total_orders"] == 3
    assert s["revenue"] == 150.0          # completed 60 + processing 90
    assert s["pending_orders"] == 2       # pending + processing
    months = client.get("/api/analytics/monthly-sales", headers=auth_headers).get_json()["items"]
    assert len(months) == 12 and sum(m["orders"] for m in months) == 3
    growth = client.get("/api/analytics/customer-growth", headers=auth_headers).get_json()["items"]
    assert growth[-1]["total_customers"] == 2
    top = client.get("/api/analytics/top-customers", headers=auth_headers).get_json()["items"]
    assert top[0]["total_spent"] == 90.0 and top[0]["name"]  # guest with the 90 processing order


def test_settings_roundtrip_masks_secrets(client, auth_headers):
    resp = client.put("/api/settings", headers=auth_headers, json={
        "store_url": "https://shop.test/", "consumer_key": "ck_abcdef123456", "consumer_secret": "cs_secret",
        "webhook_secret": "whsec"})
    body = resp.get_json()
    assert body["store_url"] == "https://shop.test" and body["configured"] is True
    assert body["consumer_key"].startswith("ck_a") and "123456" not in body["consumer_key"]
    assert "cs_secret" not in str(body)
    # blank secret keeps the stored one
    again = client.put("/api/settings", headers=auth_headers, json={"consumer_secret": ""}).get_json()
    assert again["has_consumer_secret"] is True


def test_settings_rejects_bad_url(client, auth_headers):
    assert client.put("/api/settings", headers=auth_headers, json={"store_url": "shop.test"}).status_code == 400
