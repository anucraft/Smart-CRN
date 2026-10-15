"""Small helpers so every route returns the same JSON shapes."""
from flask import jsonify, request


def error(message, status=400):
    return jsonify({"error": message}), status


def pagination_args(default_per_page=10, max_per_page=100):
    try:
        page = max(int(request.args.get("page", 1)), 1)
        per_page = int(request.args.get("per_page", default_per_page))
    except ValueError:
        page, per_page = 1, default_per_page
    return page, min(max(per_page, 1), max_per_page)


def paginate(query, page, per_page, serialize):
    """Works with any SQLAlchemy Query (including multi-entity ones)."""
    total = query.order_by(None).count()
    rows = query.offset((page - 1) * per_page).limit(per_page).all()
    return {
        "items": [serialize(r) for r in rows],
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": (total + per_page - 1) // per_page,
    }
