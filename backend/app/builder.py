"""
Resume Builder blueprint: form -> live preview -> live score -> PDF/DOCX export,
plus AI helpers. The live score reuses your existing parser/scorer/ats_checker
by rendering the draft to a temporary DOCX and analysing it like an upload.
"""

from __future__ import annotations

import io
import logging
import os
import re
import tempfile
from xml.sax.saxutils import escape

import requests
from docx import Document
from docx.shared import Inches, Pt
from flask import Blueprint, jsonify, render_template, request, send_file, session

from app.extensions import limiter
from app.models import Resume
from app.services import ai_service, ats_checker, parser, scorer
from app.services.parser import ParsingError
from app.services.skills_data import available_roles

logger = logging.getLogger(__name__)
builder_bp = Blueprint("builder", __name__, url_prefix="/builder")

MAX_PAYLOAD = 100_000  # bytes


# ---------- draft helpers ----------

def _lines(value) -> list[str]:
    if isinstance(value, list):
        raw = [str(v) for v in value]
    else:
        raw = str(value or "").split("\n")
    return [re.sub(r"^[\s•\-*]+", "", ln).strip() for ln in raw if ln.strip()]


def _get_draft():
    if request.content_length and request.content_length > MAX_PAYLOAD:
        return None
    body = request.get_json(silent=True) or {}
    draft = body.get("draft")
    return draft if isinstance(draft, dict) else None


def build_sections(d: dict):
    """Return (name, contact_line, sections). Section items: head/text/bullet tuples."""
    c = d.get("contact") or {}
    name = (c.get("name") or "").strip() or "Your Name"
    parts = [c.get(k, "").strip() for k in ("email", "phone", "location", "linkedin", "github")]
    contact_line = " | ".join(p for p in parts if p)

    secs = []
    summary = (d.get("summary") or "").strip()
    if summary:
        secs.append(("Summary", [("text", summary)]))

    skills = [s.strip() for s in re.split(r"[,;\n]", d.get("skills") or "") if s.strip()]
    if skills:
        secs.append(("Technical Skills", [("text", ", ".join(skills))]))

    exp = []
    for e in d.get("experience") or []:
        title = " - ".join(x for x in [(e.get("title") or "").strip(), (e.get("company") or "").strip()] if x)
        if title:
            exp.append(("head", title, (e.get("dates") or "").strip()))
        exp += [("bullet", b) for b in _lines(e.get("bullets"))]
    if exp:
        secs.append(("Work Experience", exp))

    proj = []
    for p in d.get("projects") or []:
        pname = (p.get("name") or "").strip()
        if pname:
            proj.append(("head", pname, (p.get("link") or "").strip()))
        if (p.get("stack") or "").strip():
            proj.append(("text", "Tech stack: " + p["stack"].strip()))
        proj += [("bullet", b) for b in _lines(p.get("bullets"))]
    if proj:
        secs.append(("Projects", proj))

    edu = []
    for e in d.get("education") or []:
        left = " - ".join(x for x in [(e.get("degree") or "").strip(), (e.get("school") or "").strip()] if x)
        if left:
            edu.append(("head", left, (e.get("dates") or "").strip()))
        if (e.get("gpa") or "").strip():
            edu.append(("text", "GPA/CGPA: " + e["gpa"].strip()))
    if edu:
        secs.append(("Education", edu))

    certs = _lines(d.get("certifications"))
    if certs:
        secs.append(("Certifications", [("bullet", c) for c in certs]))

    return name, contact_line, secs


# ---------- exporters ----------

def docx_bytes(d: dict) -> bytes:
    name, contact_line, secs = build_sections(d)
    doc = Document()
    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = Inches(0.8)
    sec.top_margin = sec.bottom_margin = Inches(0.7)
    base = doc.styles["Normal"]
    base.font.name = "Calibri"
    base.font.size = Pt(10.5)

    p = doc.add_paragraph()
    r = p.add_run(name)
    r.bold = True
    r.font.size = Pt(18)
    if contact_line:
        doc.add_paragraph(contact_line)

    for title, items in secs:
        h = doc.add_paragraph()
        hr = h.add_run(title)
        hr.bold = True
        hr.font.size = Pt(12)
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.space_after = Pt(2)
        for item in items:
            if item[0] == "head":
                para = doc.add_paragraph()
                para.add_run(item[1]).bold = True
                if item[2]:
                    para.add_run("  |  " + item[2])
            elif item[0] == "bullet":
                doc.add_paragraph(item[1], style="List Bullet")
            else:
                doc.add_paragraph(item[1])

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def pdf_bytes(d: dict) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

    name, contact_line, secs = build_sections(d)
    s_name = ParagraphStyle("n", fontName="Helvetica-Bold", fontSize=18, leading=22)
    s_c = ParagraphStyle("c", fontName="Helvetica", fontSize=9, leading=12)
    s_h = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=11, leading=14, spaceBefore=8)
    s_b = ParagraphStyle("b", fontName="Helvetica", fontSize=10, leading=13)
    s_li = ParagraphStyle("li", parent=s_b, leftIndent=14, bulletIndent=4)

    story = [Paragraph(escape(name), s_name)]
    if contact_line:
        story.append(Paragraph(escape(contact_line), s_c))
    for title, items in secs:
        story += [Paragraph(escape(title.upper()), s_h), HRFlowable(width="100%", thickness=0.6, color="#444444")]
        story.append(Spacer(1, 2))
        for item in items:
            if item[0] == "head":
                right = f" &nbsp;|&nbsp; {escape(item[2])}" if item[2] else ""
                story.append(Paragraph(f"<b>{escape(item[1])}</b>{right}", s_b))
            elif item[0] == "bullet":
                story.append(Paragraph(escape(item[1]), s_li, bulletText="\u2022"))
            else:
                story.append(Paragraph(escape(item[1]), s_b))

    buf = io.BytesIO()
    SimpleDocTemplate(buf, pagesize=A4, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                      topMargin=0.7 * inch, bottomMargin=0.7 * inch).build(story)
    return buf.getvalue()


# ---------- routes ----------

@builder_bp.route("")
def index():
    prefill = {}
    resume_id = request.args.get("resume_id")
    if resume_id:
        resume = Resume.query.get(resume_id)
        if resume and resume.session_id == session.get("session_id"):
            prefill = {
                "email": resume.email or "", "phone": resume.phone or "",
                "linkedin": resume.linkedin or "", "github": resume.github or "",
            }
    return render_template("builder.html", roles=list(available_roles()), prefill=prefill)


@builder_bp.route("/api/score", methods=["POST"])
@limiter.limit("300 per hour")
def api_score():
    draft = _get_draft()
    role = (request.get_json(silent=True) or {}).get("role", "")
    if draft is None or role not in available_roles():
        return jsonify(error="Invalid request."), 400

    fd, path = tempfile.mkstemp(suffix=".docx")
    os.close(fd)
    try:
        with open(path, "wb") as f:
            f.write(docx_bytes(draft))
        parsed = parser.parse_resume(path, ".docx")
    except ParsingError:
        return jsonify(error="Add more content to see a score."), 422
    finally:
        try:
            os.remove(path)
        except OSError:
            pass

    score = scorer.score_resume(parsed)
    ats = ats_checker.check_ats_keywords(parsed, role)
    return jsonify(
        resume_score=score.total_score,
        ats_score=ats.ats_score,
        categories=[{"label": c.label, "points": c.points, "max_points": c.max_points, "notes": c.notes}
                    for c in score.categories],
        matched_skills=list(ats.matched_skills),
        missing_skills=list(ats.missing_skills),
    )


def _ai_guard(fn):
    """Run an AI call and turn every failure into a clear JSON error."""
    try:
        return jsonify(fn())
    except ai_service.AIUnavailable as exc:
        # Not configured / key missing in .env
        return jsonify(error=str(exc)), 503
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else None
        detail = exc.response.text[:300] if exc.response is not None else ""
        logger.warning("AI provider returned HTTP %s: %s", status, detail)
        if status in (401, 403):
            msg = "The AI provider rejected the API key. Check the key in backend/.env and restart the server."
        elif status == 429:
            msg = "AI rate limit reached. Wait a minute and try again."
        elif status in (400, 404):
            msg = "The AI model name looks wrong. Check AI_MODEL in backend/.env."
        else:
            msg = f"The AI provider returned an error (HTTP {status}). Try again shortly."
        return jsonify(error=msg), 502
    except requests.RequestException as exc:
        logger.warning("AI request failed: %s", exc)
        return jsonify(error="Could not reach the AI service. Check your internet connection and try again."), 502
    except Exception:  # noqa: BLE001 - never leak a stack trace to the browser
        logger.exception("Unexpected error in AI helper")
        return jsonify(error="Something went wrong generating that. Check the server terminal for details."), 500


@builder_bp.route("/api/improve", methods=["POST"])
@limiter.limit("30 per hour")
def api_improve():
    body = request.get_json(silent=True) or {}
    bullets = _lines(body.get("bullets"))
    role = body.get("role", "")
    if not bullets or role not in available_roles() or len(str(body.get("bullets"))) > 3000:
        return jsonify(error="Add 1-8 short bullet points first."), 400
    return _ai_guard(lambda: {"bullets": ai_service.improve_bullets(bullets, role, str(body.get("context", ""))[:200])})


@builder_bp.route("/api/summary", methods=["POST"])
@limiter.limit("30 per hour")
def api_summary():
    draft = _get_draft()
    role = (request.get_json(silent=True) or {}).get("role", "")
    if draft is None or role not in available_roles():
        return jsonify(error="Invalid request."), 400
    facts = {
        "titles": [e.get("title", "") for e in draft.get("experience") or [] if e.get("title")],
        "skills": draft.get("skills", ""),
        "education": [e.get("degree", "") for e in draft.get("education") or [] if e.get("degree")],
        "projects": [p.get("name", "") for p in draft.get("projects") or [] if p.get("name")],
    }
    return _ai_guard(lambda: {"summary": ai_service.generate_summary(facts, role)})


@builder_bp.route("/export/<fmt>", methods=["POST"])
@limiter.limit("60 per hour")
def export(fmt: str):
    draft = _get_draft()
    if draft is None or fmt not in ("pdf", "docx"):
        return jsonify(error="Invalid request."), 400
    if fmt == "pdf":
        data, mime = pdf_bytes(draft), "application/pdf"
    else:
        data, mime = docx_bytes(draft), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return send_file(io.BytesIO(data), mimetype=mime, as_attachment=True, download_name=f"resume.{fmt}")