import os
import json
from datetime import timedelta


def load_app_config():
    """Load application configuration from credentials file."""
    config_file = "credentials/app_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load app config: {e}")
    return {}


class Config:
    # Load app configuration from credentials file
    _app_config = load_app_config()

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///homeview.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google API Configuration
    GOOGLE_CREDENTIALS_FILE = "credentials/google_credentials.json"
    GOOGLE_SCOPES = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    GOOGLE_CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID") or "primary"

    # Google Sheets Configuration
    GOOGLE_SHEETS_ID = (
        _app_config.get("google_sheets_id")
        or os.environ.get("GOOGLE_SHEETS_ID")
        or "your-sheets-id-here"
    )
    CHORES_SHEET_NAME = "Chores"
    TODOS_SHEET_NAME = "Todos"

    # Google Drive Configuration
    GOOGLE_DRIVE_ICONS_FOLDER_ID = (
        _app_config.get("google_drive_icons_folder_id")
        or os.environ.get("GOOGLE_DRIVE_ICONS_FOLDER_ID")
        or "your-icons-folder-id-here"
    )

    # Weather API Configuration
    WEATHER_API_KEY = (
        _app_config.get("weather_api_key")
        or os.environ.get("WEATHER_API_KEY")
        or "your-weather-api-key-here"
    )
    WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

    # Weather location from config file or environment variables
    _weather_location = _app_config.get("weather_location", {})
    WEATHER_LOCATION = {
        "lat": float(
            _weather_location.get("lat", os.environ.get("WEATHER_LAT", "39.9342"))
        ),
        "lon": float(
            _weather_location.get("lon", os.environ.get("WEATHER_LON", "-105.0570"))
        ),
        "city": _weather_location.get(
            "city", os.environ.get("WEATHER_CITY", "Broomfield")
        ),
    }

    # Cache Configuration
    CACHE_DEFAULT_TIMEOUT = 900  # 15 minutes
    WEATHER_CACHE_TIMEOUT = 600  # 10 minutes (safe for 60 calls/minute limit)
    CALENDAR_CACHE_TIMEOUT = 900  # 15 minutes

    # UI Configuration
    TOUCH_TARGET_SIZE = 44  # minimum touch target size in pixels
