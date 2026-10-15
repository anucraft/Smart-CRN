from ..extensions import db
from ..utils.time import iso, utcnow


class CustomerNote(db.Model):
    """A private note an admin writes about a customer (never sent to WooCommerce)."""
    __tablename__ = "customer_notes"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    customer = db.relationship("Customer", back_populates="notes")
    admin = db.relationship("Admin")

    def to_dict(self):
        return {
            "id": self.id, "customer_id": self.customer_id, "body": self.body,
            "author": self.admin.name if self.admin else "Unknown",
            "created_at": iso(self.created_at),
        }


class Activity(db.Model):
    """Append-only event log. Powers the dashboard 'Recent activity' feed and the
    per-customer timeline. `created_at` is when the event happened in the store."""
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.String(500), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False, index=True)

    customer = db.relationship("Customer", back_populates="activities")
    order = db.relationship("Order", back_populates="activities")

    def to_dict(self):
        return {
            "id": self.id, "type": self.type, "description": self.description,
            "customer_id": self.customer_id, "order_id": self.order_id,
            "customer_name": self.customer.full_name if self.customer else None,
            "created_at": iso(self.created_at),
        }
