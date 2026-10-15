"""Payloads shaped like real WooCommerce REST API v3 responses (trimmed)."""
import datetime as _dt

_now = _dt.datetime.now(_dt.timezone.utc).replace(tzinfo=None)
RECENT = (_now - _dt.timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
OLDER = (_now - _dt.timedelta(days=40)).strftime("%Y-%m-%dT%H:%M:%S")

PRODUCTS = [
    {"id": 11, "name": "Beans 1kg", "sku": "B1", "price": "30.00", "status": "publish", "stock_status": "instock",
     "stock_quantity": 10, "images": [{"src": "https://x.test/b.jpg"}], "categories": [{"name": "Coffee"}]},
]
CUSTOMERS = [
    {"id": 5, "email": "Maya@Example.com", "first_name": "Maya", "last_name": "Nair", "date_created_gmt": OLDER,
     "billing": {"phone": "123", "city": "Panaji", "country": "IN", "address_1": "1 Beach Rd"}},
]


def order(woo_id, customer_id, email, status="completed", total="60.00", created=RECENT, first="Maya", last="Nair"):
    return {
        "id": woo_id, "number": str(woo_id), "status": status, "currency": "USD", "total": total, "total_tax": "0",
        "shipping_total": "0", "discount_total": "0", "payment_method": "stripe", "payment_method_title": "Card",
        "date_created_gmt": created, "date_paid_gmt": created if status == "completed" else None,
        "date_completed_gmt": created if status == "completed" else None, "customer_id": customer_id,
        "billing": {"first_name": first, "last_name": last, "email": email, "city": "Panaji"},
        "shipping": {}, "customer_note": "",
        "line_items": [{"product_id": 11, "name": "Beans 1kg", "sku": "B1", "quantity": 2, "price": 30, "total": total}],
    }


ORDERS = [
    order(101, 5, "maya@example.com", "completed", "60.00"),
    order(102, 5, "maya@example.com", "pending", "30.00"),
    order(103, 0, "guest@example.com", "processing", "90.00", first="Guest", last="Buyer"),  # guest checkout
]


class FakeWooClient:
    """Stands in for WooClient: same `pages()` interface, no network."""

    def __init__(self, data=None):
        self.data = data or {"products": PRODUCTS, "customers": CUSTOMERS, "orders": ORDERS}

    def pages(self, path, params=None, per_page=100):
        yield self.data[path]
