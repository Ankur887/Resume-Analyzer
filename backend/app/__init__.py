"""
Flask application factory.
Initialises extensions, registers Blueprints, and creates the DB tables.
"""

from __future__ import annotations

import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask

load_dotenv()


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=False)

    # ------------------------------------------------------------------ config
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret-change-in-prod"),
        SQLALCHEMY_DATABASE_URI=os.getenv(
            "DATABASE_URI", "sqlite:///resume_analyzer.db"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.root_path, "uploads"),
        MAX_CONTENT_LENGTH=int(os.getenv("MAX_CONTENT_LENGTH", 5 * 1024 * 1024)),
        PERMANENT_SESSION_LIFETIME=timedelta(days=30),
        WTF_CSRF_ENABLED=False,  # No WTF forms used; CSRF handled manually via session
    )

    if test_config:
        app.config.update(test_config)

    # ------------------------------------------------------- init extensions
    from app.extensions import db, limiter

    db.init_app(app)
    limiter.init_app(app)

    # -------------------------------------------------------- register routes
    from app.routes import main_bp
    from app.builder import builder_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(builder_bp)

    # ------------------------------------------------------ create DB tables
    with app.app_context():
        db.create_all()

    return app