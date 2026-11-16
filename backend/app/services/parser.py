"""
parser.py — Module 1: Resume Upload and Parsing
Extracts raw text and structured fields from PDF / DOCX resumes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


# ------------------------------------------------------------------ dataclass


@dataclass
class ParsedResume:
    raw_text: str
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    word_count: int = 0

    # Section-presence flags (used by the scorer)
    has_education: bool = False
    has_skills: bool = False
    has_experience: bool = False
    has_projects: bool = False
    has_certifications: bool = False
    has_summary: bool = False


# ------------------------------------------------------------------ error


class ParsingError(Exception):
    """Raised when a resume file cannot be parsed."""


# ------------------------------------------------------------------ helpers


_EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", re.IGNORECASE
)
_PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s\-.]?)?"          # optional country code
    r"(?:\(?\d{2,4}\)?[\s\-.]?)?"       # optional area code
    r"\d{3,5}[\s\-.]?\d{4,6}",          # main number
    re.IGNORECASE,
)
_LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w\-]+", re.IGNORECASE)
_GITHUB_RE = re.compile(r"github\.com/[\w\-]+", re.IGNORECASE)

_SECTION_HEADERS: dict[str, list[str]] = {
    "education": ["education", "academic", "qualification", "degree", "university", "college"],
    "skills": ["skills", "technical skills", "competencies", "technologies", "tools", "expertise"],
    "experience": ["experience", "employment", "work history", "internship", "intern", "job"],
    "projects": ["projects", "project work", "portfolio", "personal projects", "academic projects"],
    "certifications": ["certifications", "certificates", "courses", "training", "licenses"],
    "summary": ["summary", "objective", "profile", "about", "overview"],
}


def _extract_fields(text: str) -> dict:
    """Pull contact fields and section flags from raw text."""
    lower = text.lower()

    email_match = _EMAIL_RE.search(text)
    phone_match = _PHONE_RE.search(text)
    linkedin_match = _LINKEDIN_RE.search(text)
    github_match = _GITHUB_RE.search(text)

    flags: dict[str, bool] = {}
    for section, keywords in _SECTION_HEADERS.items():
        flags[f"has_{section}"] = any(kw in lower for kw in keywords)

    return {
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0).strip() if phone_match else None,
        "linkedin": f"https://{linkedin_match.group(0)}" if linkedin_match else None,
        "github": f"https://{github_match.group(0)}" if github_match else None,
        "word_count": len(text.split()),
        **flags,
    }


# ------------------------------------------------------------------ parsers


def _parse_pdf(path: str) -> str:
    """Extract text from a PDF file using pdfplumber."""
    try:
        import pdfplumber  # type: ignore
    except ImportError:
        raise ParsingError("pdfplumber is not installed. Run: pip install pdfplumber")

    try:
        pages: list[str] = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages.append(page_text)
        text = "\n".join(pages).strip()
    except Exception as exc:
        raise ParsingError(f"Could not read PDF file: {exc}") from exc

    if not text:
        raise ParsingError(
            "No text could be extracted from the PDF. "
            "The file may be scanned/image-based or password-protected."
        )
    return text


def _parse_docx(path: str) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document  # type: ignore
    except ImportError:
        raise ParsingError("python-docx is not installed. Run: pip install python-docx")

    try:
        doc = Document(path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        # Also capture text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        paragraphs.append(cell.text.strip())
        text = "\n".join(paragraphs).strip()
    except Exception as exc:
        raise ParsingError(f"Could not read DOCX file: {exc}") from exc

    if not text:
        raise ParsingError("No text could be extracted from the DOCX file.")
    return text


# ------------------------------------------------------------------ public API


def parse_resume(path: str, extension: str) -> ParsedResume:
    """
    Parse a resume file and return a :class:`ParsedResume`.

    :param path: Absolute file-system path to the uploaded file.
    :param extension: Lowercase file extension including dot (".pdf" | ".docx").
    :raises ParsingError: If the file cannot be read or yields no text.
    """
    if extension == ".pdf":
        raw_text = _parse_pdf(path)
    elif extension in (".docx", ".doc"):
        raw_text = _parse_docx(path)
    else:
        raise ParsingError(f"Unsupported file type: {extension!r}")

    fields = _extract_fields(raw_text)
    return ParsedResume(raw_text=raw_text, **fields)
