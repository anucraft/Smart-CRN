from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..extensions import db
from ..models import CustomerNote, Customer, Order
from ..services import customer_service
from ..utils.responses import error, pagination_args, paginate

bp = Blueprint("customers", __name__, url_prefix="/api/customers")


@bp.get("")
@jwt_required()
def list_customers():
    page, per_page = pagination_args()
    query = customer_service.list_customers_query(
        q=request.args.get("q"), segment=request.args.get("segment"), sort=request.args.get("sort", "newest"),
    )
    return jsonify(paginate(query, page, per_page, customer_service.serialize_row))


def _get_or_404(customer_id):
    return db.session.get(Customer, customer_id)


@bp.get("/<int:customer_id>")
@jwt_required()
def get_customer(customer_id):
    customer = _get_or_404(customer_id)
    if customer is None:
        return error("Customer not found.", 404)
    recent_orders = customer.orders.order_by(Order.date_created.desc()).limit(10).all()
    return jsonify({
        **customer.to_dict(),
        **customer_service.customer_stats(customer.id),
        "recent_orders": [o.to_dict() for o in recent_orders],
    })


@bp.get("/<int:customer_id>/timeline")
@jwt_required()
def get_timeline(customer_id):
    if _get_or_404(customer_id) is None:
        return error("Customer not found.", 404)
    return jsonify({"items": [a.to_dict() for a in customer_service.timeline(customer_id)]})


@bp.get("/<int:customer_id>/notes")
@jwt_required()
def list_notes(customer_id):
    customer = _get_or_404(customer_id)
    if customer is None:
        return error("Customer not found.", 404)
    notes = customer.notes.order_by(CustomerNote.created_at.desc(), CustomerNote.id.desc()).all()
    return jsonify({"items": [n.to_dict() for n in notes]})


@bp.post("/<int:customer_id>/notes")
@jwt_required()
def create_note(customer_id):
    customer = _get_or_404(customer_id)
    if customer is None:
        return error("Customer not found.", 404)
    body = ((request.get_json(silent=True) or {}).get("body") or "").strip()
    if not body:
        return error("Note cannot be empty.", 400)
    if len(body) > 2000:
        return error("Note is too long (max 2000 characters).", 400)
    note = customer_service.add_note(customer, int(get_jwt_identity()), body)
    return jsonify(note.to_dict()), 201


@bp.delete("/<int:customer_id>/notes/<int:note_id>")
@jwt_required()
def delete_note(customer_id, note_id):
    note = CustomerNote.query.filter_by(id=note_id, customer_id=customer_id).first()
    if note is None:
        return error("Note not found.", 404)
    db.session.delete(note)
    db.session.commit()
    return "", 204
