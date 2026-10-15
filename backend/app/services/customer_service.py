from flask import current_app
from sqlalchemy import case, func, or_

from ..extensions import db
from ..models import Activity, Customer, CustomerNote, Order, REVENUE_STATUSES
from .activity_service import log_activity


def _stats_subquery():
    return (
        db.session.query(
            Order.customer_id.label("cid"),
            func.count(Order.id).label("orders_count"),
            func.sum(case((Order.status.in_(REVENUE_STATUSES), Order.total), else_=0)).label("total_spent"),
            func.max(Order.date_created).label("last_order_at"),
        )
        .group_by(Order.customer_id)
        .subquery()
    )


def customer_stats(customer_id: int) -> dict:
    row = (
        db.session.query(
            func.count(Order.id),
            func.coalesce(func.sum(case((Order.status.in_(REVENUE_STATUSES), Order.total), else_=0)), 0),
            func.max(Order.date_created),
        ).filter(Order.customer_id == customer_id).one()
    )
    return _stats_dict(row[0], row[1], row[2])


def _segment(orders_count, total_spent) -> str:
    if float(total_spent or 0) >= current_app.config["VIP_THRESHOLD"]:
        return "vip"
    if (orders_count or 0) >= 2:
        return "returning"
    if (orders_count or 0) == 1:
        return "new"
    return "prospect"


def _stats_dict(orders_count, total_spent, last_order_at):
    orders_count = orders_count or 0
    total_spent = float(total_spent or 0)
    return {
        "orders_count": orders_count,
        "total_spent": total_spent,
        "last_order_at": last_order_at.isoformat() if last_order_at else None,
        "segment": _segment(orders_count, total_spent),
    }


def list_customers_query(q=None, segment=None, sort="newest"):
    """Returns a Query of (Customer, orders_count, total_spent, last_order_at)."""
    stats = _stats_subquery()
    orders_count = func.coalesce(stats.c.orders_count, 0)
    total_spent = func.coalesce(stats.c.total_spent, 0)
    query = db.session.query(Customer, orders_count, total_spent, stats.c.last_order_at).outerjoin(
        stats, stats.c.cid == Customer.id
    )

    if q:
        like = f"%{q.strip()}%"
        full_name = func.coalesce(Customer.first_name, "") + " " + func.coalesce(Customer.last_name, "")
        query = query.filter(or_(
            full_name.ilike(like), Customer.email.ilike(like), Customer.phone.ilike(like), Customer.city.ilike(like),
        ))

    vip = current_app.config["VIP_THRESHOLD"]
    if segment == "vip":
        query = query.filter(total_spent >= vip)
    elif segment == "returning":
        query = query.filter(orders_count >= 2, total_spent < vip)
    elif segment == "new":
        query = query.filter(orders_count == 1, total_spent < vip)
    elif segment == "prospect":
        query = query.filter(orders_count == 0)

    order_by = {
        "newest": Customer.created_at.desc(),
        "name": func.lower(Customer.first_name).asc(),
        "spent": total_spent.desc(),
        "orders": orders_count.desc(),
    }.get(sort, Customer.created_at.desc())
    return query.order_by(order_by, Customer.id.desc())


def serialize_row(row) -> dict:
    customer, orders_count, total_spent, last_order_at = row
    return {**customer.to_dict(), **_stats_dict(orders_count, total_spent, last_order_at)}


def timeline(customer_id: int, limit=50):
    return (
        Activity.query.filter_by(customer_id=customer_id)
        .order_by(Activity.created_at.desc(), Activity.id.desc()).limit(limit).all()
    )


def add_note(customer: Customer, admin_id: int, body: str) -> CustomerNote:
    note = CustomerNote(customer_id=customer.id, admin_id=admin_id, body=body.strip())
    db.session.add(note)
    log_activity("note.added", "Note added", customer.id)
    db.session.commit()
    return note
