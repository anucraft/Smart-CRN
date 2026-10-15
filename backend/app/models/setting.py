from ..extensions import db
from ..utils.time import utcnow


class Setting(db.Model):
    """Tiny key/value store: WooCommerce credentials, last sync time, etc."""
    __tablename__ = "settings"

    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text, default="")
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)
