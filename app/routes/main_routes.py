from flask import Blueprint, render_template, jsonify, redirect, url_for
from app import db
from app.models import CalendarEvent, Chore, Todo, WeatherData
from app.services.auth import GoogleAuthService

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Display the main dashboard or login page."""
    auth_service = GoogleAuthService()

    if auth_service.is_authenticated():
        return render_template("index.html")
    else:
        return render_template("login.html")


@main_bp.route("/dashboard")
def dashboard():
    """Display the main dashboard (requires authentication)."""
    auth_service = GoogleAuthService()

    if not auth_service.is_authenticated():
        return redirect(url_for("main.index"))

    return render_template("index.html")


@main_bp.route("/api/health")
def health_check():
    """Health check endpoint for system monitoring."""
    try:
        # Check database connection
        from sqlalchemy import text

        db.session.execute(text("SELECT 1"))

        # Get basic stats
        stats = {
            "calendar_events": CalendarEvent.query.count(),
            "chores": Chore.query.count(),
            "todos": Todo.query.count(),
            "weather_data": WeatherData.query.count(),
        }

        return jsonify({"status": "Online", "database": "Connected", "stats": stats})
    except Exception as e:
        return (
            jsonify({"status": "Offline", "database": "Disconnected", "error": str(e)}),
            500,
        )
