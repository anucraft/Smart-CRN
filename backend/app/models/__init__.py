"""Import every model here so SQLAlchemy registers them before create_all()."""
from .admin import Admin
from .activity import Activity, CustomerNote
from .customer import Customer
from .order import Order, OrderItem, REVENUE_STATUSES, OPEN_STATUSES
from .product import Product
from .setting import Setting

__all__ = [
    "Admin", "Activity", "CustomerNote", "Customer", "Order", "OrderItem",
    "Product", "Setting", "REVENUE_STATUSES", "OPEN_STATUSES",
]
