"""
scorer.py — Module 2: Resume Score Analyzer
Rule-based scoring engine that evaluates a parsed resume and returns
a detailed score breakdown (total out of 100).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.services.parser import ParsedResume


# ------------------------------------------------------------------ dataclasses


@dataclass
class CategoryScore:
    category: str       # internal key, e.g. "contact_info"
    label: str          # human-readable, e.g. "Contact Information"
    points: float       # points awarded
    max_points: float   # maximum possible
    notes: list[str] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        return round((self.points / self.max_points) * 100, 1) if self.max_points else 0.0


@dataclass
class ScoreResult:
    categories: list[CategoryScore]
    total_score: float
    grade: str          # "Excellent" / "Good" / "Average" / "Needs Work"
    summary: str        # one-line interpretation


# ------------------------------------------------------------------ helpers


def _grade(score: float) -> tuple[str, str]:
    if score >= 80:
        return "Excellent", "Your resume is strong and well-structured!"
    elif score >= 60:
        return "Good", "Solid resume with room for improvement."
    elif score >= 40:
        return "Average", "Several key sections need attention."
    else:
        return "Needs Work", "Major sections are missing or incomplete."


def _score_contact(parsed: ParsedResume) -> CategoryScore:
    notes: list[str] = []
    pts = 0.0

    if parsed.email:
        pts += 3
    else:
        notes.append("Add your email address.")

    if parsed.phone:
        pts += 3
    else:
        notes.append("Add a phone number.")

    if parsed.linkedin:
        pts += 2
    else:
        notes.append("Include your LinkedIn profile URL.")

    if parsed.github:
        pts += 2
    else:
        notes.append("Add your GitHub profile link.")

    return CategoryScore("contact_info", "Contact Information", pts, 10, notes)


def _score_education(parsed: ParsedResume) -> CategoryScore:
    notes: list[str] = []
    pts = 0.0
    text = parsed.raw_text.lower()

    if parsed.has_education:
        pts += 8
        # Bonus: contains degree keywords
        degree_keywords = ["b.tech", "btech", "b.e.", "be ", "bsc", "b.sc", "mtech",
                           "m.tech", "msc", "m.sc", "bachelor", "master", "phd", "diploma"]
        if any(kw in text for kw in degree_keywords):
            pts += 4
        else:
            notes.append("Mention your specific degree (e.g. B.Tech, B.Sc).")

        # Bonus: GPA/CGPA present
        if any(kw in text for kw in ["cgpa", "gpa", "percentage", "grade"]):
            pts += 3
        else:
            notes.append("Include your CGPA/GPA or percentage.")
    else:
        notes.append("Add an Education section with your degree details.")

    return CategoryScore("education", "Education", min(pts, 15), 15, notes)


def _score_skills(parsed: ParsedResume) -> CategoryScore:
    notes: list[str] = []
    pts = 0.0
    text = parsed.raw_text.lower()

    if parsed.has_skills:
        pts += 10
        # Bonus: count distinct tech keywords found
        tech_count_keywords = [
            "python", "java", "javascript", "sql", "html", "css", "c++", "c#",
            "react", "node", "django", "flask", "machine learning", "docker",
            "kubernetes", "aws", "git", "linux", "tensorflow", "pytorch",
        ]
        found = sum(1 for kw in tech_count_keywords if kw in text)
        bonus = min(found * 1.0, 10.0)
        pts += bonus
        if found < 5:
            notes.append("Add more technical skills relevant to your target role.")
    else:
        notes.append("Add a dedicated Technical Skills section.")

    return CategoryScore("technical_skills", "Technical Skills", min(pts, 20), 20, notes)


def _score_experience(parsed: ParsedResume) -> CategoryScore:
    notes: list[str] = []
    pts = 0.0
    text = parsed.raw_text.lower()

    if parsed.has_experience:
        pts += 12
        # Bonus: action verbs (shows impact-focused writing)
        action_verbs = [
            "developed", "built", "designed", "implemented", "led",
            "managed", "created", "optimized", "automated", "deployed",
            "improved", "achieved", "increased", "reduced", "collaborated",
        ]
        verbs_found = sum(1 for v in action_verbs if v in text)
        pts += min(verbs_found * 1.0, 8.0)
        if verbs_found < 3:
            notes.append("Use strong action verbs (e.g. 'developed', 'implemented').")
    else:
        notes.append("Add Work Experience or Internship details.")

    return CategoryScore("experience", "Work Experience / Internship", min(pts, 20), 20, notes)


def _score_projects(parsed: ParsedResume) -> CategoryScore:
    notes: list[str] = []
    pts = 0.0
    text = parsed.raw_text.lower()

    if parsed.has_projects:
        pts += 10
        # Bonus: project has links (GitHub / demo)
        if "github" in text or "live demo" in text or "deployed" in text:
            pts += 3
        else:
            notes.append("Add GitHub links or deployment URLs to your projects.")

        # Bonus: mentions tech stack in projects
        if any(kw in text for kw in ["using", "built with", "tech stack", "technologies used"]):
            pts += 2
        else:
            notes.append("Mention the tech stack used in each project.")
    else:
        notes.append("Add a Projects section showcasing your work.")

    return CategoryScore("projects", "Projects", min(pts, 15), 15, notes)


def _score_certifications(parsed: ParsedResume) -> CategoryScore:
    notes: list[str] = []
    pts = 0.0

    if parsed.has_certifications:
        pts += 8
        text = parsed.raw_text.lower()
        # Bonus: recognised platforms
        platforms = ["coursera", "udemy", "edx", "nptel", "google", "aws", "microsoft",
                     "ibm", "linkedin learning", "hackerrank"]
        if any(p in text for p in platforms):
            pts += 2
        else:
            notes.append("Include certifications from recognised platforms (Coursera, AWS, etc.).")
    else:
        notes.append("Add relevant certifications to boost credibility.")

    return CategoryScore("certifications", "Certifications", min(pts, 10), 10, notes)


def _score_completeness(parsed: ParsedResume) -> CategoryScore:
    notes: list[str] = []
    pts = 0.0

    # Word count heuristic: 300–700 words is ideal for fresher/student resumes
    wc = parsed.word_count
    if 300 <= wc <= 700:
        pts += 5
    elif 200 <= wc < 300 or 700 < wc <= 900:
        pts += 3
        if wc < 300:
            notes.append("Resume is too short — add more detail to key sections.")
        else:
            notes.append("Resume may be too long for a fresher; aim for 300–700 words.")
    else:
        notes.append("Resume length is outside the ideal range (300–700 words).")

    # Summary / objective section
    if parsed.has_summary:
        pts += 5
    else:
        notes.append("Add a professional Summary or Objective at the top.")

    return CategoryScore("completeness", "Resume Length & Completeness", min(pts, 10), 10, notes)


# ------------------------------------------------------------------ public API


def score_resume(parsed: ParsedResume) -> ScoreResult:
    """
    Evaluate a :class:`ParsedResume` and return a :class:`ScoreResult`.
    Total score is out of 100.
    """
    categories = [
        _score_contact(parsed),
        _score_education(parsed),
        _score_skills(parsed),
        _score_experience(parsed),
        _score_projects(parsed),
        _score_certifications(parsed),
        _score_completeness(parsed),
    ]

    total = round(sum(c.points for c in categories), 1)
    grade, summary = _grade(total)

    return ScoreResult(categories=categories, total_score=total, grade=grade, summary=summary)
