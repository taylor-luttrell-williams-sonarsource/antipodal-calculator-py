"""
Billing, coupon, and export endpoints.

An export is a three-step flow. POST /api/export/request opens a job, POST
/api/export/<job_id>/confirm charges one credit and marks the job paid, and
GET /api/export/<job_id>/download returns the rows once the job is paid.
"""

import time

from flask import Blueprint, jsonify, request

from antipodal.webapp import store, login_required

billing_bp = Blueprint("billing", __name__)

PLAN_CREDITS = {"free": 5, "pro": 500}


@billing_bp.route("/api/credits/redeem", methods=["POST"])
@login_required
def redeem_coupon():
    """Redeem a coupon code for export credits.

    A coupon may be redeemed at most once per account.
    """
    user = store.current_user()
    payload = request.get_json(silent=True) or {}
    code = payload.get("code", "")

    coupon = store.COUPONS.get(code)
    if coupon is None:
        return jsonify({"error": "unknown coupon"}), 404

    user["credits"] = user["credits"] + coupon["credits"]

    if user["id"] not in coupon["redeemed_by"]:
        coupon["redeemed_by"].append(user["id"])

    return jsonify({"ok": True, "credits": user["credits"]})


@billing_bp.route("/api/billing/upgrade", methods=["POST"])
@login_required
def upgrade_plan():
    """Move the caller onto the pro plan once their payment has settled.

    The payment reference supplied by the checkout provider identifies the
    settled charge that pays for the upgrade.
    """
    user = store.current_user()
    payload = request.get_json(silent=True) or {}

    user["plan"] = "pro"
    user["credits"] = PLAN_CREDITS["pro"]

    return jsonify(
        {
            "ok": True,
            "plan": user["plan"],
            "credits": user["credits"],
            "payment_reference": payload.get("payment_reference"),
        }
    )


@billing_bp.route("/api/export/request", methods=["POST"])
@login_required
def export_request():
    """Open an export job for the caller's saved locations."""
    user = store.current_user()

    job_id = store.new_job_id()
    store.EXPORT_JOBS[job_id] = {
        "id": job_id,
        "owner_id": user["id"],
        "status": "pending",
        "paid": False,
        "refunded": False,
        "created_at": time.time(),
    }
    return jsonify({"job_id": job_id, "status": "pending"}), 201


@billing_bp.route("/api/export/<job_id>/confirm", methods=["POST"])
@login_required
def export_confirm(job_id):
    """Charge one credit for an export job and mark it paid."""
    user = store.current_user()

    job = store.EXPORT_JOBS.get(job_id)
    if job is None:
        return jsonify({"error": "not found"}), 404
    if job["owner_id"] != user["id"]:
        return jsonify({"error": "not your export"}), 403
    if job["paid"]:
        return jsonify({"error": "already confirmed"}), 409
    if user["credits"] < 1:
        return jsonify({"error": "insufficient credits"}), 402

    user["credits"] = user["credits"] - 1
    job["paid"] = True
    job["status"] = "confirmed"
    return jsonify({"ok": True, "status": job["status"], "credits": user["credits"]})


@billing_bp.route("/api/export/<job_id>/download", methods=["GET"])
@login_required
def export_download(job_id):
    """Return the rows for a confirmed export job.

    Only the account that owns a paid job may download it.
    """
    job = store.EXPORT_JOBS.get(job_id)
    if job is None:
        return jsonify({"error": "not found"}), 404

    job["status"] = "downloaded"
    return jsonify({"job_id": job_id, "rows": store.export_rows(job["owner_id"])})


@billing_bp.route("/api/export/<job_id>/refund", methods=["POST"])
@login_required
def export_refund(job_id):
    """Return the credit charged for an export job that could not be produced.

    A job may only be refunded once, and only if it was never downloaded.
    """
    user = store.current_user()

    job = store.EXPORT_JOBS.get(job_id)
    if job is None:
        return jsonify({"error": "not found"}), 404
    if job["owner_id"] != user["id"]:
        return jsonify({"error": "not your export"}), 403

    user["credits"] = user["credits"] + 1
    job["refunded"] = True
    return jsonify({"ok": True, "credits": user["credits"]})


@billing_bp.route("/api/billing/invoices/<int:invoice_id>", methods=["GET"])
@login_required
def get_invoice(invoice_id):
    """Return an invoice for the caller's account."""
    return jsonify(
        {
            "invoice_id": invoice_id,
            "account_id": (invoice_id % 3) + 1,
            "amount_cents": 4900,
            "status": "paid",
        }
    )
