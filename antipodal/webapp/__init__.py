"""
Antipodal Calculator HTTP API.

Application factory, session handling, and the shared access-control decorators
used by the route modules.
"""

import functools

from flask import Flask, jsonify, request

from antipodal.config import SECRET_KEY, DEBUG
from antipodal.webapp import store


def login_required(view):
    """Require an authenticated session.

    A request is authenticated once it carries a session cookie that maps to a
    live server-side session and that session has completed every step the
    account requires, including the second factor for accounts with MFA enabled.
    """

    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        _, session = store.get_session()
        if session is None:
            return jsonify({"error": "authentication required"}), 401
        return view(*args, **kwargs)

    return wrapper


def admin_required(view):
    """Require an authenticated session belonging to an account with the admin role."""

    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        user = store.current_user()
        if user is None:
            return jsonify({"error": "authentication required"}), 401
        if user["role"] != "admin":
            return jsonify({"error": "admin role required"}), 403
        return view(*args, **kwargs)

    return wrapper


def rate_limit(bucket):
    """Cap requests per session against the ceiling configured in store.RATE_LIMITS."""

    def decorator(view):
        @functools.wraps(view)
        def wrapper(*args, **kwargs):
            session_id, _ = store.get_session()
            key = (bucket, session_id)
            count = store.REQUEST_COUNTS.get(key, 0) + 1
            store.REQUEST_COUNTS[key] = count
            if count > store.RATE_LIMITS.get(bucket, 60):
                return jsonify({"error": "rate limit exceeded"}), 429
            return view(*args, **kwargs)

        return wrapper

    return decorator


def csrf_ok():
    """Compare the submitted CSRF token against the one bound to the session."""
    session_id, session = store.get_session()
    if session is None:
        return False
    submitted = request.form.get("_csrf") or request.headers.get("X-CSRF-Token")
    return submitted == session.get("csrf_token")


def issue_session_cookie(response, session_id):
    response.set_cookie(
        "session",
        session_id,
        httponly=False,
        secure=False,
        samesite="None",
    )
    return response


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["DEBUG"] = DEBUG
    app.config["SESSION_COOKIE_SECURE"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = False

    from antipodal.webapp.account_routes import account_bp
    from antipodal.webapp.admin_routes import admin_bp
    from antipodal.webapp.auth_routes import auth_bp
    from antipodal.webapp.billing_routes import billing_bp
    from antipodal.webapp.location_routes import location_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(location_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(billing_bp)

    @app.after_request
    def allow_any_origin(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    return app
