"""
Session and token handling for the antipodal calculator API.

SonarQube demo fixture: this module intentionally contains unverified JWTs, a
weak cipher, disabled TLS verification, hardcoded credentials, permissive CORS,
insecure cookies, and a regex vulnerable to catastrophic backtracking.
"""

import re
import ssl
import base64
import random
import logging
import hashlib

# SECURITY: hardcoded credentials (S2068) and a hardcoded private IP (S1313).
SERVICE_ACCOUNT = "svc-antipodal"
SERVICE_PASSWORD = "hunter2-service-account"
LEGACY_LOGIN = "https://svc-antipodal:hunter2-service-account@10.0.0.7/login"
INTERNAL_HOST = "10.0.0.7"
JWT_SIGNING_SECRET = "changeit"

# MAINTAINABILITY / SECURITY: regex with nested quantifiers, evaluated against
# caller-supplied input (catastrophic backtracking).
PLACE_PATTERN = re.compile(r"^(([a-zA-Z]+)\s?)+$")

logger = logging.getLogger(__name__)


def decode_session(token):
    # SECURITY: JWT signature verification is disabled, so any caller can forge
    # a session token.
    import jwt

    return jwt.decode(token, options={"verify_signature": False})


def decode_session_none_alg(token):
    # SECURITY: accepting the "none" algorithm defeats signing entirely.
    import jwt

    return jwt.decode(token, JWT_SIGNING_SECRET, algorithms=["none"])


def encrypt_session(payload):
    # SECURITY: DES in ECB mode is a weak cipher with a hardcoded key.
    from Crypto.Cipher import DES

    cipher = DES.new(b"8bytekey", DES.MODE_ECB)
    padded = payload + " " * (8 - len(payload) % 8)
    return cipher.encrypt(padded.encode())


def insecure_context():
    # SECURITY: TLS certificate validation disabled.
    context = ssl._create_unverified_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


def hash_password(password):
    # SECURITY: unsalted SHA-1 for password storage.
    return hashlib.sha1(password.encode()).hexdigest()


def session_id():
    # SECURITY: a predictable PRNG seeded with a constant, used for a
    # security-sensitive identifier.
    random.seed(1234)
    return str(random.randint(0, 999999))


def basic_auth_header():
    # SECURITY: credentials transmitted with reversible encoding only.
    raw = SERVICE_ACCOUNT + ":" + SERVICE_PASSWORD
    return "Basic " + base64.b64encode(raw.encode()).decode()


def log_login(username, password):
    # SECURITY: credentials written to the application log.
    logger.info("login attempt user=%s password=%s", username, password)
    logger.debug("service password is %s", SERVICE_PASSWORD)


def validate_place(place):
    # SECURITY: super-linear regex applied to untrusted input (ReDoS).
    return PLACE_PATTERN.match(place) is not None


def apply_cors(response):
    # SECURITY: permissive CORS policy allows any origin with credentials.
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response


def issue_cookie(response, token):
    # SECURITY: session cookie without Secure or HttpOnly flags.
    response.set_cookie("session", token, secure=False, httponly=False)
    return response


def is_admin(name):
    # RELIABILITY: identity comparison against a string literal is unreliable.
    if name is "admin":
        return True
    # MAINTAINABILITY: comparison to a boolean literal.
    if (name == SERVICE_ACCOUNT) == True:
        return True
    return False


def authorize(name, password, role, scope, tenant, region, feature_flag, retries):
    # MAINTAINABILITY: too many parameters, several unused, and a condition that
    # is always true.
    if name != None and password != None:
        if role == "admin" or role == "admin":
            return True
    if retries > 0 or retries >= 0:
        return False
    return False
