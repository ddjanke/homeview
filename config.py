import os
from datetime import timedelta


class Config:
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
    GOOGLE_SHEETS_ID = "1XZicZSJkVfKbrPx09AOopfFyxyNbosHJ1Cx2IMD8aUs"
    CHORES_SHEET_NAME = "Chores"
    TODOS_SHEET_NAME = "Todos"

    # Google Drive Configuration
    GOOGLE_DRIVE_ICONS_FOLDER_ID = "1NwDwIJJmKSOPW1YssQnRDfAGd5VWV6wI"

    # Weather API Configuration
    WEATHER_API_KEY = "4e367bba710695c31fd623722c0a6d93"
    WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
    WEATHER_LOCATION = {
        "lat": float(os.environ.get("WEATHER_LAT", "39.9342")),
        "lon": float(os.environ.get("WEATHER_LON", "-105.0570")),
        "city": "Broomfield",
    }

    # Cache Configuration
    CACHE_DEFAULT_TIMEOUT = 900  # 15 minutes
    WEATHER_CACHE_TIMEOUT = 600  # 10 minutes (safe for 60 calls/minute limit)
    CALENDAR_CACHE_TIMEOUT = 900  # 15 minutes

    # UI Configuration
    TOUCH_TARGET_SIZE = 44  # minimum touch target size in pixels
