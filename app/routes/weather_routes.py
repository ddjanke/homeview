from flask import Blueprint, render_template, jsonify
from app.services.weather_api import WeatherService

weather_bp = Blueprint("weather", __name__)


@weather_bp.route("/")
def weather_view():
    """Display the weather view."""
    return render_template("weather_content.html")


@weather_bp.route("/api/current")
def get_current_weather():
    """Get current weather conditions."""
    try:
        weather_service = WeatherService()
        current_weather = weather_service.get_current_weather()

        if current_weather is None:
            return (
                jsonify({"success": False, "error": "No weather data available"}),
                500,
            )

        return jsonify({"success": True, "weather": current_weather})
    except Exception as e:
        print(f"Weather API error: {e}")
        import traceback

        traceback.print_exc()
        return (
            jsonify({"success": False, "error": f"Weather service error: {str(e)}"}),
            500,
        )


@weather_bp.route("/api/forecast")
def get_forecast():
    """Get weather forecast."""
    try:
        weather_service = WeatherService()
        forecast = weather_service.get_forecast()

        return jsonify({"success": True, "forecast": forecast})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@weather_bp.route("/api/alerts")
def get_weather_alerts():
    """Get weather alerts."""
    try:
        weather_service = WeatherService()
        alerts = weather_service.get_weather_alerts()

        return jsonify({"success": True, "alerts": alerts})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@weather_bp.route("/api/all")
def get_all_weather():
    """Get all weather data (current, forecast, alerts)."""
    try:
        weather_service = WeatherService()
        weather_data = weather_service.get_all_weather_data()

        return jsonify({"success": True, "weather": weather_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
