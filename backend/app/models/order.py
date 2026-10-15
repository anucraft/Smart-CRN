from ..extensions import db
from ..utils.time import iso, utcnow

# Statuses whose value counts as revenue (money received or committed to be received).
REVENUE_STATUSES = ("completed", "processing")
# Orders that still need the owner's attention.
OPEN_STATUSES = ("pending", "on-hold", "processing")


class Order(db.Model):
    """A WooCommerce order. Payment/shipping status are DERIVED from the Woo status
    because WooCommerce has no separate shipping-status field."""
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    woo_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    number = db.Column(db.String(50), index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True, index=True)
    status = db.Column(db.String(30), nullable=False, default="pending", index=True)
    currency = db.Column(db.String(10), default="USD")
    total = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    total_tax = db.Column(db.Numeric(12, 2), default=0)
    shipping_total = db.Column(db.Numeric(12, 2), default=0)
    discount_total = db.Column(db.Numeric(12, 2), default=0)
    payment_method = db.Column(db.String(100), default="")
    payment_method_title = db.Column(db.String(150), default="")
    date_created = db.Column(db.DateTime, default=utcnow, nullable=False, index=True)
    date_paid = db.Column(db.DateTime, nullable=True)
    date_completed = db.Column(db.DateTime, nullable=True)
    billing = db.Column(db.JSON, default=dict)
    shipping = db.Column(db.JSON, default=dict)
    customer_note = db.Column(db.Text, default="")

    customer = db.relationship("Customer", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    activities = db.relationship("Activity", back_populates="order")

    @property
    def payment_status(self) -> str:
        if self.status == "refunded":
            return "refunded"
        if self.status == "failed":
            return "failed"
        if self.status == "cancelled":
            return "cancelled"
        return "paid" if (self.date_paid or self.status == "completed") else "pending"

    @property
    def shipping_status(self) -> str:
        return {
            "pending": "awaiting_payment",
            "on-hold": "on_hold",
            "processing": "to_ship",
            "completed": "delivered",
        }.get(self.status, "not_applicable")

    def _base(self):
        return {
            "id": self.id,
            "woo_id": self.woo_id,
            "number": self.number,
            "status": self.status,
            "payment_status": self.payment_status,
            "shipping_status": self.shipping_status,
            "currency": self.currency,
            "total": float(self.total or 0),
            "date_created": iso(self.date_created),
            "customer": (
                {"id": self.customer.id, "name": self.customer.full_name, "email": self.customer.email}
                if self.customer else None
            ),
        }

    def to_dict(self):
        return self._base()

    def to_detail_dict(self):
        data = self._base()
        data.update({
            "total_tax": float(self.total_tax or 0),
            "shipping_total": float(self.shipping_total or 0),
            "discount_total": float(self.discount_total or 0),
            "payment_method": self.payment_method_title or self.payment_method,
            "date_paid": iso(self.date_paid),
            "date_completed": iso(self.date_completed),
            "billing": self.billing or {},
            "shipping": self.shipping or {},
            "customer_note": self.customer_note,
            "items": [i.to_dict() for i in self.items],
        })
        return data


class OrderItem(db.Model):
    """One line of an order (normalisation: an order has many items)."""
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    woo_product_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(100), default="")
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Numeric(12, 2), default=0)
    total = db.Column(db.Numeric(12, 2), default=0)

    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product")

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "sku": self.sku, "quantity": self.quantity,
            "price": float(self.price or 0), "total": float(self.total or 0),
        }
