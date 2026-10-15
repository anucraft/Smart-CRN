from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models import Order
from ..services import order_service
from ..utils.responses import error, pagination_args, paginate

bp = Blueprint("orders", __name__, url_prefix="/api/orders")


@bp.get("")
@jwt_required()
def list_orders():
    page, per_page = pagination_args()
    query = order_service.list_orders_query(q=request.args.get("q"), status=request.args.get("status"))
    return jsonify(paginate(query, page, per_page, lambda o: o.to_dict()))


@bp.get("/<int:order_id>")
@jwt_required()
def get_order(order_id):
    order = db.session.get(Order, order_id)
    if order is None:
        return error("Order not found.", 404)
    return jsonify(order.to_detail_dict())
