"""
Flask application factory.

NOTE: Only use this file if your real app/__init__.py is truly empty.
Your server already runs, so it probably is not. If anything fails to import,
send me your real file (and extensions.py / routes.py) and I will merge it.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")  # load keys before anything reads them


def create_app() -> Flask:
    app = Flask(__name__)

    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-only-change-me"),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{BACKEND_DIR / 'instance' / 'resume_analyzer.db'}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=str(Path(__file__).resolve().parent / "uploads"),
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,  # 5 MB uploads
    )
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(BACKEND_DIR / "instance", exist_ok=True)

    logging.basicConfig(level=logging.INFO)
    logging.getLogger(__name__).info(
        "AI provider: %s | Groq key loaded: %s",
        os.getenv("AI_PROVIDER", "(auto)"),
        bool(os.getenv("GROQ_API_KEY")),
    )

    # Extensions (assumes app/extensions.py defines `db` and `limiter`)
    from app.extensions import db, limiter

    db.init_app(app)
    limiter.init_app(app)

    # Models must be imported before create_all
    from app import models  # noqa: F401

    # Blueprints
    from app.builder import builder_bp

    app.register_blueprint(builder_bp)

    # Register every Blueprint defined in app/routes.py, whatever it is named
    from flask import Blueprint
    from app import routes as routes_module

    for obj in vars(routes_module).values():
        if isinstance(obj, Blueprint) and obj.name not in app.blueprints:
            app.register_blueprint(obj)

    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(429)
    def rate_limited(_e):
        return jsonify(error="Too many requests. Please slow down."), 429

    return app