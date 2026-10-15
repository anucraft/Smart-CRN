"""Turns raw WooCommerce JSON into rows in our database.

Every upsert_* function is IDEMPOTENT: running it twice with the same payload
changes nothing. That is what makes both bulk sync and webhooks safe to retry."""
from decimal import Decimal, InvalidOperation

from ..extensions import db
from ..models import Customer, Order, OrderItem, Product
from ..utils.time import parse_woo_datetime, utcnow
from .activity_service import log_activity
from .settings_service import set_last_sync

RESOURCES = ("products", "customers", "orders")  # order matters: orders reference the others


def _money(value):
    try:
        return Decimal(str(value or 0))
    except InvalidOperation:
        return Decimal("0")


def _norm_email(email):
    email = (email or "").strip().lower()
    return email or None


# ----------------------------------------------------------------- products
def upsert_product(data: dict):
    product = Product.query.filter_by(woo_id=data["id"]).first()
    created = product is None
    if created:
        product = Product(woo_id=data["id"])
        db.session.add(product)
    images = data.get("images") or []
    product.name = data.get("name") or f"Product {data['id']}"
    product.sku = data.get("sku") or ""
    product.price = _money(data.get("price"))
    product.status = data.get("status") or "publish"
    product.stock_status = data.get("stock_status") or "instock"
    product.stock_quantity = data.get("stock_quantity")
    product.image_url = images[0].get("src", "") if images else ""
    product.categories = [c.get("name") for c in data.get("categories", []) if c.get("name")]
    return product, created


# ---------------------------------------------------------------- customers
def _apply_customer_fields(customer: Customer, data: dict):
    billing = data.get("billing") or {}
    customer.first_name = data.get("first_name") or billing.get("first_name") or customer.first_name or ""
    customer.last_name = data.get("last_name") or billing.get("last_name") or customer.last_name or ""
    customer.phone = billing.get("phone") or customer.phone or ""
    customer.address = billing.get("address_1") or customer.address or ""
    customer.city = billing.get("city") or customer.city or ""
    customer.state = billing.get("state") or customer.state or ""
    customer.country = billing.get("country") or customer.country or ""


def upsert_customer(data: dict):
    """Insert/update from a WooCommerce customer object (or an order's billing block
    wrapped as {'id': ..., 'email': ..., 'billing': {...}})."""
    woo_id = data.get("id") or None
    email = _norm_email(data.get("email") or (data.get("billing") or {}).get("email"))

    customer = Customer.query.filter_by(woo_id=woo_id).first() if woo_id else None
    if customer is None and email:
        customer = Customer.query.filter_by(email=email).first()  # e.g. earlier guest checkout

    created = customer is None
    if created:
        customer = Customer(created_at=parse_woo_datetime(data.get("date_created_gmt")) or utcnow())
        db.session.add(customer)
    if woo_id and not customer.woo_id:
        customer.woo_id = woo_id
    if email:
        customer.email = email
    _apply_customer_fields(customer, data)
    db.session.flush()
    if created:
        log_activity("customer.created", f"{customer.full_name} joined", customer.id, created_at=customer.created_at)
    return customer, created


# ------------------------------------------------------------------- orders
def _resolve_customer(data: dict):
    billing = data.get("billing") or {}
    woo_customer_id = data.get("customer_id") or 0
    if woo_customer_id:
        customer = Customer.query.filter_by(woo_id=woo_customer_id).first()
        if customer:
            return customer
        # Webhook for the order can arrive before the customer is synced.
        customer, _ = upsert_customer({"id": woo_customer_id, "billing": billing})
        return customer
    if _norm_email(billing.get("email")):  # guest checkout
        customer, _ = upsert_customer({"id": None, "billing": billing})
        return customer
    return None


def upsert_order(data: dict):
    order = Order.query.filter_by(woo_id=data["id"]).first()
    created = order is None
    old_status = None if created else order.status
    if created:
        order = Order(woo_id=data["id"])
        db.session.add(order)

    order.number = str(data.get("number") or data["id"])
    order.status = data.get("status") or "pending"
    order.currency = data.get("currency") or "USD"
    order.total = _money(data.get("total"))
    order.total_tax = _money(data.get("total_tax"))
    order.shipping_total = _money(data.get("shipping_total"))
    order.discount_total = _money(data.get("discount_total"))
    order.payment_method = data.get("payment_method") or ""
    order.payment_method_title = data.get("payment_method_title") or ""
    order.date_created = parse_woo_datetime(data.get("date_created_gmt")) or order.date_created or utcnow()
    order.date_paid = parse_woo_datetime(data.get("date_paid_gmt"))
    order.date_completed = parse_woo_datetime(data.get("date_completed_gmt"))
    order.billing = data.get("billing") or {}
    order.shipping = data.get("shipping") or {}
    order.customer_note = data.get("customer_note") or ""
    order.customer = _resolve_customer(data)

    # Replace line items wholesale: simplest way to stay in sync with edits.
    order.items.clear()
    for line in data.get("line_items", []):
        product = Product.query.filter_by(woo_id=line.get("product_id")).first() if line.get("product_id") else None
        order.items.append(OrderItem(
            product=product, woo_product_id=line.get("product_id"), name=line.get("name") or "Item",
            sku=line.get("sku") or "", quantity=line.get("quantity") or 1,
            price=_money(line.get("price")), total=_money(line.get("total")),
        ))
    db.session.flush()

    cid = order.customer.id if order.customer else None
    if created:
        log_activity("order.created", f"Order #{order.number} placed · {order.currency} {order.total}",
                     cid, order.id, created_at=order.date_created)
    elif old_status != order.status:
        log_activity("order.status_changed", f"Order #{order.number} moved from {old_status} to {order.status}",
                     cid, order.id)
    return order, created


# -------------------------------------------------------------- bulk syncing
_UPSERTS = {"products": upsert_product, "customers": upsert_customer, "orders": upsert_order}
_PATHS = {"products": "products", "customers": "customers", "orders": "orders"}
_PARAMS = {"customers": {"role": "all"}}


def sync_resource(client, resource: str) -> dict:
    if resource not in _UPSERTS:
        raise ValueError(f"Unknown resource '{resource}'")
    stats = {"created": 0, "updated": 0, "total": 0}
    for batch in client.pages(_PATHS[resource], _PARAMS.get(resource)):
        for item in batch:
            _, created = _UPSERTS[resource](item)
            stats["created" if created else "updated"] += 1
            stats["total"] += 1
        db.session.commit()  # commit per page: progress survives a later failure
    return stats


def sync(client, resources=None) -> dict:
    wanted = [r for r in RESOURCES if r in (resources or RESOURCES)]
    results = {}
    for resource in wanted:
        results[resource] = sync_resource(client, resource)
    summary = {"finished_at": utcnow().isoformat(), "results": results}
    parts = ", ".join(f"{v['total']} {k}" for k, v in results.items())
    log_activity("sync.completed", f"WooCommerce sync finished ({parts})")
    db.session.commit()
    set_last_sync(summary)
    return summary
