import requests
from datetime import datetime
from app.models.weather import WeatherData
from app import db
from config import Config


class WeatherService:
    def __init__(self):
        self.api_key = Config.WEATHER_API_KEY
        self.base_url = Config.WEATHER_BASE_URL
        self.location = Config.WEATHER_LOCATION

    def get_current_weather(self):
        """Get current weather conditions with today's high/low."""
        try:
            # Get current weather
            url = f"{self.base_url}/weather"
            params = {
                "lat": self.location["lat"],
                "lon": self.location["lon"],
                "appid": self.api_key,
                "units": "imperial",  # Use Fahrenheit
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Get today's forecast for high/low
            forecast_url = f"{self.base_url}/forecast"
            forecast_response = requests.get(forecast_url, params=params, timeout=10)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            # Calculate today's high/low from forecast
            today = datetime.now().strftime("%Y-%m-%d")
            today_temps = []
            
            for item in forecast_data["list"]:
                item_date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
                if item_date == today:
                    today_temps.append(item["main"]["temp"])

            current_weather = {
                "temp": round(data["main"]["temp"]),
                "description": data["weather"][0]["description"].title(),
                "main": data["weather"][0]["main"],
                "temperature": round(data["main"]["temp"]),
                "condition": data["weather"][0]["main"].lower(),
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "icon": self._get_weather_icon(data["weather"][0]["icon"]),
                "high": round(max(today_temps)) if today_temps else round(data["main"]["temp"]),
                "low": round(min(today_temps)) if today_temps else round(data["main"]["temp"]),
                "last_updated": datetime.utcnow().isoformat(),
            }

            # Cache the data
            self._cache_weather_data(current_weather, None, None)

            return current_weather

        except Exception as e:
            print(f"Error fetching current weather: {e}")
            return self._get_cached_weather()

    def get_forecast(self):
        """Get 5-day weather forecast."""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "lat": self.location["lat"],
                "lon": self.location["lon"],
                "appid": self.api_key,
                "units": "imperial",
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Process forecast data (every 3 hours, we want daily)
            forecast = []
            daily_data = {}

            for item in data["list"]:
                date_str = item["dt_txt"].split(" ")[0]
                if date_str not in daily_data:
                    daily_data[date_str] = {
                        "temps": [],
                        "conditions": [],
                        "precipitation": [],
                        "icons": [],
                    }

                daily_data[date_str]["temps"].append(item["main"]["temp"])
                daily_data[date_str]["conditions"].append(item["weather"][0]["main"])
                daily_data[date_str]["icons"].append(item["weather"][0]["icon"])
                if "rain" in item and "3h" in item["rain"]:
                    daily_data[date_str]["precipitation"].append(item["rain"]["3h"])
                elif "snow" in item and "3h" in item["snow"]:
                    daily_data[date_str]["precipitation"].append(item["snow"]["3h"])
                else:
                    daily_data[date_str]["precipitation"].append(0)

            # Convert to daily forecast
            for date_str, data in daily_data.items():
                # Get the most common condition and its corresponding icon
                most_common_condition = self._get_most_common(data["conditions"])
                # Find the best icon that matches the most common condition
                # Prefer daytime icons (ending with 'd') over night icons (ending with 'n')
                condition_icon = "partly-cloudy"  # default
                day_icons = []
                night_icons = []

                for i, condition in enumerate(data["conditions"]):
                    if condition == most_common_condition:
                        icon_code = data["icons"][i]
                        if icon_code.endswith("d"):
                            day_icons.append(icon_code)
                        elif icon_code.endswith("n"):
                            night_icons.append(icon_code)

                # Prefer daytime icons, fall back to night icons
                if day_icons:
                    condition_icon = self._get_weather_icon(day_icons[0])
                elif night_icons:
                    condition_icon = self._get_weather_icon(night_icons[0])

                # Map the condition to a more descriptive name based on the icon
                descriptive_condition = self._get_descriptive_condition(
                    most_common_condition, condition_icon
                )

                forecast.append(
                    {
                        "date": date_str,
                        "high": round(max(data["temps"])),
                        "low": round(min(data["temps"])),
                        "condition": descriptive_condition,
                        "icon": condition_icon,
                        "precipitation_chance": min(
                            100, sum(data["precipitation"]) * 10
                        ),  # Rough calculation
                    }
                )

            # Cache the data
            self._cache_weather_data(None, forecast, None)

            return forecast

        except Exception as e:
            print(f"Error fetching forecast: {e}")
            return self._get_cached_forecast()

    def get_weather_alerts(self):
        """Get weather alerts (if available)."""
        try:
            url = f"{self.base_url}/onecall"
            params = {
                "lat": self.location["lat"],
                "lon": self.location["lon"],
                "appid": self.api_key,
                "exclude": "minutely,hourly,daily",
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            alerts = data.get("alerts", [])

            processed_alerts = []
            for alert in alerts:
                processed_alerts.append(
                    {
                        "title": alert.get("event", "Weather Alert"),
                        "description": alert.get("description", ""),
                        "severity": alert.get("severity", "moderate"),
                        "expires": alert.get("expires", ""),
                    }
                )

            # Cache the data
            self._cache_weather_data(None, None, processed_alerts)

            return processed_alerts

        except Exception as e:
            print(f"Error fetching weather alerts: {e}")
            return self._get_cached_alerts()

    def get_all_weather_data(self):
        """Get all weather data (current, forecast, alerts)."""
        current = self.get_current_weather()
        forecast = self.get_forecast()
        alerts = self.get_weather_alerts()

        return {"current": current, "forecast": forecast, "alerts": alerts}

    def _cache_weather_data(self, current, forecast, alerts):
        """Cache weather data in database."""
        try:
            weather_data = WeatherData.query.first()
            if not weather_data:
                weather_data = WeatherData()
                db.session.add(weather_data)

            if current:
                weather_data.set_current_data(current)
            if forecast:
                weather_data.set_forecast_data(forecast)
            if alerts:
                weather_data.set_alerts_data(alerts)

            db.session.commit()

        except Exception as e:
            print(f"Error caching weather data: {e}")
            try:
                db.session.rollback()
            except:
                pass

    def _get_cached_weather(self):
        """Get cached weather data if still valid."""
        try:
            weather_data = WeatherData.query.first()
            if weather_data and weather_data.get_current_data():
                # Check if cache is still valid (within 10 minutes)
                cache_age = datetime.utcnow() - weather_data.last_updated
                if cache_age.total_seconds() < Config.WEATHER_CACHE_TIMEOUT:
                    return weather_data.get_current_data()
            return None
        except Exception:
            return None

    def _get_cached_forecast(self):
        """Get cached forecast data if still valid."""
        try:
            weather_data = WeatherData.query.first()
            if weather_data and weather_data.get_forecast_data():
                # Check if cache is still valid (within 10 minutes)
                cache_age = datetime.utcnow() - weather_data.last_updated
                if cache_age.total_seconds() < Config.WEATHER_CACHE_TIMEOUT:
                    return weather_data.get_forecast_data()
            return []
        except Exception:
            return []

    def _get_cached_alerts(self):
        """Get cached alerts data if still valid."""
        try:
            weather_data = WeatherData.query.first()
            if weather_data and weather_data.get_alerts_data():
                # Check if cache is still valid (within 10 minutes)
                cache_age = datetime.utcnow() - weather_data.last_updated
                if cache_age.total_seconds() < Config.WEATHER_CACHE_TIMEOUT:
                    return weather_data.get_alerts_data()
            return []
        except Exception:
            return []

    def _get_weather_icon(self, icon_code):
        """Convert OpenWeatherMap icon code to our icon name."""
        icon_mapping = {
            "01d": "sunny",
            "01n": "clear-night",
            "02d": "partly-cloudy",
            "02n": "partly-cloudy-night",
            "03d": "cloudy",
            "03n": "cloudy",
            "04d": "cloudy",
            "04n": "cloudy",
            "09d": "rainy",
            "09n": "rainy",
            "10d": "rainy",
            "10n": "rainy",
            "11d": "thunderstorm",
            "11n": "thunderstorm",
            "13d": "snowy",
            "13n": "snowy",
            "50d": "foggy",
            "50n": "foggy",
        }
        return icon_mapping.get(icon_code, "partly-cloudy")

    def _get_most_common(self, items):
        """Get the most common item in a list."""
        if not items:
            return "Clear"
        return max(set(items), key=items.count)

    def _get_descriptive_condition(self, condition, icon):
        """Get a more descriptive condition name based on the icon."""
        # Map generic conditions to more descriptive names based on icon
        if condition == "Clouds":
            if icon == "partly-cloudy":
                return "Partly Cloudy"
            elif icon == "cloudy":
                return "Cloudy"
            else:
                return "Partly Cloudy"  # Default for clouds
        elif condition == "Clear":
            if icon == "sunny":
                return "Sunny"
            elif icon == "clear-night":
                return "Clear"
            else:
                return "Clear"
        elif condition == "Rain":
            return "Rainy"
        elif condition == "Snow":
            return "Snowy"
        elif condition == "Thunderstorm":
            return "Thunderstorm"
        elif condition == "Fog":
            return "Foggy"
        else:
            return condition  # Return as-is for other conditions
