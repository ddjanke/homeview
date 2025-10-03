from datetime import datetime, timedelta
from googleapiclient.discovery import build
from .auth import GoogleAuthService
from app.models.calendar import CalendarEvent
from app import db
from config import Config


class GoogleCalendarService:
    def __init__(self):
        self.auth_service = GoogleAuthService()
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize the Google Calendar service."""
        try:
            creds = self.auth_service.get_credentials()
            self.service = build("calendar", "v3", credentials=creds)
        except Exception as e:
            print(f"Error initializing Google Calendar service: {e}")
            self.service = None

    def get_events(self, start_date=None, end_date=None):
        """Get events from Google Calendar and cache them locally."""
        if not self.service:
            return []

        try:
            # Default to current week if no dates provided
            if not start_date:
                start_date = datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            if not end_date:
                end_date = start_date + timedelta(days=7)

            # Format dates for Google Calendar API
            start_str = start_date.isoformat() + "Z"
            end_str = end_date.isoformat() + "Z"

            # Call the Calendar API
            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=start_str,
                    timeMax=end_str,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])

            # Add calendar info to each event
            for event in events:
                event["calendar_id"] = "primary"
                event["calendar_name"] = "Primary"
                event["calendar_color"] = "1"  # Default blue for primary

            # Cache events in local database
            self._cache_events(events)

            return events

        except Exception as e:
            print(f"Error fetching calendar events: {e}")
            return self._get_cached_events(start_date, end_date)

    def get_calendars(self):
        """Get list of all accessible calendars."""
        if not self.service:
            return []

        try:
            calendar_list = self.service.calendarList().list().execute()
            calendars = calendar_list.get("items", [])

            # Filter out calendars that are not accessible for reading events
            accessible_calendars = []
            for calendar in calendars:
                if calendar.get("accessRole") in ["owner", "reader", "writer"]:
                    accessible_calendars.append(
                        {
                            "id": calendar["id"],
                            "summary": calendar.get("summary", "Untitled Calendar"),
                            "color": calendar.get("colorId", "1"),
                            "selected": calendar.get("selected", True),
                        }
                    )

            return accessible_calendars
        except Exception as e:
            print(f"Error fetching calendar list: {e}")
            return []

    def get_events_from_all_calendars(self, start_date=None, end_date=None):
        """Get events from all accessible calendars."""
        if not self.service:
            return []

        try:
            # Default to current week if no dates provided
            if not start_date:
                start_date = datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            if not end_date:
                end_date = start_date + timedelta(days=7)

            # Format dates for Google Calendar API
            start_str = start_date.isoformat() + "Z"
            end_str = end_date.isoformat() + "Z"

            all_events = []

            # Get all accessible calendars
            calendars = self.get_calendars()
            calendar_ids = [cal["id"] for cal in calendars if cal["selected"]]

            # If no calendars found, fall back to primary
            if not calendar_ids:
                calendar_ids = ["primary"]

            # Fetch events from each calendar
            for calendar_id in calendar_ids:
                try:
                    events_result = (
                        self.service.events()
                        .list(
                            calendarId=calendar_id,
                            timeMin=start_str,
                            timeMax=end_str,
                            singleEvents=True,
                            orderBy="startTime",
                        )
                        .execute()
                    )

                    events = events_result.get("items", [])
                    # Add calendar info to each event
                    for event in events:
                        event["calendar_id"] = calendar_id
                        # Find calendar name and color
                        calendar_name = "Primary"
                        calendar_color = "1"  # Default blue
                        if calendar_id != "primary":
                            for cal in calendars:
                                if cal["id"] == calendar_id:
                                    calendar_name = cal["summary"]
                                    calendar_color = cal["color"]
                                    break
                        event["calendar_name"] = calendar_name
                        event["calendar_color"] = calendar_color

                    all_events.extend(events)
                except Exception as e:
                    print(f"Error fetching events from calendar {calendar_id}: {e}")
                    continue

            # Sort all events by start time
            all_events.sort(
                key=lambda x: x.get("start", {}).get(
                    "dateTime", x.get("start", {}).get("date", "")
                )
            )

            # Cache events in local database
            self._cache_events(all_events)

            return all_events

        except Exception as e:
            print(f"Error fetching calendar events: {e}")
            return self._get_cached_events(start_date, end_date)

    def _cache_events(self, events):
        """Cache events in local database."""
        try:
            for event in events:
                event_id = event.get("id")
                if not event_id:
                    continue

                # Check if event already exists
                existing_event = CalendarEvent.query.get(event_id)

                # Parse start and end times
                start_time = self._parse_datetime(event.get("start", {}))
                end_time = self._parse_datetime(event.get("end", {}))

                if not start_time or not end_time:
                    continue

                event_data = {
                    "id": event_id,
                    "title": event.get("summary", "No Title"),
                    "start_time": start_time,
                    "end_time": end_time,
                    "category": self._get_category(event),
                    "description": event.get("description", ""),
                    "recurring": "recurrence" in event,
                    "last_updated": datetime.utcnow(),
                }

                if existing_event:
                    # Update existing event
                    for key, value in event_data.items():
                        setattr(existing_event, key, value)
                else:
                    # Create new event
                    new_event = CalendarEvent(**event_data)
                    db.session.add(new_event)

            db.session.commit()

        except Exception as e:
            print(f"Error caching events: {e}")
            db.session.rollback()

    def _get_cached_events(self, start_date, end_date):
        """Get cached events from local database."""
        try:
            events = CalendarEvent.query.filter(
                CalendarEvent.start_time >= start_date,
                CalendarEvent.start_time <= end_date,
            ).all()

            return [event.to_dict() for event in events]

        except Exception as e:
            print(f"Error getting cached events: {e}")
            return []

    def _parse_datetime(self, datetime_obj):
        """Parse Google Calendar datetime object."""
        try:
            if "dateTime" in datetime_obj:
                return datetime.fromisoformat(
                    datetime_obj["dateTime"].replace("Z", "+00:00")
                )
            elif "date" in datetime_obj:
                return datetime.fromisoformat(datetime_obj["date"])
            return None
        except Exception:
            return None

    def _get_category(self, event):
        """Determine event category based on event data."""
        # Simple categorization - can be enhanced
        title = event.get("summary", "").lower()
        if any(word in title for word in ["work", "meeting", "office"]):
            return "work"
        elif any(word in title for word in ["family", "kids", "child"]):
            return "family"
        else:
            return "personal"
