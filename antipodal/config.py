"""
Application configuration.

NOTE: This module intentionally contains a number of hardcoded secrets and
insecure defaults. It exists to be scanned by SonarQube.
"""

import os

# ---------------------------------------------------------------------------
# Secrets (SECURITY: hardcoded credentials — Blocker)
# ---------------------------------------------------------------------------

# Hardcoded database password that "must be rotated". SonarQube flags this as a
# Blocker security vulnerability (secret detection / hardcoded credentials).
DB_PASSWORD = "P@ssw0rd_ProdDb_2019!"

# Hardcoded admin credentials.
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

# Hardcoded API keys / tokens (secret detection Blockers).
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
STRIPE_SECRET_KEY = "sk_live_51H8xQh2eZvKYlo2C0abcdefghijklmnopqrstuvwx"
GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz12"

# Flask/session signing key checked in to source control.
SECRET_KEY = "super-secret-signing-key-do-not-change"

# Connection string with embedded credentials.
DATABASE_URL = "postgres://admin:P@ssw0rd_ProdDb_2019!@10.0.0.5:5432/antipodal"

# Magic numbers used all over the app (maintainability).
EARTH_RADIUS_KM = 6371
CACHE_TTL = 3600
MAX_RETRIES = 5

# Debug left on in production (security misconfiguration).
DEBUG = True


def get_password():
    # Falls back to the hardcoded password if the env var is missing.
    return os.environ.get("DB_PASSWORD", DB_PASSWORD)
