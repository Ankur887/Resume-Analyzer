# SMART RESUME ANALYZER (ResumeAI)
## Comprehensive Technical Project & Architecture Report

---

## 1. Executive Summary

The **Smart Resume Analyzer (ResumeAI)** is an intelligent, full-stack web application designed to evaluate candidate resumes against industry-standard hiring metrics and Applicant Tracking Systems (ATS) keyword requirements. Modern hiring pipelines rely heavily on automated resume parsers to screen applicants; over **75% of resumes are rejected** before reaching a human recruiter due to missing keywords, non-standard section formatting, or structural deficiencies.

ResumeAI addresses this issue by providing candidates with instant, privacy-focused, and transparent resume evaluation. Built on **Flask 3.0**, **SQLAlchemy 2.0**, **pdfplumber**, and custom **n-gram tokenization algorithms**, the application extracts text from PDF and DOCX files, calculates a weighted 100-point score across seven key categories, cross-references candidate skills against specific target technology roles, and outputs prioritized, actionable feedback.

---

## 2. Problem Statement & Motivation

Job seekers, especially fresh graduates and junior engineers, face significant hurdles when submitting resumes online:

- **ATS Keyword Filtering:** Automated ATS engines filter candidates based on exact keyword matches. Candidates with high competence often get filtered out simply due to synonym variations or missing role-specific terminology.
- **Lack of Actionable Feedback:** Traditional job application portals do not inform candidates why their resume failed to pass initial screening.
- **Data Privacy Concerns:** Commercial resume scanners frequently store uploaded resumes permanently, exposing personal contact information to data monetization or leaks.
- **Structural Formatting Errors:** Multi-column layouts, graphics, and non-standard headers cause parsing failures in traditional ATS software.

---

## 3. System Architecture & Technical Stack

The application follows a clean 5-module modular architecture running on a Python/Flask web engine:

| Layer / Module | Technologies Used | Key Purpose |
| :--- | :--- | :--- |
| **Web Framework** | Flask 3.0.3, Werkzeug 3.0.4, Jinja2 | HTTP Routing, Server-Side Templating, Security |
| **Database Layer** | Flask-SQLAlchemy 3.1.1, SQLite 3 | Data Persistence (`Resume` and `Analysis` Entities) |
| **Parsing Engine** | `pdfplumber` 0.11.4, `python-docx` 1.1.2 | PDF & DOCX Raw Text & Table Extraction |
| **Security & Limits** | Flask-Limiter 3.8.0, Werkzeug utilities | Rate Limiting (20/hr) & Path Sanitization |
| **Frontend UI** | Vanilla CSS3, Custom Glassmorphism, JS | Visual Analytics Dashboard & Progress Rings |

---

## 4. Core Modules & Algorithms Deep-Dive

### Module 1: Multi-Format Resume Parsing & Field Extraction
The parser extracts raw text from PDF and Word (`.docx`) documents.
- **PDF Parsing:** Uses `pdfplumber` to extract structured line text page-by-page.
- **DOCX Parsing:** Evaluates paragraphs and table cells via `python-docx`.
- **Regex Metadata Extraction:**
  - *Email Parser:* Standard RFC-compliant pattern.
  - *Phone Parser:* Captures international codes, area codes, and standard mobile formats.
  - *Social Profiles:* Identifies LinkedIn (`linkedin.com/in/*`) and GitHub (`github.com/*`) handles.
- **Section Detection:** Scans text for Education, Technical Skills, Experience, Projects, Certifications, and Summary sections.

### Module 2: Weighted 7-Category Scoring Engine
Evaluates the candidate's resume across 7 key weighted categories out of 100 points:

| Category Name | Weight / Max Pts | Evaluation Criteria |
| :--- | :--- | :--- |
| **Technical Skills** | 20 pts | Section presence (+10 pts) + Tech keyword count bonus (up to +10 pts). |
| **Work Experience** | 20 pts | Section presence (+12 pts) + Action verb count bonus (up to +8 pts). |
| **Education** | 15 pts | Section presence (+8 pts) + Degree keyword (+4 pts) + GPA/CGPA (+3 pts). |
| **Projects** | 15 pts | Section presence (+10 pts) + GitHub/demo links (+3 pts) + Tech stack (+2 pts). |
| **Contact Info** | 10 pts | Email (+3), Phone (+3), LinkedIn (+2), GitHub (+2). |
| **Certifications** | 10 pts | Section presence (+8 pts) + Recognized platform Coursera/AWS (+2 pts). |
| **Completeness** | 10 pts | Word count 300-700 (+5 pts) + Summary section presence (+5 pts). |

### Module 3: ATS Keyword Matching & Tokenization Engine
To avoid heavy ML dependency overheads while ensuring precise multi-word skill extraction, ResumeAI utilizes an **N-Gram Tokenization Strategy**:
- Converts normalized resume text into **1-gram, 2-gram, and 3-gram** token sets.
- Enables exact matching for multi-word skills like `"machine learning"`, `"power bi"`, `"natural language processing"`, and `"rest api"`.
- Maintains detailed skill taxonomies across **7 tech target roles**: *Data Analyst, Web Developer, AI Engineer, Cloud Engineer, DevOps Engineer, Android Developer, and Cybersecurity Analyst*.

### Module 4: Smart Feedback Prioritization Engine
Classifies actionable feedback into three priority tiers:
- **HIGH Priority:** Category score $\le 40\%$, ATS score $< 30\%$, or missing core role skills.
- **MEDIUM Priority:** Category score $41-70\%$, ATS score $30-60\%$, or missing technical tools.
- **LOW Priority:** Category score $> 70\%$, general formatting advice, or metric quantification tips.

---

## 5. Database Schema & Data Models

Utilizes SQLAlchemy 2.0 Mapped declarative models stored in an SQLite database:

- **`Resume` Entity:** `id` (PK), `session_id`, `original_filename`, `stored_filename`, `file_type`, `raw_text`, `email`, `phone`, `linkedin`, `github`, `word_count`, `uploaded_at`.
- **`Analysis` Entity:** `id` (PK), `resume_id` (FK), `target_role`, `resume_score`, `ats_score`, `category_scores` (JSON), `matched_skills` (JSON), `missing_skills` (JSON), `suggestions` (JSON), `created_at`.

---

## 6. Security, Privacy & Performance

- **Payload Size Enforcement:** Strict 5 MB upload limit enforced via Flask configuration.
- **File Path Sanitization:** `secure_filename()` combined with UUID tokens prevents directory traversal (`../`).
- **Transient Storage:** Original binary files are deleted from disk immediately after text parsing.
- **Rate Limiting:** Flask-Limiter caps `/analyze` submissions to 20 requests per hour per IP.
- **Session Isolation:** Session UUID ensures users can only access their own dashboard results.

---

## 7. System Verification & Results

- **Multi-Column PDF Parsing:** Verified text extraction accuracy on complex multi-column resumes.
- **Table Text Parsing in Word:** Confirmed skills listed inside DOCX tables are properly captured.
- **Malformed & Password-Protected Files:** Caught gracefully with user-friendly error banners.
- **Performance:** End-to-end analysis completes in **< 350 ms** on average.

---

## 8. Conclusion & Future Roadmap

The Smart Resume Analyzer provides a lightweight, highly accurate, and privacy-conscious web solution for job seekers aiming to optimize their resumes for ATS screening.

**Future Roadmap:**
1. **LLM Integration:** Integrate local LLMs (e.g., Llama-3 / Ollama) for AI-driven resume bullet rewrites.
2. **Dynamic Job Description Scraping:** Allow users to paste raw job description text or URLs for real-time skill gap analysis.
3. **Automated ATS Resume Generator:** Export optimized, clean single-column PDF resumes directly from the dashboard.
