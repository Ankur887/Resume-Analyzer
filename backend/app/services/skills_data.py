"""
skills_data.py — Module 3 (ATS Keyword Checker)
Role → required keyword mappings used for ATS matching.
"""

from __future__ import annotations

# Each role maps to a dict of category → list of required skill keywords.
# Keywords are lowercase; matching is case-insensitive.

ROLE_SKILLS: dict[str, dict[str, list[str]]] = {
    "Data Analyst": {
        "Core Skills": [
            "python", "sql", "excel", "statistics", "data analysis",
            "data visualization", "tableau", "power bi", "matplotlib",
            "pandas", "numpy", "r", "hypothesis testing",
        ],
        "Tools & Technologies": [
            "jupyter", "google analytics", "bigquery", "mysql", "postgresql",
            "mongodb", "apache spark", "hadoop",
        ],
        "Soft Skills": [
            "communication", "problem solving", "critical thinking",
            "storytelling", "presentation",
        ],
    },
    "Web Developer": {
        "Core Skills": [
            "html", "css", "javascript", "react", "node.js", "nodejs",
            "rest api", "restful", "responsive design", "bootstrap",
            "typescript", "git", "json",
        ],
        "Tools & Technologies": [
            "webpack", "docker", "mongodb", "postgresql", "mysql",
            "express", "next.js", "vue", "angular", "tailwind",
            "github", "api", "http",
        ],
        "Soft Skills": [
            "collaboration", "problem solving", "agile", "scrum",
        ],
    },
    "AI Engineer": {
        "Core Skills": [
            "python", "machine learning", "deep learning", "tensorflow",
            "pytorch", "scikit-learn", "nlp", "natural language processing",
            "computer vision", "neural network", "data preprocessing",
            "model training", "feature engineering",
        ],
        "Tools & Technologies": [
            "jupyter", "keras", "huggingface", "transformers", "openai",
            "langchain", "pandas", "numpy", "docker", "git",
            "mlflow", "kubernetes",
        ],
        "Soft Skills": [
            "research", "analytical thinking", "communication", "documentation",
        ],
    },
    "Cloud Engineer": {
        "Core Skills": [
            "aws", "azure", "google cloud", "gcp", "cloud computing",
            "infrastructure", "devops", "ci/cd", "terraform", "docker",
            "kubernetes", "networking", "linux", "bash", "python",
        ],
        "Tools & Technologies": [
            "ec2", "s3", "lambda", "cloudformation", "ansible",
            "jenkins", "github actions", "prometheus", "grafana",
            "load balancing", "auto scaling",
        ],
        "Soft Skills": [
            "problem solving", "documentation", "collaboration",
        ],
    },
    "DevOps Engineer": {
        "Core Skills": [
            "devops", "ci/cd", "docker", "kubernetes", "jenkins",
            "github actions", "linux", "bash", "python", "terraform",
            "ansible", "monitoring", "logging",
        ],
        "Tools & Technologies": [
            "aws", "azure", "gcp", "git", "prometheus", "grafana",
            "elk stack", "nginx", "maven", "gradle",
        ],
        "Soft Skills": [
            "collaboration", "automation mindset", "problem solving",
        ],
    },
    "Android Developer": {
        "Core Skills": [
            "java", "kotlin", "android", "android sdk", "android studio",
            "xml", "jetpack compose", "mvvm", "restful api", "sqlite",
            "room database", "firebase",
        ],
        "Tools & Technologies": [
            "gradle", "git", "retrofit", "okhttp", "coroutines",
            "live data", "view model", "google play", "push notifications",
        ],
        "Soft Skills": [
            "ui/ux", "problem solving", "debugging",
        ],
    },
    "Cybersecurity Analyst": {
        "Core Skills": [
            "cybersecurity", "network security", "penetration testing",
            "ethical hacking", "vulnerability assessment", "siem",
            "firewall", "ids", "ips", "encryption", "incident response",
            "risk assessment", "linux", "python",
        ],
        "Tools & Technologies": [
            "kali linux", "metasploit", "wireshark", "nmap", "burp suite",
            "splunk", "nessus", "owasp", "iso 27001",
        ],
        "Soft Skills": [
            "analytical thinking", "communication", "attention to detail",
        ],
    },
}


def available_roles() -> list[str]:
    """Return the list of supported target roles."""
    return sorted(ROLE_SKILLS.keys())


def get_role_skills(role: str) -> dict[str, list[str]]:
    """Return the skill categories dict for a role (empty dict if unknown)."""
    return ROLE_SKILLS.get(role, {})


def get_all_keywords(role: str) -> list[str]:
    """Flatten all keywords for a given role into a single list."""
    skill_map = get_role_skills(role)
    flat: list[str] = []
    for keywords in skill_map.values():
        flat.extend(keywords)
    return flat
