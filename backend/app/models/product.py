from ..extensions import db
from ..utils.time import iso, utcnow


class Product(db.Model):
    """Catalogue item synced from WooCommerce. Lets order lines link to real products."""
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    woo_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(100), default="")
    price = db.Column(db.Numeric(12, 2), default=0)
    status = db.Column(db.String(30), default="publish")
    stock_status = db.Column(db.String(30), default="instock")
    stock_quantity = db.Column(db.Integer, nullable=True)
    image_url = db.Column(db.String(500), default="")
    categories = db.Column(db.JSON, default=list)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id, "woo_id": self.woo_id, "name": self.name, "sku": self.sku,
            "price": float(self.price or 0), "status": self.status,
            "stock_status": self.stock_status, "stock_quantity": self.stock_quantity,
            "image_url": self.image_url, "categories": self.categories or [],
            "updated_at": iso(self.updated_at),
        }
