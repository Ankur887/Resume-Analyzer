"""
routes.py — All HTTP routes for the Resume Analyzer application.
Covers: upload page, analyze endpoint, dashboard, and history.
"""

from __future__ import annotations

import logging
import os
import uuid

from flask import (
    Blueprint, current_app, flash, redirect,
    render_template, request, session, url_for,
)
from werkzeug.utils import secure_filename

from app.extensions import db, limiter
from app.models import Analysis, Resume
from app.services import ats_checker, feedback, parser, scorer
from app.services.parser import ParsingError
from app.services.skills_data import available_roles
from app.utils.validators import UploadValidationError, build_safe_storage_path, validate_upload

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)


# ------------------------------------------------------------------ helpers


def _get_session_id() -> str:
    if "session_id" not in session:
        session["session_id"] = uuid.uuid4().hex
        session.permanent = True
    return session["session_id"]


def _safe_remove(path: str) -> None:
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError as exc:
        logger.warning("Could not remove temp upload %s: %s", path, exc)


# ------------------------------------------------------------------ routes


@main_bp.route("/")
def index():
    return render_template("index.html", roles=available_roles())


@main_bp.route("/analyze", methods=["POST"])
@limiter.limit("20 per hour")
def analyze():
    session_id = _get_session_id()
    role = request.form.get("target_role", "").strip()
    uploaded_file = request.files.get("resume_file")

    if role not in available_roles():
        flash("Please choose a valid target role.", "error")
        return redirect(url_for("main.index"))

    try:
        validate_upload(uploaded_file)
    except UploadValidationError as exc:
        flash(str(exc), "error")
        return redirect(url_for("main.index"))

    extension = os.path.splitext(uploaded_file.filename)[1].lower()
    stored_filename, full_path = build_safe_storage_path(
        current_app.config["UPLOAD_FOLDER"], uploaded_file.filename
    )

    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
    uploaded_file.save(full_path)

    try:
        parsed = parser.parse_resume(full_path, extension)
    except ParsingError as exc:
        logger.warning("Parsing failed for %s: %s", stored_filename, exc)
        flash(str(exc), "error")
        _safe_remove(full_path)
        return redirect(url_for("main.index"))
    finally:
        _safe_remove(full_path)

    # ---- persist resume record ----------------------------------------
    resume = Resume(
        session_id=session_id,
        original_filename=secure_filename(uploaded_file.filename),
        stored_filename=stored_filename,
        file_type=extension,
        raw_text=parsed.raw_text,
        email=parsed.email,
        phone=parsed.phone,
        linkedin=parsed.linkedin,
        github=parsed.github,
        word_count=parsed.word_count,
    )
    db.session.add(resume)
    db.session.flush()

    # ---- run AI pipeline ----------------------------------------------
    score_result = scorer.score_resume(parsed)
    ats_result = ats_checker.check_ats_keywords(parsed, role)
    suggestions = feedback.generate_feedback(score_result, ats_result)

    analysis = Analysis(
        resume_id=resume.id,
        target_role=role,
        resume_score=score_result.total_score,
        ats_score=ats_result.ats_score,
        category_scores=[
            {
                "category": c.category,
                "label": c.label,
                "points": c.points,
                "max_points": c.max_points,
                "percentage": c.percentage,
                "notes": c.notes,
            }
            for c in score_result.categories
        ],
        matched_skills=ats_result.matched_skills,
        missing_skills=ats_result.missing_skills,
        suggestions=[
            {"priority": s.priority, "category": s.category, "message": s.message}
            for s in suggestions
        ],
    )
    db.session.add(analysis)
    db.session.commit()

    return redirect(url_for("main.dashboard", analysis_id=analysis.id))


@main_bp.route("/dashboard/<analysis_id>")
def dashboard(analysis_id: str):
    analysis = db.session.get(Analysis, analysis_id)
    if not analysis:
        return render_template("errors/404.html"), 404

    resume = db.session.get(Resume, analysis.resume_id)
    if not resume or resume.session_id != _get_session_id():
        return render_template("errors/404.html"), 404

    return render_template("dashboard.html", analysis=analysis, resume=resume)


@main_bp.route("/history")
def history():
    session_id = _get_session_id()
    resumes = (
        Resume.query
        .filter_by(session_id=session_id)
        .order_by(Resume.uploaded_at.desc())
        .limit(50)
        .all()
    )
    # Attach latest analysis to each resume for display
    resume_data = []
    for r in resumes:
        latest = (
            Analysis.query
            .filter_by(resume_id=r.id)
            .order_by(Analysis.created_at.desc())
            .first()
        )
        resume_data.append({"resume": r, "analysis": latest})

    return render_template("history.html", resume_data=resume_data)


@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404


@main_bp.app_errorhandler(413)
def file_too_large(e):
    flash("File too large. Maximum upload size is 5 MB.", "error")
    return redirect(url_for("main.index"))


@main_bp.app_errorhandler(500)
def internal_error(e):
    logger.exception("Unhandled 500 error: %s", e)
    return render_template("errors/500.html"), 500


@main_bp.route("/history/<resume_id>/delete", methods=["POST"])
def delete_resume(resume_id: str):
    """Delete a resume and all its analyses for the current session."""
    session_id = _get_session_id()
    resume = db.session.get(Resume, resume_id)
    if resume and resume.session_id == session_id:
        # Cascade-delete analyses linked to this resume
        Analysis.query.filter_by(resume_id=resume.id).delete()
        db.session.delete(resume)
        db.session.commit()
    # Always redirect back — even if not found (session mismatch)
    return redirect(url_for("main.history"))
