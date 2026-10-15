"""All dashboard / analytics numbers. Money statuses are defined in models.order."""
from collections import OrderedDict
from datetime import datetime

from sqlalchemy import case, func

from ..extensions import db
from ..models import Customer, Order, OPEN_STATUSES, REVENUE_STATUSES
from ..utils.time import utcnow


def _month_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m")


def _last_n_months(n: int):
    """['2025-11', ..., '2026-10'] ending with the current month."""
    now = utcnow()
    year, month = now.year, now.month
    keys = []
    for _ in range(n):
        keys.append(f"{year:04d}-{month:02d}")
        month -= 1
        if month == 0:
            month, year = 12, year - 1
    return list(reversed(keys))


def summary() -> dict:
    revenue = db.session.query(func.coalesce(func.sum(Order.total), 0)).filter(Order.status.in_(REVENUE_STATUSES)).scalar()
    total_orders = Order.query.count()
    paying_orders = Order.query.filter(Order.status.in_(REVENUE_STATUSES)).count()
    return {
        "total_customers": Customer.query.count(),
        "total_orders": total_orders,
        "revenue": float(revenue or 0),
        "pending_orders": Order.query.filter(Order.status.in_(OPEN_STATUSES)).count(),
        "average_order_value": round(float(revenue or 0) / paying_orders, 2) if paying_orders else 0,
    }


def monthly_sales(months: int = 12) -> list:
    keys = _last_n_months(months)
    buckets = OrderedDict((k, {"month": k, "revenue": 0.0, "orders": 0}) for k in keys)
    start = datetime.strptime(keys[0] + "-01", "%Y-%m-%d")
    rows = db.session.query(Order.date_created, Order.total, Order.status).filter(Order.date_created >= start).all()
    for created, total, status in rows:
        bucket = buckets.get(_month_key(created))
        if bucket is None:
            continue
        bucket["orders"] += 1
        if status in REVENUE_STATUSES:
            bucket["revenue"] += float(total or 0)
    for b in buckets.values():
        b["revenue"] = round(b["revenue"], 2)
    return list(buckets.values())


def customer_growth(months: int = 12) -> list:
    keys = _last_n_months(months)
    start = datetime.strptime(keys[0] + "-01", "%Y-%m-%d")
    before = Customer.query.filter(Customer.created_at < start).count()
    new_per_month = {k: 0 for k in keys}
    for (created,) in db.session.query(Customer.created_at).filter(Customer.created_at >= start).all():
        key = _month_key(created)
        if key in new_per_month:
            new_per_month[key] += 1
    result, running = [], before
    for k in keys:
        running += new_per_month[k]
        result.append({"month": k, "new_customers": new_per_month[k], "total_customers": running})
    return result


def top_customers(limit: int = 5) -> list:
    rows = (
        db.session.query(
            Customer,
            func.sum(case((Order.status.in_(REVENUE_STATUSES), Order.total), else_=0)).label("spent"),
            func.count(Order.id).label("orders"),
        )
        .join(Order, Order.customer_id == Customer.id)
        .group_by(Customer.id)
        .order_by(func.sum(case((Order.status.in_(REVENUE_STATUSES), Order.total), else_=0)).desc())
        .limit(limit)
        .all()
    )
    return [
        {"id": c.id, "name": c.full_name, "email": c.email, "total_spent": float(spent or 0), "orders_count": count}
        for c, spent, count in rows
    ]
