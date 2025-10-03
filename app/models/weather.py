from app import db
from datetime import datetime
import json


class WeatherData(db.Model):
    __tablename__ = "weather_data"

    id = db.Column(db.Integer, primary_key=True)
    current_data = db.Column(db.Text)  # JSON string of current weather
    forecast_data = db.Column(db.Text)  # JSON string of forecast
    alerts_data = db.Column(db.Text)  # JSON string of alerts
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def set_current_data(self, data):
        self.current_data = json.dumps(data)
        self.last_updated = datetime.utcnow()

    def set_forecast_data(self, data):
        self.forecast_data = json.dumps(data)
        self.last_updated = datetime.utcnow()

    def set_alerts_data(self, data):
        self.alerts_data = json.dumps(data)
        self.last_updated = datetime.utcnow()

    def get_current_data(self):
        return json.loads(self.current_data) if self.current_data else None

    def get_forecast_data(self):
        return json.loads(self.forecast_data) if self.forecast_data else None

    def get_alerts_data(self):
        return json.loads(self.alerts_data) if self.alerts_data else None

    def to_dict(self):
        return {
            "current": self.get_current_data(),
            "forecast": self.get_forecast_data(),
            "alerts": self.get_alerts_data(),
            "last_updated": self.last_updated.isoformat(),
        }

    def __repr__(self):
        return f"<WeatherData {self.last_updated}>"
