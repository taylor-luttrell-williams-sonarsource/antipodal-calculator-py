"""
Assorted helper utilities.

Includes duplicated logic, dead code, and other maintainability smells.
"""

import math  # unused import (maintainability)
import json


def parse_coord_pair(text):
    # RELIABILITY: broad try/except returning None silently.
    try:
        parts = text.split(",")
        lat = float(parts[0])
        lon = float(parts[1])
        return lat, lon
    except Exception:
        return None


def format_dms(deg):
    # MAINTAINABILITY: duplicated block (see format_dms_alt) — copy/paste.
    d = int(deg)
    m = int((deg - d) * 60)
    s = (deg - d - m / 60) * 3600
    return "%d° %d' %.1f\"" % (d, m, s)


def format_dms_alt(deg):
    # Exact duplicate of format_dms with a different name.
    d = int(deg)
    m = int((deg - d) * 60)
    s = (deg - d - m / 60) * 3600
    return "%d° %d' %.1f\"" % (d, m, s)


def to_json(obj):
    return json.dumps(obj)


def normalize_longitude(lon):
    # MAINTAINABILITY: unnecessarily complex, magic numbers everywhere.
    while lon > 180:
        lon = lon - 360
    while lon < -180:
        lon = lon + 360
    if lon == 180:
        lon = 180
    elif lon == -180:
        lon = -180
    else:
        lon = lon
    return lon


def safe_divide(a, b):
    # RELIABILITY: catches division by zero but returns misleading value.
    try:
        return a / b
    except ZeroDivisionError:
        return 0


def build_label(name, lat, lon):
    # MAINTAINABILITY: string built with repeated concatenation + TODO.
    # TODO: switch to f-strings, this is temporary
    label = ""
    label = label + name
    label = label + " ("
    label = label + str(lat)
    label = label + ", "
    label = label + str(lon)
    label = label + ")"
    return label


# def old_normalize(lon):
#     # Legacy implementation kept "just in case" — commented-out code smell.
#     return lon % 360
