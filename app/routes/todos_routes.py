from flask import Blueprint, render_template, jsonify, request
from app.services.google_sheets import GoogleSheetsService
from app.models.todos import Todo
from app import db
from datetime import datetime

todos_bp = Blueprint("todos", __name__)


@todos_bp.route("/")
def todos_view():
    """Display the todos view."""
    return render_template("todos_content.html")


@todos_bp.route("/api/todos")
def get_todos():
    """Get all todos, sorted by priority."""
    try:
        todos = Todo.query.order_by(Todo.priority.desc(), Todo.created_date.asc()).all()
        return jsonify({"success": True, "todos": [todo.to_dict() for todo in todos]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@todos_bp.route("/api/todos/sync", methods=["POST"])
def sync_todos():
    """Sync todos from Google Sheets."""
    try:
        sheets_service = GoogleSheetsService()
        todos = sheets_service.sync_todos_from_sheets()

        return jsonify(
            {
                "success": True,
                "todos": [todo.to_dict() for todo in todos],
                "message": f"Synced {len(todos)} todos from Google Sheets",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@todos_bp.route("/api/todos/<int:todo_id>/complete", methods=["POST"])
def complete_todo(todo_id):
    """Mark a todo as complete."""
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return jsonify({"success": False, "error": "Todo not found"}), 404

        todo.mark_completed()

        return jsonify({"success": True, "todo": todo.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@todos_bp.route("/api/todos", methods=["POST"])
def create_todo():
    """Create a new todo."""
    try:
        data = request.get_json()

        todo = Todo(
            title=data.get("title", ""),
            description=data.get("description", ""),
            priority=int(data.get("priority", 5)),
            due_date=(
                datetime.strptime(data["due_date"], "%Y-%m-%d").date()
                if data.get("due_date")
                else None
            ),
        )

        db.session.add(todo)
        db.session.commit()

        return jsonify({"success": True, "todo": todo.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@todos_bp.route("/api/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    """Update a todo."""
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return jsonify({"success": False, "error": "Todo not found"}), 404

        data = request.get_json()

        if "title" in data:
            todo.title = data["title"]
        if "description" in data:
            todo.description = data["description"]
        if "priority" in data:
            todo.priority = int(data["priority"])
        if "due_date" in data:
            todo.due_date = (
                datetime.strptime(data["due_date"], "%Y-%m-%d").date()
                if data["due_date"]
                else None
            )

        db.session.commit()

        return jsonify({"success": True, "todo": todo.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@todos_bp.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    """Delete a todo."""
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return jsonify({"success": False, "error": "Todo not found"}), 404

        db.session.delete(todo)
        db.session.commit()

        return jsonify({"success": True, "message": "Todo deleted successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
