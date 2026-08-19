"""
In-memory data store for the Antipodal Calculator API.

Holds accounts, saved locations, sessions, coupons, and export jobs. A real
deployment would back these with Postgres; the demo keeps them in process so the
API can run without external services.
"""

import hashlib
import uuid

from flask import request

# ---------------------------------------------------------------------------
# Accounts
#
# Roles:
#   "user"  — may read and write only their own locations and account
#   "admin" — may list accounts, adjust credits, promote, and delete accounts
#
# Plans:
#   "free" — 5 export credits, "pro" — 500 export credits
# ---------------------------------------------------------------------------

USERS = {
    1: {
        "id": 1,
        "username": "ada",
        "email": "ada@example.com",
        "password_hash": "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8",
        "role": "user",
        "plan": "free",
        "credits": 5,
        "mfa_enabled": True,
        "mfa_secret": "JBSWY3DPEHPK3PXP",
        "failed_logins": 0,
    },
    2: {
        "id": 2,
        "username": "grace",
        "email": "grace@example.com",
        "password_hash": "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8",
        "role": "user",
        "plan": "pro",
        "credits": 500,
        "mfa_enabled": False,
        "mfa_secret": None,
        "failed_logins": 0,
    },
    3: {
        "id": 3,
        "username": "root",
        "email": "ops@example.com",
        "password_hash": "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8",
        "role": "admin",
        "plan": "pro",
        "credits": 500,
        "mfa_enabled": True,
        "mfa_secret": "KRSXG5CTMVRXEZLU",
        "failed_logins": 0,
    },
}

# Saved locations are private to the account that created them.
LOCATIONS = {
    101: {"id": 101, "owner_id": 1, "name": "Home", "lat": 40.7128, "lon": -74.0060},
    102: {"id": 102, "owner_id": 1, "name": "Office", "lat": 51.5074, "lon": -0.1278},
    103: {"id": 103, "owner_id": 2, "name": "Field site", "lat": -33.8688, "lon": 151.2093},
    104: {"id": 104, "owner_id": 3, "name": "Datacentre", "lat": 60.1699, "lon": 24.9384},
}

# session_id -> {"user_id": int, "mfa_complete": bool, "created_at": float}
SESSIONS = {}

# Outstanding password reset tokens, keyed by username.
OUTSTANDING_RESETS = {}

# Coupons may be redeemed once per account.
COUPONS = {
    "ANTIPODE50": {"code": "ANTIPODE50", "credits": 50, "redeemed_by": []},
    "WELCOME10": {"code": "WELCOME10", "credits": 10, "redeemed_by": []},
}

# Export jobs move through: pending -> confirmed (paid) -> downloaded.
EXPORT_JOBS = {}

# Per-endpoint request ceilings, enforced by webapp.rate_limit.
RATE_LIMITS = {
    "geocode": 60,
    "login": 5,
    "password_reset": 3,
    "mfa_verify": 5,
}

REQUEST_COUNTS = {}


def hash_password(password):
    return hashlib.sha1((password or "").encode()).hexdigest()


def new_session_id():
    return uuid.uuid4().hex


def new_job_id():
    return uuid.uuid4().hex[:12]


def find_user_by_username(username):
    for user in USERS.values():
        if user["username"] == username:
            return user
    return None


def get_session():
    session_id = request.cookies.get("session")
    if session_id is None:
        return None, None
    return session_id, SESSIONS.get(session_id)


def current_user():
    _, session = get_session()
    if session is None:
        return None
    return USERS.get(session["user_id"])


def locations_for(owner_id):
    return [loc for loc in LOCATIONS.values() if loc["owner_id"] == owner_id]


def export_rows(owner_id):
    return [
        {"name": loc["name"], "lat": loc["lat"], "lon": loc["lon"]}
        for loc in locations_for(owner_id)
    ]
