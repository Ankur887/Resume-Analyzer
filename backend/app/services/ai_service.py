"""
AI "magic touch" helpers: bullet rewriting and summary generation.

Provider is chosen in .env (AI_PROVIDER = groq | anthropic | openai | ollama | none).
Contact details are scrubbed before any text leaves the server, and the
prompts forbid inventing facts. If no provider is configured the rest of
the app keeps working; the AI buttons just report that AI is not set up.

Example .env (backend/.env):
    AI_PROVIDER=groq
    GROQ_API_KEY=gsk_your_new_key_here
    AI_MODEL=openai/gpt-oss-120b
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load backend/.env no matter which folder the app is started from.
# This file lives at backend/app/services/ai_service.py -> parents[2] is backend/.
_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_ENV_PATH)


class AIUnavailable(Exception):
    """Raised when no AI provider is configured."""


SYSTEM = (
    "You are an expert resume writer for ATS-friendly tech resumes. "
    "Never invent employers, job titles, tools, certifications or numbers. "
    "If a metric would strengthen a line but was not provided, use a "
    "placeholder such as [X%] or [N users] for the candidate to fill in. "
    "Output plain text only, with no markdown."
)

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_URL = re.compile(r"(https?://\S+|(?:www\.|linkedin\.com|github\.com)\S+)", re.I)
_PHONE = re.compile(r"(?<!\w)\+?\d[\d\s().-]{8,}\d")


def scrub(text: str) -> str:
    """Remove emails, URLs and phone numbers before sending text to an AI."""
    for rx in (_EMAIL, _URL, _PHONE):
        text = rx.sub("", text)
    return text.strip()


def _chat_completions(url: str, key: str, model: str, prompt: str,
                      max_tokens: int, timeout: int) -> str:
    """Call any OpenAI-compatible /chat/completions endpoint (OpenAI, Groq)."""
    payload = {
        "model": model,
        "temperature": 0.4,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
    }
    if model.startswith("openai/gpt-oss"):
        # Reasoning models: reasoning tokens count toward the limit, so give
        # extra headroom and keep reasoning short to avoid empty answers.
        payload["max_completion_tokens"] = max_tokens + 1500
        payload["reasoning_effort"] = "low"
    else:
        payload["max_tokens"] = max_tokens

    r = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "resume-analyzer/1.0",
        },
        json=payload,
        timeout=timeout,
    )
    r.raise_for_status()
    text = (r.json()["choices"][0]["message"].get("content") or "").strip()
    if not text:
        raise AIUnavailable("The AI model returned an empty answer. Try again.")
    return text


def _call(prompt: str, max_tokens: int = 700) -> str:
    provider = os.getenv("AI_PROVIDER", "").strip().lower()
    timeout = 60

    # Convenience: if AI_PROVIDER is not set but a Groq key exists, use Groq.
    if not provider and os.getenv("GROQ_API_KEY"):
        provider = "groq"

    if provider == "groq":
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise AIUnavailable("GROQ_API_KEY is missing in .env")
        return _chat_completions(
            "https://api.groq.com/openai/v1/chat/completions",
            key,
            os.getenv("AI_MODEL", "openai/gpt-oss-120b"),
            prompt, max_tokens, timeout,
        )

    if provider == "anthropic":
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise AIUnavailable("ANTHROPIC_API_KEY is missing in .env")
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={
                "model": os.getenv("AI_MODEL", "claude-sonnet-5-5"),
                "max_tokens": max_tokens,
                "system": SYSTEM,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=timeout,
        )
        r.raise_for_status()
        return "".join(b.get("text", "") for b in r.json().get("content", [])).strip()

    if provider == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise AIUnavailable("OPENAI_API_KEY is missing in .env")
        return _chat_completions(
            "https://api.openai.com/v1/chat/completions",
            key,
            os.getenv("AI_MODEL", "gpt-4o-mini"),
            prompt, max_tokens, timeout,
        )

    if provider == "ollama":
        base = os.getenv("OLLAMA_URL", "http://localhost:11434")
        r = requests.post(
            f"{base}/api/chat",
            json={
                "model": os.getenv("AI_MODEL", "llama3.1"),
                "stream": False,
                "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
            },
            timeout=120,
        )
        r.raise_for_status()
        return r.json()["message"]["content"].strip()

    raise AIUnavailable(
        "AI is not configured. Set AI_PROVIDER=groq and GROQ_API_KEY in backend/.env, "
        "then restart the server."
    )


def improve_bullets(bullets: list[str], role: str, context: str = "") -> list[str]:
    bullets = [scrub(b) for b in bullets if b.strip()][:8]
    prompt = (
        f"Target role: {role}\nContext: {scrub(context)}\n\n"
        "Rewrite each resume bullet below so it is concise, starts with a strong action verb "
        "and shows impact. Keep every fact true to the original. Keep the same number of bullets. "
        "Return ONLY a JSON array of strings.\n\nBullets:\n" + "\n".join(f"- {b}" for b in bullets)
    )
    out = _call(prompt)
    match = re.search(r"\[.*\]", out, re.S)
    if match:
        try:
            parsed = json.loads(match.group(0))
            result = [str(x).strip() for x in parsed if str(x).strip()]
            if result:
                return result
        except json.JSONDecodeError:
            pass
    # Fallback: model ignored the JSON instruction, split by lines instead.
    return [re.sub(r"^[\s•\-*\d.]+", "", ln).strip() for ln in out.splitlines() if ln.strip()][:8]


def generate_summary(facts: dict, role: str) -> str:
    prompt = (
        f"Target role: {role}\n\nCandidate facts (use ONLY these):\n"
        f"- Job titles: {scrub(', '.join(facts.get('titles', []))) or 'none given'}\n"
        f"- Skills: {scrub(facts.get('skills', '')) or 'none given'}\n"
        f"- Education: {scrub(', '.join(facts.get('education', []))) or 'none given'}\n"
        f"- Projects: {scrub(', '.join(facts.get('projects', []))) or 'none given'}\n\n"
        "Write a 2-3 sentence professional resume summary. No first-person pronouns. "
        "Return only the paragraph."
    )
    return _call(prompt, max_tokens=300).strip().strip('"')