from app import db
from datetime import datetime


class Chore(db.Model):
    __tablename__ = "chores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    assigned_to = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly
    day_of_week = db.Column(db.String(10))  # Su, M, Tu, W, Th, F, Sa
    icon_name = db.Column(db.String(100))  # Name of icon file (without extension)
    completed = db.Column(db.Boolean, default=False)
    completed_date = db.Column(db.DateTime)
    last_reset = db.Column(db.DateTime, default=datetime.utcnow)
    google_sheet_row = db.Column(db.Integer)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "assigned_to": self.assigned_to,
            "frequency": self.frequency,
            "day_of_week": self.day_of_week,
            "icon_name": self.icon_name,
            "completed": self.completed,
            "completed_date": (
                self.completed_date.isoformat() if self.completed_date else None
            ),
            "last_reset": self.last_reset.isoformat(),
            "google_sheet_row": self.google_sheet_row,
            "created_date": self.created_date.isoformat(),
        }

    def mark_completed(self):
        self.completed = True
        self.completed_date = datetime.utcnow()
        db.session.commit()

    def reset_completion(self):
        self.completed = False
        self.completed_date = None
        self.last_reset = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f"<Chore {self.name} - {self.assigned_to}>"
