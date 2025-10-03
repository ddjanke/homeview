import os
from datetime import timedelta

# Raspberry Pi Optimized Configuration
# This configuration is optimized for Raspberry Pi Zero W performance


class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get("SECRET_KEY") or "pi-secret-key-change-in-production"
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Database Configuration - Using SQLite for Pi Zero W
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "sqlite:///instance/homeview.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Optimized for Pi Zero W - reduce database operations
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Google API Configuration
    GOOGLE_CREDENTIALS_FILE = "credentials/google_credentials.json"
    GOOGLE_SCOPES = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    GOOGLE_CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID") or "primary"

    # Google Sheets Configuration
    # TODO: Replace with your actual Google Sheets ID
    GOOGLE_SHEETS_ID = (
        os.environ.get("GOOGLE_SHEETS_ID") or "YOUR_GOOGLE_SHEETS_ID_HERE"
    )
    CHORES_SHEET_NAME = "Chores"
    TODOS_SHEET_NAME = "Todos"

    # Google Drive Configuration
    # TODO: Replace with your actual Google Drive folder ID
    GOOGLE_DRIVE_ICONS_FOLDER_ID = (
        os.environ.get("GOOGLE_DRIVE_ICONS_FOLDER_ID")
        or "YOUR_GOOGLE_DRIVE_FOLDER_ID_HERE"
    )

    # Weather API Configuration
    # TODO: Get your free API key from https://openweathermap.org/api
    WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY") or "YOUR_WEATHER_API_KEY_HERE"
    WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

    # TODO: Set your location coordinates
    WEATHER_LOCATION = {
        "lat": float(os.environ.get("WEATHER_LAT", "39.9342")),  # Broomfield, CO
        "lon": float(os.environ.get("WEATHER_LON", "-105.0570")),
        "city": os.environ.get("WEATHER_CITY", "Broomfield"),
    }

    # Cache Configuration - Optimized for Pi Zero W
    CACHE_DEFAULT_TIMEOUT = 1800  # 30 minutes (longer for Pi Zero W)
    WEATHER_CACHE_TIMEOUT = 1800  # 30 minutes (safe for API limits)
    CALENDAR_CACHE_TIMEOUT = 1800  # 30 minutes

    # Reduced cache timeouts for better responsiveness
    CHORES_CACHE_TIMEOUT = 900  # 15 minutes
    TODOS_CACHE_TIMEOUT = 900  # 15 minutes

    # UI Configuration - Optimized for touch screens
    TOUCH_TARGET_SIZE = 48  # Larger touch targets for Pi Zero W
    TOUCH_FRIENDLY = True  # Enable touch-friendly UI features

    # Performance optimizations for Pi Zero W
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache for static files

    # Disable debug mode for production
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    # Pi-specific optimizations
    PI_OPTIMIZATIONS = True
    REDUCE_LOGGING = True  # Reduce log verbosity for Pi Zero W




