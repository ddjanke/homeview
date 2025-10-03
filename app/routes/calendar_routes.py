from flask import Blueprint, render_template, jsonify
from app.services.google_calendar import GoogleCalendarService
from datetime import datetime, timedelta

calendar_bp = Blueprint("calendar", __name__)


@calendar_bp.route("/")
def calendar_view():
    """Display the calendar view."""
    return render_template("calendar_content.html")


@calendar_bp.route("/api/events")
def get_events():
    """Get calendar events for the current week."""
    try:
        calendar_service = GoogleCalendarService()

        # Get current week
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=7)

        events = calendar_service.get_events_from_all_calendars(
            start_of_week, end_of_week
        )

        return jsonify(
            {
                "success": True,
                "events": events,
                "week_start": start_of_week.isoformat(),
                "week_end": end_of_week.isoformat(),
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@calendar_bp.route("/api/events/<int:week_offset>")
def get_events_by_week(week_offset):
    """Get calendar events for a specific week offset."""
    try:
        calendar_service = GoogleCalendarService()

        # Calculate week based on offset
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_week = (
            today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
        )
        end_of_week = start_of_week + timedelta(days=7)

        events = calendar_service.get_events_from_all_calendars(
            start_of_week, end_of_week
        )

        return jsonify(
            {
                "success": True,
                "events": events,
                "week_start": start_of_week.isoformat(),
                "week_end": end_of_week.isoformat(),
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@calendar_bp.route("/api/calendars")
def get_calendars():
    """Get list of accessible calendars."""
    try:
        calendar_service = GoogleCalendarService()
        calendars = calendar_service.get_calendars()

        return jsonify({"success": True, "calendars": calendars})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
