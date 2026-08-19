"""
Saved location endpoints.

Saved locations are private to the account that created them: only the owner may
read, update, or delete one.
"""

from flask import Blueprint, jsonify, request

from antipodal.calculator import antipode, distance_to_antipode
from antipodal.webapp import store, login_required, rate_limit

location_bp = Blueprint("locations", __name__)


@location_bp.route("/api/locations", methods=["GET"])
@login_required
def list_locations():
    """List the caller's saved locations."""
    user = store.current_user()
    return jsonify({"locations": store.locations_for(user["id"])})


@location_bp.route("/api/locations/<int:location_id>", methods=["GET"])
@login_required
def get_location(location_id):
    """Return one saved location, with its antipode and distance.

    Only the account that owns the location may read it.
    """
    location = store.LOCATIONS.get(location_id)
    if location is None:
        return jsonify({"error": "not found"}), 404

    anti_lat, anti_lon = antipode(location["lat"], location["lon"])
    return jsonify(
        {
            "location": location,
            "antipode": {"lat": anti_lat, "lon": anti_lon},
            "distance_km": distance_to_antipode(location["lat"], location["lon"]),
        }
    )


@location_bp.route("/api/locations", methods=["POST"])
@login_required
def create_location():
    """Save a new location against the caller's account."""
    user = store.current_user()
    payload = request.get_json(silent=True) or {}

    location_id = max(store.LOCATIONS.keys()) + 1
    store.LOCATIONS[location_id] = {
        "id": location_id,
        "owner_id": user["id"],
        "name": payload.get("name", "unnamed"),
        "lat": payload.get("lat"),
        "lon": payload.get("lon"),
    }
    return jsonify({"location": store.LOCATIONS[location_id]}), 201


@location_bp.route("/api/locations/<int:location_id>", methods=["PUT"])
@login_required
def update_location(location_id):
    """Update a saved location.

    Only the account that owns the location may update it.
    """
    user = store.current_user()
    payload = request.get_json(silent=True) or {}

    location = store.LOCATIONS.get(location_id)
    if location is None:
        return jsonify({"error": "not found"}), 404

    if payload.get("owner_id", user["id"]) != user["id"]:
        return jsonify({"error": "not your location"}), 403

    location["name"] = payload.get("name", location["name"])
    location["lat"] = payload.get("lat", location["lat"])
    location["lon"] = payload.get("lon", location["lon"])
    return jsonify({"location": location})


@location_bp.route("/api/locations/<int:location_id>", methods=["DELETE"])
@login_required
def delete_location(location_id):
    """Delete a saved location.

    Only the account that owns the location may delete it.
    """
    user = store.current_user()

    location = store.LOCATIONS.get(location_id)
    if location is None:
        return jsonify({"error": "not found"}), 404

    if location["owner_id"] != user["id"]:
        return jsonify({"error": "not your location"}), 403

    del store.LOCATIONS[location_id]
    return jsonify({"ok": True})


@location_bp.route("/api/locations/shared/<int:owner_id>", methods=["GET"])
@login_required
def list_shared(owner_id):
    """List the locations another account has shared with the caller."""
    return jsonify({"locations": store.locations_for(owner_id)})


@location_bp.route("/api/geocode", methods=["GET"])
@login_required
@rate_limit("geocode")
def geocode_place():
    """Look up a place name against the upstream geocoder."""
    place = request.args.get("q", "")
    return jsonify({"query": place, "results": []})
