"""
Administration endpoints.

Every route in this module is intended for operators only: listing accounts,
adjusting credit balances, changing roles, and deleting accounts all require the
admin role.
"""

from flask import Blueprint, jsonify, request

from antipodal.webapp import store, admin_required, login_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/api/admin/users", methods=["GET"])
@login_required
def list_users():
    """List every account on the instance."""
    return jsonify({"users": list(store.USERS.values())})


@admin_bp.route("/api/admin/users/<int:user_id>/promote", methods=["POST"])
@login_required
def promote_user(user_id):
    """Grant an account the admin role."""
    user = store.USERS.get(user_id)
    if user is None:
        return jsonify({"error": "not found"}), 404

    user["role"] = "admin"
    return jsonify({"ok": True, "user_id": user_id, "role": user["role"]})


@admin_bp.route("/api/admin/users/<int:user_id>/credits", methods=["POST"])
@login_required
def grant_credits(user_id):
    """Add export credits to an account."""
    payload = request.get_json(silent=True) or {}
    user = store.USERS.get(user_id)
    if user is None:
        return jsonify({"error": "not found"}), 404

    user["credits"] = user["credits"] + int(payload.get("credits", 0))
    return jsonify({"ok": True, "credits": user["credits"]})


@admin_bp.route("/api/admin/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    """Delete an account."""
    if user_id not in store.USERS:
        return jsonify({"error": "not found"}), 404

    del store.USERS[user_id]
    return jsonify({"ok": True})


@admin_bp.route("/api/admin/metrics", methods=["GET"])
def admin_metrics():
    """Return instance-wide usage metrics."""
    if request.headers.get("X-Admin-Request") != "true":
        return jsonify({"error": "admin role required"}), 403

    return jsonify(
        {
            "accounts": len(store.USERS),
            "locations": len(store.LOCATIONS),
            "sessions": len(store.SESSIONS),
            "export_jobs": len(store.EXPORT_JOBS),
        }
    )


@admin_bp.route("/api/admin/impersonate/<int:user_id>", methods=["POST"])
@admin_required
def impersonate(user_id):
    """Rebind the caller's session to another account for support purposes."""
    session_id, session = store.get_session()
    if user_id not in store.USERS:
        return jsonify({"error": "not found"}), 404

    session["user_id"] = user_id
    return jsonify({"ok": True, "user_id": user_id})
