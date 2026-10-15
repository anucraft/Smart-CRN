import pytest

from app.services.woo_client import WooClient, WooCommerceError


class FakeResponse:
    def __init__(self, status=200, body=None, total_pages=1):
        self.status_code, self._body = status, body if body is not None else []
        self.headers = {"X-WP-TotalPages": str(total_pages)}
        self.ok = status < 400

    def json(self):
        return self._body


def make_client(responses, url="https://shop.test"):
    client = WooClient(url, "ck", "cs")
    calls = []

    def fake_get(endpoint, params=None, timeout=None):
        calls.append((endpoint, params))
        return responses.pop(0)

    client.session.get = fake_get
    return client, calls


def test_pagination_follows_total_pages_header():
    client, calls = make_client([FakeResponse(body=[{"id": 1}], total_pages=2), FakeResponse(body=[{"id": 2}], total_pages=2)])
    pages = list(client.pages("orders"))
    assert [p[0]["id"] for p in pages] == [1, 2]
    assert [c[1]["page"] for c in calls] == [1, 2]
    assert calls[0][0] == "https://shop.test/wp-json/wc/v3/orders"


@pytest.mark.parametrize("status,fragment", [(401, "rejected"), (404, "not found"), (500, "HTTP 500")])
def test_http_errors_become_readable_messages(status, fragment):
    client, _ = make_client([FakeResponse(status=status)])
    with pytest.raises(WooCommerceError, match=fragment):
        client.test_connection()


def test_https_uses_basic_auth_and_http_uses_query_keys():
    https_client = WooClient("https://shop.test", "ck", "cs")
    assert https_client.session.auth == ("ck", "cs")
    http_client, calls = make_client([FakeResponse()], url="http://localhost:8080")
    http_client.test_connection()
    assert calls[0][1]["consumer_key"] == "ck" and http_client.session.auth is None
