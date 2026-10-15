from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ..services import activity_service, analytics_service

bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


def _int_arg(name, default, lo, hi):
    try:
        return min(max(int(request.args.get(name, default)), lo), hi)
    except ValueError:
        return default


@bp.get("/summary")
@jwt_required()
def summary():
    return jsonify(analytics_service.summary())


@bp.get("/monthly-sales")
@jwt_required()
def monthly_sales():
    return jsonify({"items": analytics_service.monthly_sales(_int_arg("months", 12, 1, 24))})


@bp.get("/customer-growth")
@jwt_required()
def customer_growth():
    return jsonify({"items": analytics_service.customer_growth(_int_arg("months", 12, 1, 24))})


@bp.get("/top-customers")
@jwt_required()
def top_customers():
    return jsonify({"items": analytics_service.top_customers(_int_arg("limit", 5, 1, 20))})


@bp.get("/recent-activity")
@jwt_required()
def recent_activity():
    items = activity_service.recent_activity(_int_arg("limit", 10, 1, 50))
    return jsonify({"items": [a.to_dict() for a in items]})
