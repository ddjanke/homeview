from app import db
from datetime import datetime


class CalendarEvent(db.Model):
    __tablename__ = "calendar_events"

    id = db.Column(db.String(100), primary_key=True)  # Google event ID
    title = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String(50), default="personal")
    description = db.Column(db.Text)
    recurring = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "category": self.category,
            "description": self.description,
            "recurring": self.recurring,
            "last_updated": self.last_updated.isoformat(),
        }

    def __repr__(self):
        return f"<CalendarEvent {self.title}>"
