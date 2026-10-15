def test_login_success(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["admin"]["email"] == "owner@shop.test"


def test_login_wrong_password(client, auth_headers):
    resp = client.post("/api/auth/login", json={"email": "owner@shop.test", "password": "nope"})
    assert resp.status_code == 401


def test_login_requires_fields(client):
    assert client.post("/api/auth/login", json={}).status_code == 400


def test_protected_routes_need_token(client):
    for url in ("/api/customers", "/api/orders", "/api/analytics/summary", "/api/settings"):
        assert client.get(url).status_code == 401


def test_health_is_public(client):
    assert client.get("/api/health").get_json() == {"status": "ok"}
