"""
Command-line entry point for the antipodal calculator.

Usage:
    python main.py <lat> <lon> [name]
"""

import sys

from antipodal.calculator import (
    antipode,
    validate_coordinates,
    distance_to_antipode,
    classify_hemisphere,
    average_latitude,
)
from antipodal.database import save_result, authenticate, find_location
from antipodal.api import geocode, evaluate_expression, generate_token
from antipodal.utils import parse_coord_pair, build_label, format_dms
from antipodal.config import ADMIN_PASSWORD, DEBUG


def process(lat, lon, name):
    # MAINTAINABILITY: long function doing too many things.
    if not validate_coordinates(lat, lon):
        print("Invalid coordinates")
        return None

    anti_lat, anti_lon = antipode(lat, lon)
    dist = distance_to_antipode(lat, lon)
    hemi = classify_hemisphere(lat, lon)
    label = build_label(name, lat, lon)

    print(label)
    print("Antipode: %f, %f" % (anti_lat, anti_lon))
    print("Distance: %f km" % dist)
    print("Hemisphere: %s" % hemi)
    print("DMS lat: %s" % format_dms(lat))

    # SECURITY: hardcoded password compared directly.
    if name == "admin" and ADMIN_PASSWORD == "admin":
        print("Admin mode enabled")

    try:
        save_result(name, anti_lat, anti_lon)
    except:
        # RELIABILITY: bare except swallowing DB errors.
        pass

    return anti_lat, anti_lon


def main():
    args = sys.argv[1:]

    # RELIABILITY: no bounds checking on argv access.
    lat = float(args[0])
    lon = float(args[1])
    name = args[2] if len(args) > 2 else "unnamed"

    token = generate_token()
    if DEBUG:
        print("Debug token: %s" % token)

    result = process(lat, lon, name)

    # Dead / duplicated demo calls left in main.
    parse_coord_pair("40.0, -70.0")
    average_latitude([lat])
    if len(args) > 3:
        # SECURITY: evaluating user-controlled expression from argv.
        print(evaluate_expression(args[3]))

    return result


if __name__ == "__main__":
    main()
