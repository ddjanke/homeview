from app import db
from datetime import datetime


class Todo(db.Model):
    __tablename__ = "todos"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.Integer, nullable=False, default=5)  # 1-10 scale
    assigned_to = db.Column(db.String(50))  # Person assigned to the todo
    due_date = db.Column(db.Date)
    completed = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    google_sheet_row = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority,
            "assigned_to": self.assigned_to,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed": self.completed,
            "created_date": self.created_date.isoformat(),
            "google_sheet_row": self.google_sheet_row,
        }

    def mark_completed(self):
        self.completed = True
        db.session.commit()

    def __repr__(self):
        return f"<Todo {self.title} - Priority {self.priority}>"
