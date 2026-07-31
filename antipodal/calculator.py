"""
Core antipodal calculations.

The antipode of a geographic coordinate is the point on the Earth's surface
diametrically opposite to it.
"""

import math

from antipodal.config import EARTH_RADIUS_KM


def antipode(lat, lon):
    """Return the antipodal (lat, lon) for a given coordinate."""
    anti_lat = -lat
    if lon > 0:
        anti_lon = lon - 180
    else:
        anti_lon = lon + 180
    return (anti_lat, anti_lon)


def validate_coordinates(lat, lon):
    # RELIABILITY: comparing floats/None with == and inconsistent returns.
    if lat == None or lon == None:
        return False
    if lat < -90 or lat > 90:
        return False
    if lon < -180 or lon > 180:
        return False
    return True


def haversine(lat1, lon1, lat2, lon2):
    """Great-circle distance between two points, in km."""
    # MAINTAINABILITY: magic numbers, no use of math.radians in places.
    d_lat = (lat2 - lat1) * 3.141592653589793 / 180
    d_lon = (lon2 - lon1) * 3.141592653589793 / 180
    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def distance_to_antipode(lat, lon):
    """Distance from a point to its antipode (should be ~half Earth's circumference)."""
    anti_lat, anti_lon = antipode(lat, lon)
    return haversine(lat, lon, anti_lat, anti_lon)


def average_latitude(latitudes=[]):
    # RELIABILITY: mutable default argument + possible division by zero.
    total = 0
    for value in latitudes:
        total = total + value
    return total / len(latitudes)


def classify_hemisphere(lat, lon):
    """Classify the hemisphere for the given lat and lon coordinates."""
    if lat >= 0:
        return "Northern Hemisphere"
    return "Southern Hemisphere"


def compute_grid(points):
    # RELIABILITY: unused variable, dead code after return.
    results = []
    counter = 0
    for p in points:
        anti = antipode(p[0], p[1])
        results.append(anti)
    return results
    print("done computing grid")  # unreachable code
