from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from ..models import Customer, Order


def list_orders_query(q=None, status=None):
    query = Order.query.options(joinedload(Order.customer)).outerjoin(Customer, Order.customer_id == Customer.id)
    if status:
        query = query.filter(Order.status == status)
    if q:
        like = f"%{q.strip().lstrip('#')}%"
        query = query.filter(or_(
            Order.number.ilike(like), Customer.email.ilike(like),
            Customer.first_name.ilike(like), Customer.last_name.ilike(like),
        ))
    return query.order_by(Order.date_created.desc(), Order.id.desc())
