"""Thin wrapper around the WooCommerce REST API (v3).

Only this file knows about HTTP details, so the rest of the app can be tested with
a fake client."""
import requests


class WooCommerceError(Exception):
    """Raised for any problem talking to the store (bad URL, bad keys, timeouts...)."""


class WooClient:
    def __init__(self, store_url: str, consumer_key: str, consumer_secret: str, timeout: int = 30):
        self.base_url = store_url.rstrip("/") + "/wp-json/wc/v3"
        self.timeout = timeout
        self.session = requests.Session()
        self._query_auth = {}
        if self.base_url.startswith("https://"):
            # Over HTTPS, WooCommerce accepts HTTP Basic auth with key/secret.
            self.session.auth = (consumer_key, consumer_secret)
        else:
            # Plain HTTP (local dev): WooCommerce only accepts keys in the query string.
            self._query_auth = {"consumer_key": consumer_key, "consumer_secret": consumer_secret}

    def _get(self, path, params=None):
        params = {**(params or {}), **self._query_auth}
        try:
            resp = self.session.get(f"{self.base_url}/{path}", params=params, timeout=self.timeout)
        except requests.RequestException as exc:
            raise WooCommerceError(f"Could not reach the store: {exc}") from exc
        if resp.status_code in (401, 403):
            raise WooCommerceError("WooCommerce rejected the API keys. Check the key, secret and permissions (Read/Write).")
        if resp.status_code == 404:
            raise WooCommerceError("WooCommerce REST API not found. Check the store URL and that permalinks are enabled.")
        if not resp.ok:
            raise WooCommerceError(f"WooCommerce returned HTTP {resp.status_code}.")
        return resp

    def test_connection(self) -> bool:
        self._get("products", {"per_page": 1})
        return True

    def pages(self, path, params=None, per_page=100):
        """Yield one list of records per page until WooCommerce runs out."""
        page = 1
        while True:
            resp = self._get(path, {**(params or {}), "per_page": per_page, "page": page})
            try:
                batch = resp.json()
            except ValueError as exc:
                raise WooCommerceError("WooCommerce returned a response that is not JSON.") from exc
            if not batch:
                return
            yield batch
            total_pages = int(resp.headers.get("X-WP-TotalPages", page))
            if page >= total_pages:
                return
            page += 1


def client_from_config(cfg: dict) -> WooClient:
    if not (cfg["store_url"] and cfg["consumer_key"] and cfg["consumer_secret"]):
        raise WooCommerceError("WooCommerce is not configured. Add your store URL and API keys in Settings.")
    return WooClient(cfg["store_url"], cfg["consumer_key"], cfg["consumer_secret"])
