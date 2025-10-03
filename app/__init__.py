from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Register blueprints
    from app.routes.main_routes import main_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.calendar_routes import calendar_bp
    from app.routes.chores_routes import chores_bp
    from app.routes.todos_routes import todos_bp
    from app.routes.weather_routes import weather_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(calendar_bp, url_prefix="/calendar")
    app.register_blueprint(chores_bp, url_prefix="/chores")
    app.register_blueprint(todos_bp, url_prefix="/todos")
    app.register_blueprint(weather_bp, url_prefix="/weather")

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
