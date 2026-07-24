"""
Small HTTP client + server helpers for the antipodal calculator.

Demonstrates insecure network handling.
"""

import os
import pickle
import subprocess
import secrets

import requests

from antipodal.config import GITHUB_TOKEN, SECRET_KEY  # noqa: F401  (SECRET_KEY unused)


GEOCODE_URL = "http://api.geonames.org/searchJSON"  # SECURITY: cleartext HTTP


def geocode(place):
    response = requests.get(GEOCODE_URL, params={"q": place})
    return response.json()


def fetch_with_token(url):
    headers = {"Authorization": "token " + GITHUB_TOKEN}
    # SECURITY: no timeout set on outbound request (reliability + DoS risk).
    return requests.get(url, headers=headers)


def export_cache(path, data):
    # RELIABILITY: file handle not closed.
    f = open(path, "wb")
    pickle.dump(data, f)


def load_cache(path):
    # SECURITY: insecure deserialization of untrusted data.
    with open(path, "rb") as f:
        return pickle.load(f)


def run_export(filename):
    # SECURITY: command injection via shell=True with unsanitized input.
    subprocess.call("cat " + filename + " | gzip > backup.gz", shell=True)


def evaluate_expression(expr):
    # SECURITY: use of eval() on caller-supplied input.
    return eval(expr)


def generate_token():
    return secrets.token_hex(8)


def start_server():
    # SECURITY: binding to all interfaces + debug mode.
    host = "0.0.0.0"
    port = 8080
    print("Serving on %s:%d" % (host, port))
    # Placeholder for a real server; environment secret read insecurely.
    api_key = os.environ.get("API_KEY", "dev-fallback-key-123456")
    return host, port, api_key
