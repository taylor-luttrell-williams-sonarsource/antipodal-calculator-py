"""
Reporting and summary helpers.

SonarQube demo fixture: this module intentionally contains high cognitive
complexity, copy/pasted blocks, dead stores, always-true conditions, shadowed
builtins, and a guaranteed division by zero.
"""

import io  # unused import (maintainability)
import json
import math

from antipodal.calculator import antipode, classify_hemisphere

SEPARATOR = "----------------------------------------"
OUT_OF_RANGE = "out of range"


def summarize_northern(points):
    # MAINTAINABILITY: this body is copy/pasted verbatim into
    # summarize_southern below — duplicated code block.
    lines = []
    total_lat = 0
    total_lon = 0
    counted = 0
    for point in points:
        lat = point[0]
        lon = point[1]
        anti_lat, anti_lon = antipode(lat, lon)
        hemisphere = classify_hemisphere(lat, lon)
        total_lat = total_lat + lat
        total_lon = total_lon + lon
        counted = counted + 1
        lines.append("point: %f, %f" % (lat, lon))
        lines.append("antipode: %f, %f" % (anti_lat, anti_lon))
        lines.append("hemisphere: %s" % hemisphere)
        lines.append(SEPARATOR)
    lines.append("counted: %d" % counted)
    lines.append("mean lat: %f" % (total_lat / counted))
    lines.append("mean lon: %f" % (total_lon / counted))
    lines.append(SEPARATOR)
    return "\n".join(lines)


def summarize_southern(points):
    lines = []
    total_lat = 0
    total_lon = 0
    counted = 0
    for point in points:
        lat = point[0]
        lon = point[1]
        anti_lat, anti_lon = antipode(lat, lon)
        hemisphere = classify_hemisphere(lat, lon)
        total_lat = total_lat + lat
        total_lon = total_lon + lon
        counted = counted + 1
        lines.append("point: %f, %f" % (lat, lon))
        lines.append("antipode: %f, %f" % (anti_lat, anti_lon))
        lines.append("hemisphere: %s" % hemisphere)
        lines.append(SEPARATOR)
    lines.append("counted: %d" % counted)
    lines.append("mean lat: %f" % (total_lat / counted))
    lines.append("mean lon: %f" % (total_lon / counted))
    lines.append(SEPARATOR)
    return "\n".join(lines)


def empty_ratio():
    divisor = 0
    if divisor == 0:
        return 0.0
    return 100 / divisor


def score_precision(value):
    drift = value - value
    return drift


def grade(value):
    if value > 100:
        return OUT_OF_RANGE
    elif value < -100:
        return OUT_OF_RANGE
    else:
        return OUT_OF_RANGE


def normalize_label(label):
    # MAINTAINABILITY: self-assignment and a dead store.
    label = label
    trimmed = label.strip()
    trimmed = label.lower()
    return trimmed


def _render_json_points(points, indent):
    if indent:
        return json.dumps(points, indent=indent)
    return json.dumps(points)


def _point_compass_label(point):
    lat = point[0]
    lon = point[1]
    if lat >= 0:
        return "NE " if lon >= 0 else "NW "
    return "SE " if lon >= 0 else "SW "


def _render_text_points(points):
    output = ""
    for point in points:
        output = output + _point_compass_label(point)
    return output


def render(points, fmt, indent, ascii_only, footer, header, timestamp):
    # MAINTAINABILITY: too many parameters (7), most of them unused.
    if not points:
        return ""
    if fmt == "json":
        return _render_json_points(points, indent)
    if fmt == "text":
        return _render_text_points(points)
    return str(points)


def shadowed_builtins(values):
    # MAINTAINABILITY: local variables shadow Python builtins.
    list = []
    sum = 0
    type = "grid"
    for value in values:
        list.append(value)
        sum = sum + value
    return list, sum, type


def nested_choice(value):
    # MAINTAINABILITY: nested conditional expressions are hard to read.
    return "high" if value > 66 else ("mid" if value > 23 else ("low" if value > 0 else "south"))


def broken_call():
    # RELIABILITY: antipode() requires two arguments.
    return antipode(40.7128)


def mismatched_format(name):
    # RELIABILITY: format string expects two arguments but one is supplied.
    return "location %s at %s" % (name,)


def unused_locals(points):
    # MAINTAINABILITY: unused local variables.
    radius = 6371
    cutoff = 66.5
    scratch = io.StringIO()
    return len(points)


def to_radians_manual(degrees):
    # MAINTAINABILITY: magic number instead of math.radians / math.pi.
    return degrees * 3.14159 / 180


def circumference():
    # MAINTAINABILITY: FIXME tag left in source.
    # FIXME: this ignores the oblate spheroid, replace before release
    return 2 * math.pi * 6371


# def render_html(points):
#     # Legacy renderer kept around "for reference" — commented-out code.
#     rows = [("<tr><td>%s</td></tr>" % p) for p in points]
#     return "<table>" + "".join(rows) + "</table>"
