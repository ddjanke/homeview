from googleapiclient.discovery import build
from .auth import GoogleAuthService
from .google_drive import GoogleDriveService
from app.models.chores import Chore
from app.models.todos import Todo
from app import db
from datetime import datetime
from config import Config
import os


class GoogleSheetsService:
    def __init__(self):
        self.auth_service = GoogleAuthService()
        self.service = None
        self.chores_sheet_id = None
        self.todos_sheet_id = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize the Google Sheets service."""
        try:
            creds = self.auth_service.get_credentials()
            self.service = build("sheets", "v4", credentials=creds)
            # Use the same spreadsheet ID for both chores and todos
            self.chores_sheet_id = Config.GOOGLE_SHEETS_ID
            self.todos_sheet_id = Config.GOOGLE_SHEETS_ID
        except Exception as e:
            print(f"Error initializing Google Sheets service: {e}")
            self.service = None

    def sync_chores_from_sheets(self):
        """Sync chores from Google Sheets to local database."""
        if not self.service or not self.chores_sheet_id:
            return []

        try:
            # Read chores from Google Sheets
            range_name = f"{Config.CHORES_SHEET_NAME}!A:F"  # Name, Assigned To, Frequency, Day, Icon Name
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=self.chores_sheet_id, range=range_name)
                .execute()
            )

            values = result.get("values", [])
            if not values:
                return []

            # Skip header row
            chores_data = values[1:] if len(values) > 1 else []

            # Store existing completion status before clearing
            existing_chores = Chore.query.all()
            completion_status = {}
            for chore in existing_chores:
                completion_status[chore.name] = {
                    "completed": chore.completed,
                    "completed_date": chore.completed_date,
                }

            # Clear existing chores
            Chore.query.delete()

            # Add new chores
            for i, row in enumerate(chores_data):
                if len(row) >= 4:  # Ensure we have enough columns
                    chore_name = row[0]
                    chore = Chore(
                        name=chore_name,
                        assigned_to=row[1],
                        frequency=row[2],
                        day_of_week=row[3] if len(row) > 3 else None,
                        icon_name=row[4] if len(row) > 4 else None,
                        google_sheet_row=i
                        + 2,  # +2 because of header and 0-based indexing
                    )

                    # Restore completion status if chore existed before
                    if chore_name in completion_status:
                        chore.completed = completion_status[chore_name]["completed"]
                        chore.completed_date = completion_status[chore_name][
                            "completed_date"
                        ]

                    db.session.add(chore)

            db.session.commit()

            # Download icons from Google Drive after syncing chores
            self._sync_icons_from_drive()

            return Chore.query.all()

        except Exception as e:
            print(f"Error syncing chores from sheets: {e}")
            db.session.rollback()
            return Chore.query.all()

    def sync_todos_from_sheets(self):
        """Sync todos from Google Sheets to local database."""
        if not self.service or not self.todos_sheet_id:
            return []

        try:
            # Read todos from Google Sheets
            range_name = f"{Config.TODOS_SHEET_NAME}!A:E"  # Title, Priority, Assigned To, Due Date
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=self.todos_sheet_id, range=range_name)
                .execute()
            )

            values = result.get("values", [])
            if not values:
                return []

            # Skip header row
            todos_data = values[1:] if len(values) > 1 else []

            # Store existing completion status before clearing
            existing_todos = Todo.query.all()
            completion_status = {}
            for todo in existing_todos:
                completion_status[todo.title] = {
                    "completed": todo.completed,
                    "completed_date": todo.completed_date,
                }

            # Clear existing todos
            Todo.query.delete()

            # Add new todos
            for i, row in enumerate(todos_data):
                if len(row) >= 2:  # Ensure we have enough columns (title and priority)
                    due_date = None
                    if len(row) > 3 and row[3]:
                        try:
                            due_date = datetime.strptime(row[3], "%Y-%m-%d").date()
                        except ValueError:
                            pass

                    todo_title = row[0]
                    todo = Todo(
                        title=todo_title,
                        priority=(
                            int(row[1]) if len(row) > 1 and row[1].isdigit() else 5
                        ),
                        assigned_to=row[2] if len(row) > 2 else None,
                        due_date=due_date,
                        google_sheet_row=i
                        + 2,  # +2 because of header and 0-based indexing
                    )

                    # Restore completion status if todo existed before
                    if todo_title in completion_status:
                        todo.completed = completion_status[todo_title]["completed"]
                        todo.completed_date = completion_status[todo_title][
                            "completed_date"
                        ]

                    db.session.add(todo)

            db.session.commit()
            return Todo.query.all()

        except Exception as e:
            print(f"Error syncing todos from sheets: {e}")
            db.session.rollback()
            return Todo.query.all()

    def _sync_icons_from_drive(self):
        """Download icons from Google Drive to local icons directory."""
        try:
            drive_service = GoogleDriveService()
            icons_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "static", "icons", "chores"
            )
            drive_service.sync_icons_to_local(icons_dir)
        except Exception as e:
            print(f"Error syncing icons from Drive: {e}")
