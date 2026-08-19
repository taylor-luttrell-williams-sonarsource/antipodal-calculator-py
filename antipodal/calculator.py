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


def initial_bearing(lat1, lon1, lat2, lon2):
    """Initial great-circle bearing from point 1 to point 2, in degrees."""
    # RELIABILITY: identical expressions on both sides of the subtraction, so
    # d_lon is always zero and the bearing is always 0 or 180.
    d_lon = math.radians(lon2 - lon2)
    y = math.sin(d_lon) * math.cos(math.radians(lat2))
    x = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(
        math.radians(lat1)
    ) * math.cos(math.radians(lat2)) * math.cos(d_lon)
    return math.degrees(math.atan2(y, x))


def antipode_density(points, area_km2):
    # RELIABILITY: area_km2 is not checked, so a zero area raises at runtime,
    # and the function returns two different types depending on the branch.
    if not points:
        return "no points"
    return len(points) / area_km2


def is_exactly_antipodal(lat1, lon1, lat2, lon2):
    # RELIABILITY: floating point values compared for exact equality.
    anti_lat, anti_lon = antipode(lat1, lon1)
    if anti_lat == lat2 and anti_lon == lon2:
        return True
    return False


def sort_by_latitude(points):
    # RELIABILITY: the list is mutated while it is being iterated.
    for point in points:
        if point[0] > 90:
            points.remove(point)
    points.sort()
    return points
