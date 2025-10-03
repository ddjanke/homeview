#!/usr/bin/env python3
"""
Simple test script to verify the HomeView application works correctly.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import CalendarEvent, Chore, Todo, WeatherData


def test_app_creation():
    """Test that the app can be created successfully."""
    print("Testing app creation...")
    try:
        app = create_app()
        print("✅ App created successfully")
        return app
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return None


def test_database_models():
    """Test that database models work correctly."""
    print("\nTesting database models...")
    try:
        app = create_app()
        with app.app_context():
            # Test CalendarEvent
            from datetime import datetime

            event = CalendarEvent(
                id="test_event_1",
                title="Test Event",
                start_time=datetime(2024, 1, 15, 9, 0, 0),
                end_time=datetime(2024, 1, 15, 10, 0, 0),
                category="personal",
            )
            db.session.add(event)

            # Test Chore
            chore = Chore(
                name="Test Chore",
                assigned_to="Test Person",
                frequency="daily",
                day_of_week="M",
            )
            db.session.add(chore)

            # Test Todo
            todo = Todo(title="Test Todo", description="Test Description", priority=8)
            db.session.add(todo)

            # Test WeatherData
            weather = WeatherData()
            weather.set_current_data(
                {"temperature": 72, "condition": "sunny", "humidity": 45}
            )
            db.session.add(weather)

            db.session.commit()
            print("✅ Database models work correctly")

            # Clean up test data
            db.session.delete(event)
            db.session.delete(chore)
            db.session.delete(todo)
            db.session.delete(weather)
            db.session.commit()
            print("✅ Test data cleaned up")

    except Exception as e:
        print(f"❌ Database model test failed: {e}")


def test_routes():
    """Test that routes are accessible."""
    print("\nTesting routes...")
    try:
        app = create_app()
        with app.test_client() as client:
            # Test main route
            response = client.get("/")
            assert response.status_code == 200
            print("✅ Main route works")

            # Test health check
            response = client.get("/api/health")
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "Online"
            print("✅ Health check works")

            # Test calendar route
            response = client.get("/calendar/")
            assert response.status_code == 200
            print("✅ Calendar route works")

            # Test chores route
            response = client.get("/chores/")
            assert response.status_code == 200
            print("✅ Chores route works")

            # Test todos route
            response = client.get("/todos/")
            assert response.status_code == 200
            print("✅ Todos route works")

            # Test weather route
            response = client.get("/weather/")
            assert response.status_code == 200
            print("✅ Weather route works")

    except Exception as e:
        print(f"❌ Route test failed: {e}")


def main():
    """Run all tests."""
    print("🏠 HomeView Application Test Suite")
    print("=" * 40)

    # Test app creation
    app = test_app_creation()
    if not app:
        print("\n❌ Cannot continue without app creation")
        return

    # Test database models
    test_database_models()

    # Test routes
    test_routes()

    print("\n" + "=" * 40)
    print("🎉 All tests completed!")
    print("\nTo run the application:")
    print("  python run.py")
    print("\nThen open your browser to:")
    print("  http://localhost:5000")


if __name__ == "__main__":
    main()
