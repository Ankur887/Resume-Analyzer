"""
ats_checker.py — Module 3: ATS Keyword Checker
Compares resume keywords against role-required skills.
Uses lightweight tokenisation (no spaCy model download required).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.services.parser import ParsedResume
from app.services.skills_data import get_all_keywords, get_role_skills


# ------------------------------------------------------------------ dataclass


@dataclass
class ATSResult:
    role: str
    ats_score: float                          # 0–100
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    matched_by_category: dict[str, list[str]] = field(default_factory=dict)
    missing_by_category: dict[str, list[str]] = field(default_factory=dict)


# ------------------------------------------------------------------ helpers


def _normalise(text: str) -> str:
    """Lower-case and collapse extra whitespace."""
    return re.sub(r"\s+", " ", text.lower().strip())


def _tokenise(text: str) -> set[str]:
    """
    Extract 1-, 2-, and 3-gram tokens from text for fuzzy multi-word matching.
    Returns a set of normalised n-grams.
    """
    words = re.findall(r"[a-z0-9#+\-.]+", text.lower())
    tokens: set[str] = set(words)
    # bigrams
    for i in range(len(words) - 1):
        tokens.add(f"{words[i]} {words[i+1]}")
    # trigrams
    for i in range(len(words) - 2):
        tokens.add(f"{words[i]} {words[i+1]} {words[i+2]}")
    return tokens


def _keyword_in_text(keyword: str, token_set: set[str]) -> bool:
    """Return True if the keyword (or its normalised form) is present."""
    return _normalise(keyword) in token_set


# ------------------------------------------------------------------ public API


def check_ats_keywords(parsed: ParsedResume, role: str) -> ATSResult:
    """
    Check a :class:`ParsedResume` against the required keywords for *role*.

    Returns an :class:`ATSResult` with matched/missing skills and an ATS score.
    """
    token_set = _tokenise(parsed.raw_text)
    skill_map = get_role_skills(role)

    matched_by_category: dict[str, list[str]] = {}
    missing_by_category: dict[str, list[str]] = {}
    all_matched: list[str] = []
    all_missing: list[str] = []

    for category, keywords in skill_map.items():
        matched: list[str] = []
        missing: list[str] = []
        for kw in keywords:
            if _keyword_in_text(kw, token_set):
                matched.append(kw)
            else:
                missing.append(kw)

        matched_by_category[category] = matched
        missing_by_category[category] = missing
        all_matched.extend(matched)
        all_missing.extend(missing)

    total_keywords = len(all_matched) + len(all_missing)
    ats_score = round((len(all_matched) / total_keywords) * 100, 1) if total_keywords else 0.0

    return ATSResult(
        role=role,
        ats_score=ats_score,
        matched_skills=all_matched,
        missing_skills=all_missing,
        matched_by_category=matched_by_category,
        missing_by_category=missing_by_category,
    )
