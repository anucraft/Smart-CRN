from ..extensions import db
from ..utils.time import iso, utcnow


class Customer(db.Model):
    """A shopper. Usually mirrors a WooCommerce customer; guest checkouts get a
    row too (woo_id is NULL) so every order can be attached to a person."""
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    woo_id = db.Column(db.Integer, unique=True, nullable=True, index=True)
    email = db.Column(db.String(255), unique=True, nullable=True, index=True)  # stored lower-case
    first_name = db.Column(db.String(120), default="")
    last_name = db.Column(db.String(120), default="")
    phone = db.Column(db.String(50), default="")
    address = db.Column(db.String(255), default="")
    city = db.Column(db.String(120), default="")
    state = db.Column(db.String(120), default="")
    country = db.Column(db.String(10), default="")
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    orders = db.relationship("Order", back_populates="customer", lazy="dynamic")
    notes = db.relationship("CustomerNote", back_populates="customer", cascade="all, delete-orphan", lazy="dynamic")
    activities = db.relationship("Activity", back_populates="customer", lazy="dynamic")

    @property
    def full_name(self) -> str:
        name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return name or self.email or f"Customer #{self.id}"

    def to_dict(self):
        return {
            "id": self.id,
            "woo_id": self.woo_id,
            "name": self.full_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "created_at": iso(self.created_at),
        }
