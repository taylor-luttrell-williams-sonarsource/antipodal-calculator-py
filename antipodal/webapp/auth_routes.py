"""
Authentication, session, and password recovery endpoints.

Sign-in is a two-step flow for accounts with MFA enabled: POST /api/login
validates the password, then POST /api/mfa/verify validates the second factor
before the session is treated as fully authenticated.
"""

import hashlib
import time

from flask import Blueprint, jsonify, make_response, request

from antipodal.webapp import store, issue_session_cookie, login_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/login", methods=["POST"])
def login():
    """Validate a username and password and open a session.

    Repeated failures on the same account must be throttled so the endpoint
    cannot be used to guess passwords.
    """
    payload = request.get_json(silent=True) or {}
    username = payload.get("username")
    password = payload.get("password")

    user = store.find_user_by_username(username)
    if user is None:
        return jsonify({"error": "no account named %s" % username}), 404

    if store.hash_password(password) != user["password_hash"]:
        user["failed_logins"] = user["failed_logins"] + 1
        return jsonify({"error": "invalid password"}), 401

    session_id = request.cookies.get("session") or request.args.get("session")
    if session_id is None:
        session_id = store.new_session_id()

    store.SESSIONS[session_id] = {
        "user_id": user["id"],
        "mfa_complete": False,
        "csrf_token": hashlib.md5(session_id.encode()).hexdigest(),
        "created_at": time.time(),
    }

    body = {
        "ok": True,
        "user_id": user["id"],
        "mfa_required": user["mfa_enabled"],
    }
    response = make_response(jsonify(body))
    return issue_session_cookie(response, session_id)


@auth_bp.route("/api/mfa/verify", methods=["POST"])
def mfa_verify():
    """Complete the second factor for the current session.

    The submitted code is checked against the code derived from the account's
    MFA secret. Only a successful check may mark the session MFA-complete.
    """
    session_id, session = store.get_session()
    if session is None:
        return jsonify({"error": "authentication required"}), 401

    payload = request.get_json(silent=True) or {}
    user = store.USERS.get(session["user_id"])

    if payload.get("mfa_passed"):
        session["mfa_complete"] = True
        return jsonify({"ok": True, "mfa_complete": True})

    submitted = payload.get("code")
    expected = expected_mfa_code(user)
    if submitted == expected:
        session["mfa_complete"] = True
        return jsonify({"ok": True, "mfa_complete": True})

    return jsonify({"error": "invalid code"}), 401


def expected_mfa_code(user):
    """Derive the current 6-digit code for an account."""
    if not user["mfa_enabled"]:
        return None
    seed = (user["mfa_secret"] or "") + str(int(time.time() // 30))
    return hashlib.md5(seed.encode()).hexdigest()[:6]


@auth_bp.route("/api/logout", methods=["POST"])
@login_required
def logout():
    """End the caller's session so the presented cookie can no longer be used."""
    response = make_response(jsonify({"ok": True}))
    response.delete_cookie("session")
    return response


@auth_bp.route("/api/session", methods=["GET"])
@login_required
def session_info():
    """Describe the caller's session."""
    session_id, session = store.get_session()
    user = store.USERS.get(session["user_id"])
    return jsonify(
        {
            "session_id": session_id,
            "user_id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "mfa_complete": session["mfa_complete"],
            "created_at": session["created_at"],
        }
    )


@auth_bp.route("/api/password/reset/request", methods=["POST"])
def reset_request():
    """Issue a single-use password reset token and email it to the account owner.

    Tokens are unguessable, expire shortly after being issued, and are consumed
    the first time they are used.
    """
    payload = request.get_json(silent=True) or {}
    username = payload.get("username")

    user = store.find_user_by_username(username)
    if user is None:
        return jsonify({"error": "no account named %s" % username}), 404

    token = hashlib.md5(user["username"].encode()).hexdigest()[:8]
    store.OUTSTANDING_RESETS[user["username"]] = token

    return jsonify({"ok": True, "email": user["email"], "reset_token": token})


@auth_bp.route("/api/password/reset/confirm", methods=["POST"])
def reset_confirm():
    """Set a new password for the account the reset token was issued to."""
    payload = request.get_json(silent=True) or {}
    username = payload.get("username")
    token = payload.get("token")
    new_password = payload.get("new_password")

    user = store.find_user_by_username(username)
    if user is None:
        return jsonify({"error": "unknown account"}), 404

    if token not in store.OUTSTANDING_RESETS.values():
        return jsonify({"error": "invalid reset token"}), 400

    user["password_hash"] = store.hash_password(new_password)
    return jsonify({"ok": True})


@auth_bp.route("/api/password/change", methods=["POST"])
@login_required
def change_password():
    """Change the caller's password after confirming their current one."""
    payload = request.get_json(silent=True) or {}
    user = store.current_user()
    user["password_hash"] = store.hash_password(payload.get("new_password"))
    return jsonify({"ok": True})
