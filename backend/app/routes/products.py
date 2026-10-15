from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ..models import Product
from ..utils.responses import pagination_args, paginate

bp = Blueprint("products", __name__, url_prefix="/api/products")


@bp.get("")
@jwt_required()
def list_products():
    page, per_page = pagination_args(default_per_page=12)
    query = Product.query
    q = request.args.get("q")
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(Product.name.ilike(like) | Product.sku.ilike(like))
    return jsonify(paginate(query.order_by(Product.name.asc()), page, per_page, lambda p: p.to_dict()))
