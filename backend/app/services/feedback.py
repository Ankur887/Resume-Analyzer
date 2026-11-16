"""
feedback.py — Module 4: Smart Feedback System
Generates prioritised, actionable improvement suggestions based on
resume score breakdown and ATS keyword results.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.services.ats_checker import ATSResult
from app.services.scorer import ScoreResult


# ------------------------------------------------------------------ dataclass


@dataclass
class Suggestion:
    priority: str    # "high" | "medium" | "low"
    category: str    # e.g. "ATS", "Skills", "Projects"
    message: str     # human-readable advice


# ------------------------------------------------------------------ helpers


def _pct(cat_score) -> float:
    return (cat_score.points / cat_score.max_points * 100) if cat_score.max_points else 0.0


# ------------------------------------------------------------------ rule engine


def generate_feedback(
    score_result: ScoreResult,
    ats_result: ATSResult,
) -> list[Suggestion]:
    """
    Produce a prioritised list of :class:`Suggestion` objects.

    Priority rules:
    - ``high``   → score ≤ 40 % in a category OR ATS score < 30 %
    - ``medium`` → score 40–70 % in a category OR ATS 30–60 %
    - ``low``    → minor enhancements for already-good sections
    """
    suggestions: list[Suggestion] = []

    # ---- Per-category score suggestions ---------------------------------
    for cat in score_result.categories:
        pct = _pct(cat)

        # Re-use the scorer's own notes as messages where present
        for note in cat.notes:
            priority = "high" if pct <= 40 else ("medium" if pct <= 70 else "low")
            suggestions.append(Suggestion(priority=priority, category=cat.label, message=note))

        # Generic low-score catch-all (in case notes list is empty)
        if not cat.notes and pct < 50:
            suggestions.append(
                Suggestion(
                    priority="high",
                    category=cat.label,
                    message=f"Improve your {cat.label.lower()} section to score higher.",
                )
            )

    # ---- ATS suggestions ------------------------------------------------
    ats_score = ats_result.ats_score

    if ats_score < 30:
        suggestions.append(
            Suggestion(
                priority="high",
                category="ATS Compatibility",
                message=(
                    f"Your ATS compatibility for '{ats_result.role}' is critically low "
                    f"({ats_score:.0f}%). Incorporate the missing keywords listed below."
                ),
            )
        )
    elif ats_score < 60:
        suggestions.append(
            Suggestion(
                priority="medium",
                category="ATS Compatibility",
                message=(
                    f"ATS score ({ats_score:.0f}%) can be improved. "
                    f"Add more role-specific keywords to pass automated screening."
                ),
            )
        )
    else:
        suggestions.append(
            Suggestion(
                priority="low",
                category="ATS Compatibility",
                message=(
                    f"Good ATS coverage ({ats_score:.0f}%)! "
                    f"Fine-tune with the remaining missing keywords for top results."
                ),
            )
        )

    # ---- Missing core skills suggestions --------------------------------
    core_missing = ats_result.missing_by_category.get("Core Skills", [])
    if core_missing:
        top_missing = ", ".join(f"'{s}'" for s in core_missing[:5])
        suggestions.append(
            Suggestion(
                priority="high" if len(core_missing) >= 3 else "medium",
                category="Missing Core Skills",
                message=f"Add these core skills for {ats_result.role}: {top_missing}.",
            )
        )

    # ---- Tools suggestions ----------------------------------------------
    tools_missing = ats_result.missing_by_category.get("Tools & Technologies", [])
    if len(tools_missing) >= 3:
        top_tools = ", ".join(f"'{t}'" for t in tools_missing[:4])
        suggestions.append(
            Suggestion(
                priority="medium",
                category="Tools & Technologies",
                message=f"Mention relevant tools: {top_tools}.",
            )
        )

    # ---- General best-practice tips ------------------------------------
    suggestions.append(
        Suggestion(
            priority="low",
            category="Formatting",
            message="Use a clean, single-column layout with consistent fonts and bullet points.",
        )
    )
    suggestions.append(
        Suggestion(
            priority="low",
            category="Quantify Achievements",
            message=(
                "Quantify your impact wherever possible "
                "(e.g. 'Reduced load time by 40%' instead of 'Improved performance')."
            ),
        )
    )

    # ---- Sort: high → medium → low, then by category -------------------
    priority_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda s: (priority_order.get(s.priority, 99), s.category))

    return suggestions
