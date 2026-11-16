"""
Server-rendered web routes: the upload page, the analysis flow, the
results dashboard, and history (Module 5: Dashboard and Report Generation).
"""

from __future__ import annotations

import logging
import os
import uuid

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from app.extensions import db, limiter
from app.models import Analysis, Resume
from app.services import ats_checker, feedback, parser, scorer
from app.services.parser import ParsingError
from app.services.skills_data import available_roles
from app.utils.validators import UploadValidationError, build_safe_storage_path, validate_upload

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)


def _get_session_id() -> str:
    if "session_id" not in session:
        session["session_id"] = uuid.uuid4().hex
        session.permanent = True
    return session["session_id"]


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
    stored_filename, full_path = build_safe_storage_path(current_app.config["UPLOAD_FOLDER"], uploaded_file.filename)

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
        # We only need the file transiently to extract text; don't retain
        # the original binary on disk longer than necessary.
        _safe_remove(full_path)

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
    db.session.flush()  # get resume.id without a full commit yet

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
                "notes": c.notes,
            }
            for c in score_result.categories
        ],
        matched_skills=ats_result.matched_skills,
        missing_skills=ats_result.missing_skills,
        suggestions=[{"priority": s.priority, "category": s.category, "message": s.message} for s in suggestions],
    )
    db.session.add(analysis)
    db.session.commit()

    return redirect(url_for("main.dashboard", analysis_id=analysis.id))


@main_bp.route("/dashboard/<analysis_id>")
def dashboard(analysis_id: str):
    analysis = Analysis.query.get_or_404(analysis_id)
    resume = Resume.query.get_or_404(analysis.resume_id)

    if resume.session_id != _get_session_id():
        # Not the owning session — treat as not found rather than leaking
        # existence of other users' analyses.
        return render_template("errors/404.html"), 404

    return render_template("dashboard.html", analysis=analysis, resume=resume)


@main_bp.route("/history")
def history():
    session_id = _get_session_id()
    resumes = (
        Resume.query.filter_by(session_id=session_id).order_by(Resume.uploaded_at.desc()).limit(50).all()
    )
    return render_template("history.html", resumes=resumes)


def _safe_remove(path: str) -> None:
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError as exc:
        logger.warning("Could not remove temp upload %s: %s", path, exc)