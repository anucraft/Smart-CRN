from ..extensions import db
from ..models import Activity
from ..utils.time import utcnow


def log_activity(type_, description, customer_id=None, order_id=None, created_at=None):
    """Add (but do not commit) an activity row; the caller owns the transaction."""
    activity = Activity(
        type=type_, description=description, customer_id=customer_id,
        order_id=order_id, created_at=created_at or utcnow(),
    )
    db.session.add(activity)
    return activity


def recent_activity(limit=10):
    return Activity.query.order_by(Activity.created_at.desc(), Activity.id.desc()).limit(limit).all()
