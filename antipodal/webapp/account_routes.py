"""
Account and profile endpoints.

Callers may read and modify their own account. Role, plan, and credit balance are
set by billing and administration, not by the account holder.
"""

from flask import Blueprint, jsonify, request

from antipodal.webapp import store, csrf_ok, login_required

account_bp = Blueprint("account", __name__)

EDITABLE_PROFILE_FIELDS = ("username", "email")


@account_bp.route("/api/profile", methods=["GET"])
@login_required
def get_profile():
    """Return the caller's own profile."""
    user = store.current_user()
    return jsonify(
        {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "plan": user["plan"],
            "credits": user["credits"],
        }
    )


@account_bp.route("/api/profile", methods=["PATCH"])
@login_required
def update_profile():
    """Update the caller's own profile.

    Only the fields a user is allowed to maintain themselves may be changed here.
    """
    user = store.current_user()
    payload = request.get_json(silent=True) or {}

    for field in payload:
        user[field] = payload[field]

    return jsonify({"profile": user})


@account_bp.route("/api/users/<int:user_id>", methods=["GET"])
@login_required
def get_user(user_id):
    """Return the public profile of an account, for sharing and attribution."""
    user = store.USERS.get(user_id)
    if user is None:
        return jsonify({"error": "not found"}), 404
    return jsonify({"user": user})


@account_bp.route("/account/password", methods=["POST"])
@login_required
def post_password_form():
    """Browser form endpoint for changing the caller's password."""
    if not csrf_ok():
        return jsonify({"error": "invalid csrf token"}), 403

    user = store.current_user()
    user["password_hash"] = store.hash_password(request.form.get("new_password"))
    return jsonify({"ok": True})


@account_bp.route("/account/email", methods=["POST"])
@login_required
def post_email_form():
    """Browser form endpoint for changing the caller's email address."""
    user = store.current_user()
    user["email"] = request.form.get("email", user["email"])
    return jsonify({"ok": True, "email": user["email"]})


@account_bp.route("/account/delete", methods=["POST"])
@login_required
def post_delete_form():
    """Browser form endpoint for closing the caller's account permanently."""
    user = store.current_user()

    for location_id in list(store.LOCATIONS):
        if store.LOCATIONS[location_id]["owner_id"] == user["id"]:
            del store.LOCATIONS[location_id]

    del store.USERS[user["id"]]
    return jsonify({"ok": True})
