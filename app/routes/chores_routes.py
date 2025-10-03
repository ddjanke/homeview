from flask import Blueprint, render_template, jsonify, request
from app.services.google_sheets import GoogleSheetsService
from app.models.chores import Chore
from app import db
from datetime import datetime

chores_bp = Blueprint("chores", __name__)


@chores_bp.route("/")
def chores_view():
    """Display the chores view."""
    return render_template("chores_content.html")


@chores_bp.route("/api/chores")
def get_chores():
    """Get all chores."""
    try:
        chores = Chore.query.all()
        return jsonify(
            {"success": True, "chores": [chore.to_dict() for chore in chores]}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@chores_bp.route("/api/chores/sync", methods=["POST"])
def sync_chores():
    """Sync chores from Google Sheets."""
    try:
        sheets_service = GoogleSheetsService()
        chores = sheets_service.sync_chores_from_sheets()

        return jsonify(
            {
                "success": True,
                "chores": [chore.to_dict() for chore in chores],
                "message": f"Synced {len(chores)} chores from Google Sheets",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@chores_bp.route("/api/chores/<int:chore_id>/complete", methods=["POST"])
def complete_chore(chore_id):
    """Mark a chore as complete."""
    try:
        chore = Chore.query.get(chore_id)
        if not chore:
            return jsonify({"success": False, "error": "Chore not found"}), 404

        chore.mark_completed()

        return jsonify({"success": True, "chore": chore.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@chores_bp.route("/api/chores/reset", methods=["POST"])
def reset_chores():
    """Reset chore completion status for the day."""
    try:
        # Get chores that need to be reset based on their frequency and day
        today = datetime.now().weekday()  # 0 = Monday, 6 = Sunday
        day_names = ["M", "Tu", "W", "Th", "F", "Sa", "Su"]
        today_name = day_names[today]

        chores_to_reset = Chore.query.filter(
            (Chore.frequency == "daily")
            | ((Chore.frequency == "weekly") & (Chore.day_of_week == today_name))
            | ((Chore.frequency == "monthly") & (Chore.day_of_week == today_name))
        ).all()

        for chore in chores_to_reset:
            chore.reset_completion()

        return jsonify(
            {
                "success": True,
                "message": f"Reset {len(chores_to_reset)} chores",
                "chores": [chore.to_dict() for chore in chores_to_reset],
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
