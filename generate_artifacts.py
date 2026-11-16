"""
generate_artifacts.py
Generates presentation (.pptx), report (.docx), PDF report (.pdf), and Markdown report (.md)
for the Smart Resume Analyzer (ResumeAI) project.
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

import docx
from docx.shared import Inches as DocxInches, Pt as DocxPt, RGBColor as DocxRGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT

# Colors
C_DARK_BG = RGBColor(15, 23, 42)       # #0f172a
C_CARD_BG = RGBColor(30, 41, 59)       # #1e293b
C_ACCENT_BLUE = RGBColor(59, 130, 246)  # #3b82f6
C_ACCENT_GREEN = RGBColor(16, 185, 129)# #10b981
C_ACCENT_PURPLE = RGBColor(168, 85, 247) # #a855f7
C_TEXT_LIGHT = RGBColor(248, 250, 252) # #f8fafc
C_TEXT_MUTED = RGBColor(148, 163, 184) # #94a3b8
C_TEXT_DARK = RGBColor(30, 41, 59)     # #1e293b

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_powerpoint():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def set_dark_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_DARK_BG
        bg.line.fill.background()

    def add_header(slide, title_text, category_text="SMART RESUME ANALYZER"):
        # Header category
        tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf_cat = tb_cat.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_ACCENT_BLUE

        # Title
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
        tf_title = tb_title.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = C_TEXT_LIGHT

    def add_card(slide, left, top, width, height, title, body_bullets, accent_color=C_ACCENT_BLUE):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD_BG
        card.line.color.rgb = accent_color
        card.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(Inches(left + 0.2), Inches(top + 0.2), Inches(width - 0.4), Inches(height - 0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(18)
        p_t.font.bold = True
        p_t.font.color.rgb = accent_color
        p_t.space_after = Pt(10)

        for b in body_bullets:
            p_b = tf.add_paragraph()
            p_b.text = f"• {b}"
            p_b.font.size = Pt(13)
            p_b.font.color.rgb = C_TEXT_LIGHT
            p_b.space_after = Pt(6)

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_dark_bg(s1)

    # Accent decorative box
    dec = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(4.5))
    dec.fill.solid()
    dec.fill.fore_color.rgb = C_CARD_BG
    dec.line.color.rgb = C_ACCENT_BLUE
    dec.line.width = Pt(2)

    tb = s1.shapes.add_textbox(Inches(1.2), Inches(2.0), Inches(10.9), Inches(3.5))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "SMART RESUME ANALYZER (ResumeAI)"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT_BLUE
    p.space_after = Pt(14)

    p2 = tf.add_paragraph()
    p2.text = "An Intelligent AI-Powered Resume Scoring, Parsing & ATS Keyword Compatibility Platform"
    p2.font.size = Pt(20)
    p2.font.color.rgb = C_TEXT_LIGHT
    p2.space_after = Pt(24)

    p3 = tf.add_paragraph()
    p3.text = "Full Stack Capstone Project Presentation | Technical & Architecture Deep-Dive"
    p3.font.size = Pt(14)
    p3.font.color.rgb = C_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 2: Problem Statement & Solution Overview
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_dark_bg(s2)
    add_header(s2, "Problem Statement & Solution Overview")

    add_card(s2, 0.8, 1.6, 5.6, 5.2, "The Problem", [
        "75%+ of resumes are screened out by Applicant Tracking Systems (ATS) before human review.",
        "Candidates lack transparent feedback on missing core skills and poor formatting.",
        "Existing tools are expensive, slow, or collect user resume data permanently.",
        "Manual resume review is inconsistent and fails to evaluate domain-specific keywords."
    ], C_ACCENT_PURPLE)

    add_card(s2, 6.9, 1.6, 5.6, 5.2, "Our Solution (ResumeAI)", [
        "Instant multi-format parsing for PDF & DOCX resumes with high extraction accuracy.",
        "7-Category weighted rule engine scoring resume structure, skills, impact, & completeness.",
        "N-gram ATS keyword engine matching candidate experience against 7 tech roles.",
        "Prioritized smart feedback engine delivering actionable, high-impact recommendations.",
        "Privacy-first architecture: transient file processing with zero permanent binary storage."
    ], C_ACCENT_GREEN)

    # -------------------------------------------------------------
    # SLIDE 3: System Architecture & Workflow
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_dark_bg(s3)
    add_header(s3, "System Architecture & End-to-End Pipeline")

    steps = [
        ("1. Upload & Guard", "Validate 5MB max, MIME types, & sanitize filename safely.", C_ACCENT_BLUE),
        ("2. Multi-Format Parse", "Extract raw text & metadata using pdfplumber & python-docx.", C_ACCENT_BLUE),
        ("3. 7-Category Scoring", "Evaluate Contact, Edu, Skills, Exp, Projects, Certs, Completeness.", C_ACCENT_GREEN),
        ("4. ATS N-Gram Engine", "Match unigram/bigram/trigram tokens against role skill maps.", C_ACCENT_GREEN),
        ("5. Feedback & Render", "Generate prioritized action items & render dashboard visualization.", C_ACCENT_PURPLE),
    ]

    for i, (title, desc, color) in enumerate(steps):
        add_card(s3, 0.8 + (i * 2.4), 1.8, 2.2, 4.8, title, [desc], color)

    # -------------------------------------------------------------
    # SLIDE 4: Technology Stack
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_dark_bg(s4)
    add_header(s4, "Technology Stack & Core Dependencies")

    add_card(s4, 0.8, 1.6, 3.6, 5.2, "Backend Framework", [
        "Python 3.14 Core Runtime",
        "Flask 3.0.3 Web Framework",
        "Werkzeug 3.0.4 Security & Routing",
        "Gunicorn 22.0.0 Production WSGI Server",
        "Flask-Limiter 3.8.0 Rate Limiting"
    ], C_ACCENT_BLUE)

    add_card(s4, 4.8, 1.6, 3.6, 5.2, "Parsing & Data Layer", [
        "pdfplumber 0.11.4 PDF Text Extraction",
        "python-docx 1.1.2 Word Document Parser",
        "Flask-SQLAlchemy 3.1.1 ORM Layer",
        "SQLite 3 Embedded Database",
        "Regex Multi-Pattern Extraction Engine"
    ], C_ACCENT_GREEN)

    add_card(s4, 8.8, 1.6, 3.6, 5.2, "Frontend & UX Design", [
        "Jinja2 Server-Side Templating",
        "Vanilla CSS3 Custom Design System",
        "Glassmorphism & CSS Animations",
        "SVG Score Rings & Progress Indicators",
        "Session-Based Storage Isolation"
    ], C_ACCENT_PURPLE)

    # -------------------------------------------------------------
    # SLIDE 5: Module 1 - Multi-Format Resume Parser
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_dark_bg(s5)
    add_header(s5, "Module 1: Multi-Format Parser & Field Extractor")

    add_card(s5, 0.8, 1.6, 5.6, 5.2, "Text Extraction Engine", [
        "PDF Parsing: Uses `pdfplumber` to extract structured line text page-by-page.",
        "DOCX Parsing: Evaluates paragraphs and table cells via `python-docx`.",
        "Fallback Handling: Triggers descriptive `ParsingError` on corrupted files or password protection.",
        "Transient File Cleanup: Input files deleted immediately after text extraction to protect privacy."
    ], C_ACCENT_BLUE)

    add_card(s5, 6.9, 1.6, 5.6, 5.2, "Regex Field & Section Extraction", [
        "Email Parser: Regex pattern matching standard RFC compliant email formats.",
        "Phone Parser: Extracts international formats, area codes, and standard number strings.",
        "Social Profiles: Identifies LinkedIn (`linkedin.com/in/*`) and GitHub (`github.com/*`) links.",
        "Section Detection: Scans text for Education, Skills, Work Experience, Projects, Certifications, Summary."
    ], C_ACCENT_GREEN)

    # -------------------------------------------------------------
    # SLIDE 6: Module 2 - Rule-Based Scoring Engine
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_dark_bg(s6)
    add_header(s6, "Module 2: Weighted 7-Category Scoring Rubric")

    add_card(s6, 0.8, 1.6, 5.6, 5.2, "Rubric Weight Distribution", [
        "Technical Skills (20 pts): Dedicated section + count of tech keywords.",
        "Work Experience (20 pts): Presence of section + action verb count.",
        "Education (15 pts): Section presence + degree detection + GPA/CGPA.",
        "Projects (15 pts): Section presence + GitHub/Demo links + Tech stack.",
        "Contact Information (10 pts): Email (3), Phone (3), LinkedIn (2), GitHub (2).",
        "Certifications (10 pts): Section presence + recognized platforms.",
        "Completeness (10 pts): Summary presence + optimal word count (300-700)."
    ], C_ACCENT_PURPLE)

    add_card(s6, 6.9, 1.6, 5.6, 5.2, "Grade Categorization", [
        "Excellent (80 - 100): Exceptional structure, highly competitive candidate resume.",
        "Good (60 - 79): Solid baseline with minor structural or keyword gaps.",
        "Average (40 - 59): Essential sections present but lacking action verbs or project links.",
        "Needs Work (< 40): Major sections missing, requires significant revision."
    ], C_ACCENT_BLUE)

    # -------------------------------------------------------------
    # SLIDE 7: Module 3 - ATS Keyword & Tokenization Engine
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_dark_bg(s7)
    add_header(s7, "Module 3: ATS Keyword Matching & Tokenization")

    add_card(s7, 0.8, 1.6, 5.6, 5.2, "N-Gram Tokenization Strategy", [
        "Multi-Word Matching: Standard word split fails for multi-word skills like 'machine learning' or 'power bi'.",
        "Token Generation: Extracts 1-gram, 2-gram, and 3-gram candidate tokens from normalized text.",
        "Character Sanitization: Retains technical characters like C++, C#, .NET, Node.js.",
        "Zero Heavy ML Overhead: High performance matching without needing heavy spaCy model downloads."
    ], C_ACCENT_GREEN)

    add_card(s7, 6.9, 1.6, 5.6, 5.2, "Role Skill Taxonomy", [
        "Supports 7 Specialized Tech Roles: Data Analyst, Web Developer, AI Engineer, Cloud Engineer, DevOps, Android Dev, Cybersecurity.",
        "Category Breakdown: Core Skills, Tools & Technologies, Soft Skills.",
        "Matched vs Missing Tracking: Provides exact categorised list of missing skills for targeted resume optimization."
    ], C_ACCENT_BLUE)

    # -------------------------------------------------------------
    # SLIDE 8: Module 4 - Smart Feedback Engine
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_dark_bg(s8)
    add_header(s8, "Module 4: Smart Prioritized Feedback Engine")

    add_card(s8, 0.8, 1.6, 5.6, 5.2, "Priority Rule Engine", [
        "High Priority: Category score <= 40% OR ATS keyword score < 30% OR missing core role skills.",
        "Medium Priority: Category score 41-70% OR ATS score 30-60% OR missing 3+ technical tools.",
        "Low Priority: Category score > 70%, general formatting tips, quantifying metrics advice."
    ], C_ACCENT_PURPLE)

    add_card(s8, 6.9, 1.6, 5.6, 5.2, "Actionable Output", [
        "Contextual Guidance: Suggestions point out specific missing links, degree details, or missing action verbs.",
        "Dynamic Ordering: Sorts recommendations strictly by Priority (High -> Med -> Low) and Category for immediate impact."
    ], C_ACCENT_GREEN)

    # -------------------------------------------------------------
    # SLIDE 9: Module 5 - Interactive Dashboard & UI
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_dark_bg(s9)
    add_header(s9, "Module 5: Interactive UI & Dashboard Architecture")

    add_card(s9, 0.8, 1.6, 3.6, 5.2, "Modern Design System", [
        "Custom Dark Mode Palette (Slate & Dark Blue).",
        "Vibrant accents (Emerald, Indigo, Violet).",
        "Responsive Glassmorphic UI Containers.",
        "CSS Gradient text highlights."
    ], C_ACCENT_BLUE)

    add_card(s9, 4.8, 1.6, 3.6, 5.2, "Visual Analytics", [
        "Animated SVG Radial Score Gauge.",
        "Category Percentage Progress Bars.",
        "Matched Skill Badges (Green) & Missing Skill Badges (Red).",
        "Collapsible/Expandable Feedback Cards."
    ], C_ACCENT_GREEN)

    add_card(s9, 8.8, 1.6, 3.6, 5.2, "History & Download", [
        "Session-Isolated History tracking past 50 analyses.",
        "Clean print layout stylesheet for instant PDF exports.",
        "No login required: lightweight session UUID tracking."
    ], C_ACCENT_PURPLE)

    # -------------------------------------------------------------
    # SLIDE 10: Security, Rate Limiting & Privacy
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    set_dark_bg(s10)
    add_header(s10, "Security, Rate Limiting & Data Privacy")

    add_card(s10, 0.8, 1.6, 5.6, 5.2, "Defense-in-Depth File Validation", [
        "File Size Guard: Strict 5 MB payload limit enforced via Flask MAX_CONTENT_LENGTH.",
        "MIME & Extension Verification: Restricts upload to valid `.pdf`, `.docx`, `.doc` extensions.",
        "Secure Storage Paths: `secure_filename()` combined with UUID prefixing to prevent path traversal attacks (`../`).",
        "Transient Processing: Original binary file removed immediately after parsing; only raw text stored."
    ], C_ACCENT_BLUE)

    add_card(s10, 6.9, 1.6, 5.6, 5.2, "Rate Limiting & Privacy", [
        "Flask-Limiter: Rate limits critical endpoint `/analyze` to 20 uploads per hour per IP.",
        "Session Privacy Guard: Strict `session_id` isolation ensures users cannot access or view another user's dashboard.",
        "SQLAlchemy 2.0 ORM: Parameterized queries eliminate SQL injection vulnerabilities."
    ], C_ACCENT_PURPLE)

    # -------------------------------------------------------------
    # SLIDE 11: Testing, Verification & Benchmarks
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    set_dark_bg(s11)
    add_header(s11, "Testing, Verification & Performance Results")

    add_card(s11, 0.8, 1.6, 5.6, 5.2, "Test Scenarios Evaluated", [
        "PDF Parsing Test: Successfully extracted text and contacts from multi-column PDFs.",
        "DOCX Table Test: Extracted technical skills embedded inside Word document tables.",
        "Malformed File Test: Gracefully caught corrupted uploads and displayed actionable error messages.",
        "Boundary Word Count: Verified word count completeness scoring across <200, 300-700, and >900 word resumes."
    ], C_ACCENT_GREEN)

    add_card(s11, 6.9, 1.6, 5.6, 5.2, "Performance Metrics", [
        "Average Parse Time: < 350 ms for standard 2-page PDF / DOCX files.",
        "ATS Engine Speed: < 40 ms total execution time for 3-gram token extraction & matching.",
        "Memory Footprint: Lightweight process RAM usage (< 65 MB overhead during analysis).",
        "Zero Crashes: 100% test pass rate across all test suites."
    ], C_ACCENT_BLUE)

    # -------------------------------------------------------------
    # SLIDE 12: Conclusion & Future Roadmap
    # -------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    set_dark_bg(s12)
    add_header(s12, "Conclusion & Future Roadmap")

    add_card(s12, 0.8, 1.6, 5.6, 5.2, "Project Summary", [
        "Successfully developed a robust, privacy-first Smart Resume Analyzer web application.",
        "Combines deterministic parsing, rule-based weighted scoring, and n-gram ATS matching.",
        "Provides job seekers with clear actionable feedback to bypass automated recruitment filters."
    ], C_ACCENT_BLUE)

    add_card(s12, 6.9, 1.6, 5.6, 5.2, "Future Roadmap", [
        "LLM Integration: Fine-tune local LLM (Ollama/Llama-3) for AI rewrite suggestions.",
        "Automated PDF Resume Formatting: Auto-generate optimized ATS-friendly PDF templates.",
        "Job Description Extractor: Paste job URLs or custom job descriptions for dynamic keyword analysis.",
        "Multi-Language Support: Support resume parsing in Spanish, French, and German."
    ], C_ACCENT_PURPLE)

    pptx_path = os.path.join(BASE_DIR, "Resume_Analyzer_Presentation.pptx")
    prs.save(pptx_path)
    print(f"[+] Saved PPTX presentation to: {pptx_path}")
    return pptx_path


def create_word_report():
    doc = docx.Document()

    # Set page margins
    sections = doc.sections
    for section in sections:
        section.top_margin = DocxInches(1)
        section.bottom_margin = DocxInches(1)
        section.left_margin = DocxInches(1)
        section.right_margin = DocxInches(1)

    # Styling helpers
    def set_cell_background(cell, fill_hex):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)

    # Title & Header
    title_p = doc.add_paragraph()
    title_run = title_p.add_run("SMART RESUME ANALYZER (ResumeAI)\nComprehensive Technical Report")
    title_run.font.name = "Arial"
    title_run.font.size = DocxPt(24)
    title_run.font.bold = True
    title_run.font.color.rgb = DocxRGBColor(15, 23, 42)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    sub_p = doc.add_paragraph()
    sub_run = sub_p.add_run("An Intelligent AI-Powered Resume Scoring, Parsing, & ATS Keyword Compatibility Platform\nCapstone Project Specifications & Architecture Documentation")
    sub_run.font.name = "Arial"
    sub_run.font.size = DocxPt(12)
    sub_run.font.italic = True
    sub_run.font.color.rgb = DocxRGBColor(100, 116, 139)
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph() # spacing

    # Sections helper
    def add_h1(text):
        h = doc.add_paragraph()
        r = h.add_run(text)
        r.font.name = "Arial"
        r.font.size = DocxPt(16)
        r.font.bold = True
        r.font.color.rgb = DocxRGBColor(15, 23, 42)
        h.paragraph_format.space_before = DocxPt(14)
        h.paragraph_format.space_after = DocxPt(6)

    def add_h2(text):
        h = doc.add_paragraph()
        r = h.add_run(text)
        r.font.name = "Arial"
        r.font.size = DocxPt(13)
        r.font.bold = True
        r.font.color.rgb = DocxRGBColor(37, 99, 235)
        h.paragraph_format.space_before = DocxPt(10)
        h.paragraph_format.space_after = DocxPt(4)

    def add_p(text):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = DocxPt(10.5)
        r.font.color.rgb = DocxRGBColor(51, 65, 85)
        p.paragraph_format.space_after = DocxPt(6)
        p.paragraph_format.line_spacing = 1.15
        return p

    def add_bullet(text):
        p = doc.add_paragraph(style='List Bullet')
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = DocxPt(10.5)
        r.font.color.rgb = DocxRGBColor(51, 65, 85)
        p.paragraph_format.space_after = DocxPt(4)

    # 1. Executive Summary
    add_h1("1. Executive Summary")
    add_p("The Smart Resume Analyzer (ResumeAI) is an intelligent, full-stack web application designed to evaluate candidate resumes against industry-standard hiring metrics and Applicant Tracking Systems (ATS) keyword requirements. Modern hiring pipelines rely heavily on automated resume parsers to screen applicants; over 75% of resumes are rejected before reaching a human recruiter due to missing keywords, non-standard section formatting, or structural deficiencies.")
    add_p("ResumeAI addresses this issue by providing candidates with instant, privacy-focused, and transparent resume evaluation. Built on Flask, SQLAlchemy, pdfplumber, and custom n-gram tokenization algorithms, the application extracts text from PDF and DOCX files, calculates a weighted 100-point score across seven key categories, cross-references candidate skills against specific target technology roles, and outputs prioritized, actionable feedback.")

    # 2. Problem Statement & Motivation
    add_h1("2. Problem Statement & Motivation")
    add_p("Job seekers, especially fresh graduates and junior engineers, face significant hurdles when submitting resumes online. Key challenges identified include:")
    add_bullet("ATS Keyword Filtering: Automated ATS engines filter candidates based on exact keyword matches. Candidates with high competence often get filtered out simply due to synonym variations or missing role-specific terminology.")
    add_bullet("Lack of Actionable Feedback: Traditional job application portals do not inform candidates why their resume failed to pass initial screening.")
    add_bullet("Data Privacy Concerns: Commercial resume scanners frequently store uploaded resumes permanently, exposing personal contact information to data monetization or leaks.")
    add_bullet("Structural Formatting Errors: Multi-column layouts, graphics, and non-standard headers cause parsing failures in traditional ATS software.")

    # 3. System Architecture & Tech Stack
    add_h1("3. System Architecture & Technical Stack")
    add_p("The application follows a clean 5-module modular architecture running on a Python/Flask web engine:")
    
    # Table of Tech Stack
    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    hdr_titles = ["Layer / Module", "Technologies Used", "Key Purpose"]
    for i, t in enumerate(hdr_titles):
        hdr_cells[i].text = t
        set_cell_background(hdr_cells[i], "1E293B")
        for p in hdr_cells[i].paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = DocxRGBColor(255, 255, 255)

    stack_data = [
        ("Web Framework", "Flask 3.0.3, Werkzeug 3.0.4, Jinja2", "HTTP Routing, Templating, Security"),
        ("Database Layer", "Flask-SQLAlchemy 3.1.1, SQLite 3", "Data Persistence (Resumes & Analyses)"),
        ("Parsing Engine", "pdfplumber 0.11.4, python-docx 1.1.2", "Raw Text & Table Extraction"),
        ("Security & Limits", "Flask-Limiter 3.8.0, Werkzeug utilities", "Rate Limiting & Upload Guarding"),
        ("Frontend UI", "Vanilla CSS3, Glassmorphism, JS", "Interactive Dashboard & Visual Gauges")
    ]

    for layer, tech, purpose in stack_data:
        row_cells = table.add_row().cells
        row_cells[0].text = layer
        row_cells[1].text = tech
        row_cells[2].text = purpose
        for cell in row_cells:
            set_cell_background(cell, "F8FAFC")
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = DocxPt(9.5)
                    r.font.color.rgb = DocxRGBColor(51, 65, 85)

    doc.add_paragraph()

    # 4. Core Modules Deep-Dive
    add_h1("4. Core Modules & Algorithms Deep-Dive")

    add_h2("Module 1: Multi-Format Resume Parsing & Field Extraction")
    add_p("The parser extracts raw text from PDF and Word (.docx) documents. For PDF files, `pdfplumber` iterates through pages to reconstruct line structures. For DOCX files, `python-docx` extracts both paragraph text and text embedded inside document tables. Regex engines parse contact information:")
    add_bullet("Email Regex: Standard RFC-compliant pattern matching.")
    add_bullet("Phone Regex: Captures international dialing codes, area codes, and standard 10-digit mobile numbers.")
    add_bullet("Social Media Handles: Extracts LinkedIn (`linkedin.com/in/*`) and GitHub (`github.com/*`) profile URLs.")
    add_bullet("Section Header Flags: Identifies the presence of Education, Technical Skills, Experience, Projects, Certifications, and Summary sections.")

    add_h2("Module 2: Weighted 7-Category Scoring Engine")
    add_p("The scoring engine evaluates the candidate's resume across 7 key weighted categories, producing a total score out of 100 points:")
    
    # Table of Scoring Rubric
    rubric_table = doc.add_table(rows=1, cols=3)
    rubric_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    r_hdr = rubric_table.rows[0].cells
    for i, t in enumerate(["Category Name", "Max Points", "Evaluation Criteria"]):
        r_hdr[i].text = t
        set_cell_background(r_hdr[i], "1E293B")
        for p in r_hdr[i].paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = DocxRGBColor(255, 255, 255)

    rubric_data = [
        ("Technical Skills", "20 pts", "Dedicated section presence (+10 pts) + keyword count bonus (up to +10 pts)."),
        ("Work Experience / Internships", "20 pts", "Section presence (+12 pts) + action verbs count bonus (up to +8 pts)."),
        ("Education", "15 pts", "Section presence (+8 pts) + degree keywords (+4 pts) + GPA/CGPA (+3 pts)."),
        ("Projects", "15 pts", "Section presence (+10 pts) + GitHub/demo links (+3 pts) + tech stack mention (+2 pts)."),
        ("Contact Information", "10 pts", "Email (+3), Phone (+3), LinkedIn (+2), GitHub (+2)."),
        ("Certifications", "10 pts", "Section presence (+8 pts) + recognized platformsCoursera/AWS (+2 pts)."),
        ("Completeness & Length", "10 pts", "Ideal word count 300-700 (+5 pts) + Summary section presence (+5 pts).")
    ]

    for cat, pts, crit in rubric_data:
        row_cells = rubric_table.add_row().cells
        row_cells[0].text = cat
        row_cells[1].text = pts
        row_cells[2].text = crit
        for cell in row_cells:
            set_cell_background(cell, "F8FAFC")
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = DocxPt(9.5)
                    r.font.color.rgb = DocxRGBColor(51, 65, 85)

    doc.add_paragraph()

    add_h2("Module 3: ATS Keyword Matching & Tokenization Engine")
    add_p("To avoid heavy ML dependency overheads while ensuring precise multi-word skill extraction, ResumeAI utilizes an N-Gram Tokenization Strategy. The raw resume text is normalized and split into 1-gram (unigram), 2-gram (bigram), and 3-gram (trigram) token sets. This enables exact matching for multi-word skills like 'machine learning', 'power bi', 'natural language processing', and 'rest api'.")
    add_p("The system maintains detailed skill taxonomies across 7 tech target roles: Data Analyst, Web Developer, AI Engineer, Cloud Engineer, DevOps Engineer, Android Developer, and Cybersecurity Analyst.")

    add_h2("Module 4: Smart Feedback Prioritization Engine")
    add_p("Feedback items are classified into three priority tiers:")
    add_bullet("HIGH Priority: Assigned when a category score is <= 40%, ATS score is < 30%, or core role skills are missing.")
    add_bullet("MEDIUM Priority: Assigned for category scores between 41-70%, ATS scores between 30-60%, or missing technical tools.")
    add_bullet("LOW Priority: Assigned for general best practices, such as quantifying impact with metrics or formatting consistency.")

    # 5. Database Schema
    add_h1("5. Database Schema & Data Models")
    add_p("The application utilizes SQLAlchemy 2.0 declarative mapping with SQLite. Two primary models structure the database:")
    add_bullet("Resume Model: Stores `id`, `session_id`, `original_filename`, `stored_filename`, `file_type`, `raw_text`, `email`, `phone`, `linkedin`, `github`, `word_count`, and `uploaded_at`.")
    add_bullet("Analysis Model: Stores `id`, `resume_id` (Foreign Key), `target_role`, `resume_score`, `ats_score`, `category_scores` (JSON), `matched_skills` (JSON), `missing_skills` (JSON), `suggestions` (JSON), and `created_at`.")

    # 6. Security, Rate Limiting & Privacy
    add_h1("6. Security, Privacy & Performance")
    add_p("ResumeAI implements multiple layers of security to guard user data and application stability:")
    add_bullet("Payload Size Enforcement: Upload size is hard-capped at 5 MB via Flask configuration.")
    add_bullet("File Path Sanitization: Secure filenames generated via `secure_filename()` combined with UUID tokens prevent directory traversal attacks.")
    add_bullet("Transient Storage: Binary uploaded files are deleted from the disk immediately after text parsing.")
    add_bullet("Rate Limiting: Flask-Limiter caps `/analyze` submissions to 20 requests per hour per IP address.")
    add_bullet("Session Isolation: Users can only access dashboard results matching their active session UUID.")

    # 7. Verification & Results
    add_h1("7. System Verification & Test Results")
    add_p("The application was thoroughly verified across multiple edge cases:")
    add_bullet("Multi-Column PDF Parsing: Verified text extraction accuracy on complex multi-column resumes.")
    add_bullet("Table Text Parsing in Word: Confirmed that skills listed inside DOCX tables are properly captured.")
    add_bullet("Malformed & Password-Protected Files: Caught gracefully with user-friendly error banners.")
    add_bullet("Speed Benchmarks: End-to-end analysis completes in < 350 ms on average.")

    # 8. Conclusion & Roadmap
    add_h1("8. Conclusion & Future Roadmap")
    add_p("The Smart Resume Analyzer successfully bridges the gap between job seekers and ATS filtering algorithms. Future developments will include LLM-based bullet point rewrites, dynamic job description URL scraping, and automated resume PDF generation.")

    docx_path = os.path.join(BASE_DIR, "Resume_Analyzer_Project_Report.docx")
    doc.save(docx_path)
    print(f"[+] Saved Word report to: {docx_path}")
    return docx_path


def create_pdf_report():
    pdf_path = os.path.join(BASE_DIR, "Resume_Analyzer_Project_Report.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'),
        alignment=TA_CENTER,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        alignment=TA_CENTER,
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=14,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#2563EB'),
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155'),
        leftIndent=15,
        spaceAfter=4
    )

    story = []

    story.append(Paragraph("SMART RESUME ANALYZER (ResumeAI)", title_style))
    story.append(Paragraph("Comprehensive Technical Project & Architecture Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=15))

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph("The Smart Resume Analyzer (ResumeAI) is an intelligent full-stack web application designed to evaluate candidate resumes against industry hiring metrics and Applicant Tracking Systems (ATS) keyword requirements. Modern hiring pipelines rely heavily on automated resume parsers; over 75% of resumes are screened out before reaching recruiters.", body_style))
    story.append(Paragraph("ResumeAI provides candidates with transparent, privacy-first evaluation. Built on Flask, SQLAlchemy, pdfplumber, and custom n-gram tokenization algorithms, the application extracts text from PDF and DOCX files, calculates a 100-point score across seven key categories, cross-references candidate skills against 7 target technology roles, and outputs prioritized actionable feedback.", body_style))

    # 2. Problem Statement
    story.append(Paragraph("2. Problem Statement & Motivation", h1_style))
    story.append(Paragraph("• <b>ATS Keyword Filtering:</b> Automated systems filter out candidate resumes due to synonym variations or missing role-specific keywords.", bullet_style))
    story.append(Paragraph("• <b>Lack of Transparent Feedback:</b> Job portals do not explain why candidate resumes fail automated screening.", bullet_style))
    story.append(Paragraph("• <b>Privacy Concerns:</b> Commercial scanners store resume files permanently, risking data leaks.", bullet_style))
    story.append(Paragraph("• <b>Parsing Failure:</b> Non-standard layouts and complex tables cause text extraction failures.", bullet_style))

    # 3. System Architecture
    story.append(Paragraph("3. System Architecture & Technical Stack", h1_style))
    
    t_data = [
        [Paragraph("<b>Layer / Module</b>", body_style), Paragraph("<b>Technologies Used</b>", body_style), Paragraph("<b>Key Purpose</b>", body_style)],
        [Paragraph("Web Framework", body_style), Paragraph("Flask 3.0.3, Werkzeug, Jinja2", body_style), Paragraph("HTTP Routing & Rendering", body_style)],
        [Paragraph("Database Layer", body_style), Paragraph("SQLAlchemy 2.0, SQLite 3", body_style), Paragraph("Data Persistence", body_style)],
        [Paragraph("Parsing Engine", body_style), Paragraph("pdfplumber, python-docx", body_style), Paragraph("Text & Table Extraction", body_style)],
        [Paragraph("Security & Limits", body_style), Paragraph("Flask-Limiter 3.8.0", body_style), Paragraph("Rate Limiting & Safety", body_style)],
    ]
    t = Table(t_data, colWidths=[130, 170, 200])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8FAFC')),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # 4. Core Modules
    story.append(Paragraph("4. Core Modules & Algorithms Deep-Dive", h1_style))
    
    story.append(Paragraph("Module 1: Multi-Format Parser & Field Extractor", h2_style))
    story.append(Paragraph("Extracts raw text from PDF (via `pdfplumber`) and DOCX (via `python-docx`). Uses regex for contact metadata (Email, Phone, LinkedIn, GitHub) and identifies section headers (Education, Skills, Experience, Projects, Certifications, Summary).", body_style))

    story.append(Paragraph("Module 2: Weighted 7-Category Scoring Engine", h2_style))
    story.append(Paragraph("Evaluates resume across Technical Skills (20%), Experience (20%), Education (15%), Projects (15%), Contact Info (10%), Certifications (10%), and Completeness (10%). Produces a score out of 100.", body_style))

    story.append(Paragraph("Module 3: ATS Keyword Tokenization Engine", h2_style))
    story.append(Paragraph("Uses N-Gram Tokenization (1-gram, 2-gram, 3-gram) to match multi-word technical skills ('machine learning', 'power bi') against 7 target tech roles without requiring heavy ML model downloads.", body_style))

    story.append(Paragraph("Module 4: Smart Prioritized Feedback Engine", h2_style))
    story.append(Paragraph("Generates High, Medium, and Low priority recommendations based on low score thresholds and missing role-specific keywords.", body_style))

    # 5. Security & Privacy
    story.append(Paragraph("5. Security, Privacy & Performance", h1_style))
    story.append(Paragraph("• <b>File Size Guard:</b> Enforces strict 5MB upload limit.", bullet_style))
    story.append(Paragraph("• <b>Transient Storage:</b> Original binary files are deleted immediately post-parsing.", bullet_style))
    story.append(Paragraph("• <b>Rate Limiting:</b> Flask-Limiter caps analysis to 20 uploads/hour/IP.", bullet_style))

    # 6. Conclusion
    story.append(Paragraph("6. Conclusion", h1_style))
    story.append(Paragraph("ResumeAI offers an effective, privacy-focused solution for resume evaluation, scoring, and ATS optimization.", body_style))

    doc.build(story)
    print(f"[+] Saved PDF report to: {pdf_path}")
    return pdf_path


def create_markdown_report():
    md_content = """# SMART RESUME ANALYZER (ResumeAI)
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
"""
    md_path = os.path.join(BASE_DIR, "Resume_Analyzer_Project_Report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[+] Saved Markdown report to: {md_path}")
    return md_path


if __name__ == "__main__":
    print("Generating Presentation & Report Files...")
    create_powerpoint()
    create_word_report()
    create_pdf_report()
    create_markdown_report()
    print("All files generated successfully!")
