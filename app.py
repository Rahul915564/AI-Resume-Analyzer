import streamlit as st
import os
import json
import plotly.graph_objects as go
from dotenv import load_dotenv
import PyPDF2
import httpx
from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import re
import time

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

st.set_page_config(
    page_title="AI Resume Analyzer & Job Matcher",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


def inject_css():
    dark = st.session_state.get("dark_mode", True)
    if dark:
        bg = "linear-gradient(135deg, #0f0c29, #302b63, #24243e)"
        card_bg = "rgba(255,255,255,0.05)"
        text_color = "#e0e0ff"
        border = "rgba(255,255,255,0.15)"
        card_border = f"1px solid rgba(255,255,255,0.15)"
        input_border = f"1px solid rgba(255,255,255,0.15)"
        metric_bg = "rgba(255,255,255,0.08)"
        input_bg = "rgba(255,255,255,0.06)"
        sidebar_bg = "rgba(15,12,41,0.95)"
        sidebar_border = "1px solid rgba(255,255,255,0.15)"
    else:
        bg = "linear-gradient(135deg, #e8eaf6, #ede7f6, #f3e5f5)"
        card_bg = "#f0f2f6"
        text_color = "#1a1a2e"
        border = "#e0e0e0"
        card_border = "2px solid #e0e0e0"
        input_border = "1px solid #cccccc"
        metric_bg = "#ffffff"
        input_bg = "#ffffff"
        sidebar_bg = "#e8eaf6"
        sidebar_border = "1px solid #d0d0d0"

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {{ font-family: 'Inter', sans-serif !important; }}

.stApp {{
    background: {bg};
    background-attachment: fixed;
    color: {text_color};
}}

section[data-testid="stSidebar"] {{
    background: {sidebar_bg} !important;
    backdrop-filter: blur(20px);
    border-right: {sidebar_border};
}}

div[data-testid="stMetric"] {{
    background: {metric_bg};
    backdrop-filter: blur(16px);
    border: {card_border};
    border-radius: 16px;
    padding: 16px 20px;
    box-shadow: 0 4px 24px rgba(80,60,200,0.12);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}}
div[data-testid="stMetric"]:hover {{
    transform: translateY(-4px) perspective(600px) rotateX(3deg);
    box-shadow: 0 12px 40px rgba(80,60,200,0.25);
}}

div[data-testid="stExpander"] {{
    background: {card_bg};
    backdrop-filter: blur(20px);
    border: {card_border};
    border-radius: 16px;
    overflow: hidden;
}}

.stTabs [data-baseweb="tab-list"] {{
    background: {card_bg};
    backdrop-filter: blur(16px);
    border-radius: 14px;
    padding: 6px;
    border: {card_border};
    gap: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 10px;
    color: {text_color};
    font-weight: 500;
    transition: all 0.2s ease;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: white !important;
    box-shadow: 0 4px 16px rgba(124,58,237,0.4);
}}

.stButton > button {{
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    font-size: 15px;
    padding: 12px 28px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(124,58,237,0.35);
    letter-spacing: 0.3px;
}}
.stButton > button:hover {{
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 8px 32px rgba(124,58,237,0.5);
    background: linear-gradient(135deg, #6d28d9, #1d4ed8);
}}
.stButton > button:active {{
    transform: translateY(0px) scale(0.98);
}}

.stDownloadButton > button {{
    background: linear-gradient(135deg, #059669, #0891b2);
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    box-shadow: 0 4px 20px rgba(5,150,105,0.3);
    transition: all 0.3s ease;
}}
.stDownloadButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(5,150,105,0.45);
}}

textarea, .stTextArea textarea {{
    background: {input_bg} !important;
    border: {input_border} !important;
    border-radius: 12px !important;
    color: {text_color} !important;
    backdrop-filter: blur(10px);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}}
textarea:focus, .stTextArea textarea:focus {{
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.2) !important;
}}

.stFileUploader {{
    background: {card_bg};
    border: 2px dashed {border};
    border-radius: 16px;
    transition: border-color 0.2s ease;
    backdrop-filter: blur(10px);
    padding: 8px;
    color: {text_color};
}}
.stFileUploader:hover {{
    border-color: #7c3aed;
}}

.stProgress > div > div {{
    background: linear-gradient(90deg, #7c3aed, #2563eb, #7c3aed);
    background-size: 200% 100%;
    animation: progressShimmer 1.5s linear infinite;
    border-radius: 8px;
}}
@keyframes progressShimmer {{
    0% {{ background-position: 200% 0; }}
    100% {{ background-position: -200% 0; }}
}}

div[data-testid="stAlert"] {{
    border-radius: 12px;
    backdrop-filter: blur(10px);
    border: {card_border};
}}

.hero-title {{
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 0.25rem;
    line-height: 1.1;
    animation: fadeInDown 0.7s ease;
}}
.hero-subtitle {{
    text-align: center;
    color: {'rgba(200,190,255,0.8)' if dark else 'rgba(80,60,150,0.75)'};
    font-size: 1.1rem;
    font-weight: 400;
    margin-bottom: 2rem;
    animation: fadeInDown 0.9s ease;
}}
.section-card {{
    background: {card_bg};
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: {card_border};
    border-radius: 20px;
    padding: 24px;
    margin: 12px 0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    animation: fadeInUp 0.5s ease;
    color: {text_color};
}}
.section-card:hover {{
    transform: translateY(-4px) perspective(800px) rotateX(1deg);
    box-shadow: 0 20px 60px rgba(124,58,237,0.2);
}}
.badge {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin: 3px;
}}
.badge-green {{ background: rgba(5,150,105,0.2); color: #10b981; border: 1px solid rgba(5,150,105,0.3); }}
.badge-red {{ background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }}
.badge-blue {{ background: rgba(37,99,235,0.15); color: #60a5fa; border: 1px solid rgba(37,99,235,0.3); }}
.badge-purple {{ background: rgba(124,58,237,0.15); color: #a78bfa; border: 1px solid rgba(124,58,237,0.3); }}
.badge-yellow {{ background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }}

.feature-header {{
    font-size: 1.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 16px;
}}
.qa-card {{
    background: {card_bg};
    border: {card_border};
    border-radius: 14px;
    padding: 18px;
    margin: 10px 0;
    backdrop-filter: blur(12px);
    border-left: 4px solid #7c3aed;
    animation: fadeInLeft 0.4s ease;
    color: {text_color};
}}
.roadmap-step {{
    background: {card_bg};
    border: {card_border};
    border-radius: 14px;
    padding: 16px 20px;
    margin: 8px 0;
    backdrop-filter: blur(12px);
    border-left: 4px solid #2563eb;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    color: {text_color};
}}
.salary-display {{
    background: linear-gradient(135deg, rgba(124,58,237,0.2), rgba(37,99,235,0.2));
    border: 1px solid rgba(124,58,237,0.3);
    border-radius: 20px;
    padding: 32px;
    text-align: center;
    backdrop-filter: blur(16px);
}}
.divider {{
    height: 1px;
    background: linear-gradient(90deg, transparent, {border}, transparent);
    margin: 24px 0;
    opacity: {'0.5' if not dark else '1'};
}}

@keyframes fadeInDown {{
    from {{ opacity: 0; transform: translateY(-20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes fadeInLeft {{
    from {{ opacity: 0; transform: translateX(-20px); }}
    to {{ opacity: 1; transform: translateX(0); }}
}}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.6; }}
}}
</style>
""", unsafe_allow_html=True)


def fire_confetti():
    st.components.v1.html("""
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.2/dist/confetti.browser.min.js"></script>
<script>
(function() {
    var duration = 3000;
    var end = Date.now() + duration;
    var colors = ['#a78bfa', '#60a5fa', '#34d399', '#fbbf24', '#f87171'];
    (function frame() {
        confetti({ particleCount: 3, angle: 60, spread: 55, origin: {x: 0}, colors: colors });
        confetti({ particleCount: 3, angle: 120, spread: 55, origin: {x: 1}, colors: colors });
        if (Date.now() < end) requestAnimationFrame(frame);
    }());
})();
</script>
<div style="height:1px"></div>
""", height=1)


TRANSLATIONS = {
    "en": {
        "title": "AI Resume Analyzer & Job Matcher",
        "subtitle": "Powered by Groq LLaMA 3.3 · Glassmorphism UI",
        "upload_resume": "Upload Resume (PDF)",
        "job_description": "Paste Job Description",
        "job_desc_placeholder": "Paste the full job description here...",
        "analyze_btn": "🚀 Analyze Resume",
        "analyzing": "AI is analyzing your resume...",
        "ats_score": "ATS Score",
        "skills_match": "Skills Match",
        "missing_keywords": "Missing Keywords",
        "strengths": "Strengths",
        "weaknesses": "Weaknesses",
        "suggestions": "Suggestions",
        "rewritten_summary": "Rewritten Summary",
        "download_report": "⬇️ Download Full PDF Report",
        "language_toggle": "Language / भाषा",
        "no_api_key": "Set GROQ_API_KEY in your environment.",
        "no_resume": "Please upload a resume PDF first.",
        "no_job_desc": "Please paste a job description.",
        "upload_help": "PDF only",
        "results_header": "Analysis Results",
        "overview": "📊 Overview",
        "detailed": "🔍 Analysis",
        "resume_summary_tab": "✍️ Summary",
        "interview_tab": "🎤 Interview Prep",
        "roadmap_tab": "🗺️ Career Roadmap",
        "ai_content_tab": "✨ AI Content",
        "score_gauge": "ATS Compatibility",
        "match_radar": "Skills Radar",
        "keywords_chart": "Missing Keywords",
        "strengths_label": "Strengths",
        "weaknesses_label": "Areas to Improve",
        "suggestions_label": "Suggestions",
        "summary_label": "AI-Rewritten Professional Summary",
        "sidebar_title": "How It Works",
        "sidebar_step1": "① Upload resume PDF",
        "sidebar_step2": "② Paste job description",
        "sidebar_step3": "③ Click Analyze",
        "sidebar_step4": "④ Review insights",
        "sidebar_step5": "⑤ Download report",
        "report_ready": "Report ready!",
        "error_parse": "Could not parse AI response. Try again.",
        "resume_preview": "Resume Preview",
        "dark_mode": "🌙 Dark Mode",
        "light_mode": "☀️ Light Mode",
        "gen_interview": "Generate Interview Questions",
        "gen_roadmap": "Generate Career Roadmap",
        "gen_salary": "Estimate Salary",
        "gen_linkedin": "Generate LinkedIn Bio",
        "gen_cover": "Generate Cover Letter",
        "generating": "Generating...",
        "salary_estimate": "Salary Estimate",
        "career_level": "Career Level",
    },
    "hi": {
        "title": "AI रिज्यूमे विश्लेषक",
        "subtitle": "Groq LLaMA 3.3 द्वारा संचालित",
        "upload_resume": "रिज्यूमे अपलोड करें (PDF)",
        "job_description": "जॉब विवरण पेस्ट करें",
        "job_desc_placeholder": "यहाँ पूरा जॉब विवरण पेस्ट करें...",
        "analyze_btn": "🚀 रिज्यूमे विश्लेषण करें",
        "analyzing": "AI आपके रिज्यूमे का विश्लेषण कर रहा है...",
        "ats_score": "ATS स्कोर",
        "skills_match": "कौशल मिलान",
        "missing_keywords": "गायब कीवर्ड",
        "strengths": "ताकत",
        "weaknesses": "कमज़ोरियां",
        "suggestions": "सुझाव",
        "rewritten_summary": "पुनर्लिखित सारांश",
        "download_report": "⬇️ PDF रिपोर्ट डाउनलोड करें",
        "language_toggle": "Language / भाषा",
        "no_api_key": "GROQ_API_KEY सेट करें।",
        "no_resume": "कृपया PDF अपलोड करें।",
        "no_job_desc": "जॉब विवरण पेस्ट करें।",
        "upload_help": "केवल PDF",
        "results_header": "विश्लेषण परिणाम",
        "overview": "📊 अवलोकन",
        "detailed": "🔍 विश्लेषण",
        "resume_summary_tab": "✍️ सारांश",
        "interview_tab": "🎤 साक्षात्कार",
        "roadmap_tab": "🗺️ करियर रोडमैप",
        "ai_content_tab": "✨ AI सामग्री",
        "score_gauge": "ATS संगतता",
        "match_radar": "कौशल रडार",
        "keywords_chart": "गायब कीवर्ड",
        "strengths_label": "ताकत",
        "weaknesses_label": "सुधार क्षेत्र",
        "suggestions_label": "सुझाव",
        "summary_label": "AI-पुनर्लिखित सारांश",
        "sidebar_title": "कैसे काम करता है",
        "sidebar_step1": "① रिज्यूमे PDF अपलोड करें",
        "sidebar_step2": "② जॉब विवरण पेस्ट करें",
        "sidebar_step3": "③ विश्लेषण करें",
        "sidebar_step4": "④ परिणाम देखें",
        "sidebar_step5": "⑤ रिपोर्ट डाउनलोड करें",
        "report_ready": "रिपोर्ट तैयार है!",
        "error_parse": "AI प्रतिक्रिया पार्स नहीं हो सकी।",
        "resume_preview": "रिज्यूमे पूर्वावलोकन",
        "dark_mode": "🌙 डार्क मोड",
        "light_mode": "☀️ लाइट मोड",
        "gen_interview": "साक्षात्कार प्रश्न बनाएं",
        "gen_roadmap": "करियर रोडमैप बनाएं",
        "gen_salary": "वेतन अनुमान",
        "gen_linkedin": "LinkedIn Bio बनाएं",
        "gen_cover": "Cover Letter बनाएं",
        "generating": "बना रहे हैं...",
        "salary_estimate": "वेतन अनुमान",
        "career_level": "करियर स्तर",
    }
}


def t(key):
    lang = st.session_state.get("lang", "en")
    return TRANSLATIONS[lang].get(key, TRANSLATIONS["en"].get(key, key))


def get_ai_response(prompt):
    client = Groq(
        api_key=GROQ_API_KEY,
        http_client=httpx.Client()
    )
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()


def analyze_resume_with_ai(resume_text, job_description):
    prompt = f"""You are an expert ATS system and career coach. Analyze the resume against the job description and return ONLY a valid JSON object with no markdown or code blocks.

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{job_description[:2000]}

Return this exact JSON structure:
{{
  "ats_score": <integer 0-100>,
  "skills_match_percentage": <integer 0-100>,
  "career_level": "<Junior/Mid-Level/Senior/Lead/Executive>",
  "salary_range": "<e.g. $60,000 - $85,000>",
  "missing_keywords": [{{"keyword": "string", "importance": <1-10>}}],
  "matched_keywords": ["string"],
  "strengths": ["string"],
  "weaknesses": ["string"],
  "improvement_suggestions": ["string"],
  "rewritten_summary": "string",
  "category_scores": {{
    "Technical Skills": <0-100>,
    "Experience": <0-100>,
    "Education": <0-100>,
    "Projects": <0-100>,
    "Formatting": <0-100>
  }}
}}"""
    raw = get_ai_response(prompt).strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"```$", "", raw)
    return json.loads(raw)


def generate_interview_questions(resume_text, job_description):
    prompt = f"""You are an expert technical interviewer. Based on the resume and job description, generate exactly 10 likely interview questions with ideal concise answers.

RESUME (excerpt): {resume_text[:1500]}
JOB DESCRIPTION (excerpt): {job_description[:1000]}

Return ONLY valid JSON, no markdown:
{{
  "questions": [
    {{"question": "string", "answer": "string", "category": "<Behavioral/Technical/Situational>"}}
  ]
}}"""
    raw = get_ai_response(prompt).strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"```$", "", raw)
    return json.loads(raw)


def generate_career_roadmap(resume_text, job_description):
    prompt = f"""You are a career coach. Based on the resume and job description gaps, create a 6-month career roadmap.

RESUME (excerpt): {resume_text[:1500]}
JOB DESCRIPTION (excerpt): {job_description[:1000]}

Return ONLY valid JSON, no markdown:
{{
  "roadmap": [
    {{"month": "Month 1-2", "focus": "string", "skills": ["string"], "resources": ["string"], "milestone": "string"}}
  ],
  "top_skills_to_learn": ["string"],
  "recommended_certifications": ["string"]
}}"""
    raw = get_ai_response(prompt).strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"```$", "", raw)
    return json.loads(raw)


def generate_linkedin_bio(resume_text, analysis):
    prompt = f"""Write a compelling, professional LinkedIn summary (About section) based on this resume. Make it engaging, first-person, 3-4 paragraphs, highlighting key strengths: {', '.join(analysis.get('strengths', [])[:4])}.

RESUME: {resume_text[:2000]}

Return only the LinkedIn bio text, no JSON, no formatting."""
    return get_ai_response(prompt).strip()


def generate_cover_letter(resume_text, job_description, analysis):
    prompt = f"""Write a professional, personalized cover letter for this job application. Make it compelling, specific, and under 400 words.

RESUME HIGHLIGHTS: {resume_text[:1500]}
JOB DESCRIPTION: {job_description[:1000]}
CANDIDATE STRENGTHS: {', '.join(analysis.get('strengths', [])[:4])}

Return only the cover letter text, no JSON."""
    return get_ai_response(prompt).strip()


def render_ats_gauge(score, label):
    color = "#ef4444" if score < 40 else "#f59e0b" if score < 70 else "#10b981"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": label, "font": {"size": 16, "color": "#a78bfa"}},
        number={"suffix": "/100", "font": {"size": 40, "color": color}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#6b7280"},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "rgba(0,0,0,0)",
            "steps": [
                {"range": [0, 40], "color": "rgba(239,68,68,0.1)"},
                {"range": [40, 70], "color": "rgba(245,158,11,0.1)"},
                {"range": [70, 100], "color": "rgba(16,185,129,0.1)"},
            ],
            "threshold": {"line": {"color": color, "width": 4}, "thickness": 0.75, "value": score},
        },
    ))
    fig.update_layout(
        height=280,
        margin=dict(t=40, b=10, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e0e0ff"},
    )
    return fig


def render_radar_chart(category_scores, label):
    categories = list(category_scores.keys())
    values = list(category_scores.values())
    values.append(values[0])
    categories.append(categories[0])
    fig = go.Figure(go.Scatterpolar(
        r=values, theta=categories, fill="toself",
        fillcolor="rgba(124,58,237,0.2)",
        line=dict(color="#7c3aed", width=2),
        marker=dict(size=7, color="#a78bfa"),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=9, color="#9ca3af"), gridcolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(tickfont=dict(size=11, color="#e0e0ff"), gridcolor="rgba(255,255,255,0.08)"),
        ),
        title=dict(text=label, font=dict(size=14, color="#a78bfa")),
        height=360,
        margin=dict(t=60, b=20, l=50, r=50),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e0e0ff"},
    )
    return fig


def render_keywords_bar(missing_keywords):
    if not missing_keywords:
        return None
    kws = missing_keywords[:12]
    keywords = [k["keyword"] for k in kws]
    importance = [k["importance"] for k in kws]
    colors_list = ["#ef4444" if i >= 8 else "#f59e0b" if i >= 5 else "#3b82f6" for i in importance]
    fig = go.Figure(go.Bar(
        x=importance, y=keywords, orientation="h",
        marker=dict(color=colors_list, line=dict(width=0)),
        text=[f"{i}/10" for i in importance],
        textposition="outside",
        textfont=dict(color="#e0e0ff", size=11),
    ))
    fig.update_layout(
        title=dict(text=t("keywords_chart"), font=dict(size=14, color="#a78bfa")),
        xaxis=dict(title="Importance", range=[0, 13], showgrid=True, gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#9ca3af")),
        yaxis=dict(autorange="reversed", tickfont=dict(color="#e0e0ff", size=11)),
        height=max(300, len(keywords) * 38),
        margin=dict(t=50, b=40, l=20, r=80),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e0e0ff"},
    )
    return fig


def generate_pdf_report(analysis, resume_text, job_desc):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch,
                            leftMargin=0.75*inch, rightMargin=0.75*inch)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("Title", parent=styles["Title"],
                                  fontSize=24, textColor=colors.HexColor("#7c3aed"),
                                  spaceAfter=4, alignment=TA_CENTER, fontName="Helvetica-Bold")
    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"],
                                     fontSize=11, textColor=colors.HexColor("#6b7280"),
                                     spaceAfter=16, alignment=TA_CENTER)
    heading_style = ParagraphStyle("Heading", parent=styles["Heading2"],
                                    fontSize=14, textColor=colors.HexColor("#2563eb"),
                                    spaceBefore=14, spaceAfter=6, fontName="Helvetica-Bold")
    body_style = ParagraphStyle("Body", parent=styles["Normal"],
                                 fontSize=10, textColor=colors.HexColor("#374151"),
                                 spaceAfter=4, leading=15)
    bullet_style = ParagraphStyle("Bullet", parent=styles["Normal"],
                                   fontSize=10, textColor=colors.HexColor("#374151"),
                                   leftIndent=16, spaceAfter=3, leading=14,
                                   bulletIndent=6, bulletText="•")

    story = []
    story.append(Paragraph("AI Resume Analyzer", title_style))
    story.append(Paragraph("Analysis Report · Powered by Groq LLaMA 3.3", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#7c3aed"), spaceAfter=12))

    # Scores table
    story.append(Paragraph("Score Summary", heading_style))
    score_data = [
        ["Metric", "Score"],
        ["ATS Score", f"{analysis.get('ats_score', 0)}/100"],
        ["Skills Match", f"{analysis.get('skills_match_percentage', 0)}%"],
        ["Career Level", analysis.get("career_level", "N/A")],
        ["Estimated Salary", analysis.get("salary_range", "N/A")],
    ]
    score_table = Table(score_data, colWidths=[3*inch, 3.5*inch])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7c3aed")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f3ff"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("ROUNDEDCORNERS", [6]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 12))

    # Category scores
    story.append(Paragraph("Category Breakdown", heading_style))
    cat_data = [["Category", "Score"]] + [
        [cat, f"{score}%"] for cat, score in analysis.get("category_scores", {}).items()
    ]
    cat_table = Table(cat_data, colWidths=[3*inch, 3.5*inch])
    cat_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#eff6ff"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(cat_table)
    story.append(Spacer(1, 12))

    def add_bullet_section(title, items):
        story.append(Paragraph(title, heading_style))
        for item in items:
            safe = str(item).encode("latin-1", "replace").decode("latin-1")
            story.append(Paragraph(safe, bullet_style))
        story.append(Spacer(1, 6))

    add_bullet_section("Strengths", analysis.get("strengths", []))
    add_bullet_section("Areas to Improve", analysis.get("weaknesses", []))
    add_bullet_section("Improvement Suggestions", analysis.get("improvement_suggestions", []))

    kw_list = [f"{k['keyword']} (importance: {k['importance']}/10)" for k in analysis.get("missing_keywords", [])]
    add_bullet_section("Missing Keywords", kw_list)

    story.append(Paragraph("AI-Rewritten Professional Summary", heading_style))
    summary = str(analysis.get("rewritten_summary", "")).encode("latin-1", "replace").decode("latin-1")
    story.append(Paragraph(summary, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer


def main():
    for key, default in [("lang", "en"), ("dark_mode", True), ("analysis", None),
                         ("resume_text", ""), ("job_desc", ""), ("interview_data", None),
                         ("roadmap_data", None), ("linkedin_bio", ""), ("cover_letter", "")]:
        if key not in st.session_state:
            st.session_state[key] = default

    inject_css()

    with st.sidebar:
        st.markdown(f"<div style='font-size:1.5rem;font-weight:800;background:linear-gradient(135deg,#a78bfa,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:4px'>🚀 Resume AI</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.75rem;color:#9ca3af;margin-bottom:16px'>Powered by Groq LLaMA 3.3</div>", unsafe_allow_html=True)

        mode_label = t("light_mode") if st.session_state["dark_mode"] else t("dark_mode")
        if st.button(mode_label, use_container_width=True):
            st.session_state["dark_mode"] = not st.session_state["dark_mode"]
            st.rerun()

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        lang_choice = st.radio(
            t("language_toggle"),
            options=["English", "हिंदी"],
            index=0 if st.session_state["lang"] == "en" else 1,
            horizontal=True,
        )
        st.session_state["lang"] = "en" if lang_choice == "English" else "hi"

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-weight:600;margin-bottom:8px'>{t('sidebar_title')}</div>", unsafe_allow_html=True)
        for step in ["sidebar_step1", "sidebar_step2", "sidebar_step3", "sidebar_step4", "sidebar_step5"]:
            st.markdown(f"<div style='font-size:0.85rem;color:#9ca3af;padding:2px 0'>{t(step)}</div>", unsafe_allow_html=True)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        if not GROQ_API_KEY:
            st.error(t("no_api_key"))
        else:
            st.success("✅ Groq API connected")

        if st.session_state.get("analysis"):
            a = st.session_state["analysis"]
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-weight:600;margin-bottom:8px'>{t('salary_estimate')}</div>", unsafe_allow_html=True)
            st.markdown(f"""<div class='salary-display'>
                <div style='font-size:1.5rem;font-weight:800;background:linear-gradient(135deg,#a78bfa,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent'>{a.get('salary_range','N/A')}</div>
                <div style='font-size:0.8rem;color:#9ca3af;margin-top:4px'>{t('career_level')}: {a.get('career_level','N/A')}</div>
            </div>""", unsafe_allow_html=True)

    # Hero header
    st.markdown(f"<div class='hero-title'>{t('title')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='hero-subtitle'>{t('subtitle')}</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown(f"<div class='section-card'>", unsafe_allow_html=True)
        st.markdown(f"**📄 {t('upload_resume')}**")
        uploaded_file = st.file_uploader(
            "Upload Resume PDF", type=["pdf"], help=t("upload_help"), label_visibility="collapsed"
        )
        if uploaded_file:
            text = extract_text_from_pdf(uploaded_file)
            st.session_state["resume_text"] = text
            st.success(f"✅ {len(text):,} characters extracted")
            with st.expander(t("resume_preview"), expanded=False):
                st.text_area("text", text[:2500] + ("..." if len(text) > 2500 else ""),
                             height=180, label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='section-card'>", unsafe_allow_html=True)
        st.markdown(f"**📋 {t('job_description')}**")
        job_desc = st.text_area(
            "Job Description", placeholder=t("job_desc_placeholder"),
            height=180, label_visibility="collapsed", key="job_desc_input"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        analyze_btn = st.button(t("analyze_btn"), use_container_width=True, type="primary")

    if analyze_btn:
        if not GROQ_API_KEY:
            st.error(t("no_api_key"))
        elif not st.session_state.get("resume_text"):
            st.warning(t("no_resume"))
        elif not job_desc.strip():
            st.warning(t("no_job_desc"))
        else:
            # Reset cached extras
            for k in ["interview_data", "roadmap_data", "linkedin_bio", "cover_letter"]:
                st.session_state[k] = None if k != "linkedin_bio" and k != "cover_letter" else ""

            with st.spinner(t("analyzing")):
                bar = st.progress(0)
                for i in range(0, 55, 5):
                    time.sleep(0.05)
                    bar.progress(i)
                try:
                    analysis = analyze_resume_with_ai(st.session_state["resume_text"], job_desc)
                    for i in range(55, 101, 5):
                        time.sleep(0.03)
                        bar.progress(i)
                    st.session_state["analysis"] = analysis
                    st.session_state["job_desc"] = job_desc
                    bar.empty()
                    fire_confetti()
                    st.success("✅ Analysis complete!")
                except json.JSONDecodeError:
                    bar.empty()
                    st.error(t("error_parse"))
                except Exception as e:
                    bar.empty()
                    st.error(f"Error: {e}")

    if st.session_state.get("analysis"):
        analysis = st.session_state["analysis"]
        resume_text = st.session_state.get("resume_text", "")
        job_desc_saved = st.session_state.get("job_desc", "")

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='feature-header'>📊 {t('results_header')}</div>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            t("overview"), t("detailed"), t("resume_summary_tab"),
            t("interview_tab"), t("roadmap_tab"), t("ai_content_tab")
        ])

        # ── TAB 1: OVERVIEW ──────────────────────────────────────────────
        with tab1:
            m1, m2, m3, m4 = st.columns(4)
            score = analysis.get("ats_score", 0)
            match = analysis.get("skills_match_percentage", 0)
            missing_count = len(analysis.get("missing_keywords", []))
            level = analysis.get("career_level", "N/A")

            emoji_score = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
            emoji_match = "🟢" if match >= 70 else "🟡" if match >= 40 else "🔴"

            with m1: st.metric(f"{emoji_score} {t('ats_score')}", f"{score}/100")
            with m2: st.metric(f"{emoji_match} {t('skills_match')}", f"{match}%")
            with m3: st.metric(f"🔑 {t('missing_keywords')}", str(missing_count))
            with m4: st.metric(f"🏅 {t('career_level')}", level)

            st.markdown("")
            g_col, r_col = st.columns(2)
            with g_col:
                st.plotly_chart(render_ats_gauge(score, t("score_gauge")), use_container_width=True)
            with r_col:
                if analysis.get("category_scores"):
                    st.plotly_chart(render_radar_chart(analysis["category_scores"], t("match_radar")), use_container_width=True)

            if analysis.get("missing_keywords"):
                kw_fig = render_keywords_bar(analysis["missing_keywords"])
                if kw_fig:
                    st.plotly_chart(kw_fig, use_container_width=True)

            # Salary card
            st.markdown(f"""<div class='salary-display' style='margin-top:16px'>
                <div style='font-size:0.9rem;color:#9ca3af;margin-bottom:8px'>💰 {t('salary_estimate')}</div>
                <div style='font-size:2rem;font-weight:800;background:linear-gradient(135deg,#a78bfa,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent'>{analysis.get('salary_range','N/A')}</div>
                <div style='font-size:0.85rem;color:#9ca3af;margin-top:6px'>Based on your skills & experience level</div>
            </div>""", unsafe_allow_html=True)

        # ── TAB 2: DETAILED ANALYSIS ─────────────────────────────────────
        with tab2:
            s_col, w_col = st.columns(2)
            with s_col:
                st.markdown(f"<div class='section-card'><div class='feature-header'>✅ {t('strengths_label')}</div>", unsafe_allow_html=True)
                for s in analysis.get("strengths", []):
                    st.markdown(f"<span class='badge badge-green'>✓</span> {s}", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with w_col:
                st.markdown(f"<div class='section-card'><div class='feature-header'>⚠️ {t('weaknesses_label')}</div>", unsafe_allow_html=True)
                for w in analysis.get("weaknesses", []):
                    st.markdown(f"<span class='badge badge-red'>!</span> {w}", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(f"<div class='section-card'><div class='feature-header'>💡 {t('suggestions_label')}</div>", unsafe_allow_html=True)
            for i, sug in enumerate(analysis.get("improvement_suggestions", []), 1):
                st.markdown(f"<span class='badge badge-purple'>{i}</span> {sug}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            kw_col1, kw_col2 = st.columns(2)
            with kw_col1:
                if analysis.get("matched_keywords"):
                    st.markdown("<div class='section-card'><div class='feature-header'>✅ Matched Keywords</div>", unsafe_allow_html=True)
                    badges = " ".join([f"<span class='badge badge-green'>{kw}</span>" for kw in analysis["matched_keywords"]])
                    st.markdown(badges, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            with kw_col2:
                if analysis.get("missing_keywords"):
                    st.markdown(f"<div class='section-card'><div class='feature-header'>❌ {t('missing_keywords')}</div>", unsafe_allow_html=True)
                    for kw in analysis["missing_keywords"]:
                        imp = kw.get("importance", 5)
                        cls = "badge-red" if imp >= 8 else "badge-yellow" if imp >= 5 else "badge-blue"
                        st.markdown(f"<span class='badge {cls}'>{kw['keyword']} · {imp}/10</span>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

        # ── TAB 3: RESUME SUMMARY ────────────────────────────────────────
        with tab3:
            st.markdown(f"<div class='section-card'><div class='feature-header'>✍️ {t('summary_label')}</div>", unsafe_allow_html=True)
            st.info(analysis.get("rewritten_summary", ""))
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            pdf_buf = generate_pdf_report(analysis, resume_text, job_desc_saved)
            st.success(f"📥 {t('report_ready')}")
            st.download_button(
                label=t("download_report"),
                data=pdf_buf,
                file_name="resume_analysis_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        # ── TAB 4: INTERVIEW PREP ────────────────────────────────────────
        with tab4:
            st.markdown(f"<div class='feature-header'>🎤 Interview Preparation</div>", unsafe_allow_html=True)
            st.markdown("Generate 10 likely interview questions with ideal answers based on your resume and the job.")

            if st.button(t("gen_interview"), use_container_width=True):
                with st.spinner(t("generating")):
                    try:
                        st.session_state["interview_data"] = generate_interview_questions(resume_text, job_desc_saved)
                    except Exception as e:
                        st.error(f"Error: {e}")

            if st.session_state.get("interview_data"):
                qs = st.session_state["interview_data"].get("questions", [])
                for i, qa in enumerate(qs, 1):
                    cat = qa.get("category", "General")
                    cls = "badge-purple" if cat == "Behavioral" else "badge-blue" if cat == "Technical" else "badge-yellow"
                    st.markdown(f"""<div class='qa-card'>
                        <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px'>
                            <strong style='font-size:1rem'>Q{i}. {qa.get('question','')}</strong>
                            <span class='badge {cls}'>{cat}</span>
                        </div>
                        <div style='color:#9ca3af;font-size:0.85rem;margin-top:6px;line-height:1.6'>💬 {qa.get('answer','')}</div>
                    </div>""", unsafe_allow_html=True)

        # ── TAB 5: CAREER ROADMAP ────────────────────────────────────────
        with tab5:
            st.markdown(f"<div class='feature-header'>🗺️ Career Roadmap</div>", unsafe_allow_html=True)
            st.markdown("Get a personalized 6-month plan to bridge the gap between your current skills and the job requirements.")

            if st.button(t("gen_roadmap"), use_container_width=True):
                with st.spinner(t("generating")):
                    try:
                        st.session_state["roadmap_data"] = generate_career_roadmap(resume_text, job_desc_saved)
                    except Exception as e:
                        st.error(f"Error: {e}")

            if st.session_state.get("roadmap_data"):
                rd = st.session_state["roadmap_data"]

                top_skills = rd.get("top_skills_to_learn", [])
                if top_skills:
                    st.markdown("<div style='margin:16px 0 8px;font-weight:600'>🎯 Top Skills to Learn</div>", unsafe_allow_html=True)
                    badges = " ".join([f"<span class='badge badge-purple'>{s}</span>" for s in top_skills])
                    st.markdown(badges, unsafe_allow_html=True)

                certs = rd.get("recommended_certifications", [])
                if certs:
                    st.markdown("<div style='margin:16px 0 8px;font-weight:600'>🏆 Recommended Certifications</div>", unsafe_allow_html=True)
                    badges = " ".join([f"<span class='badge badge-blue'>{c}</span>" for c in certs])
                    st.markdown(badges, unsafe_allow_html=True)

                st.markdown("<div style='margin:20px 0 12px;font-weight:600;font-size:1.1rem'>📅 6-Month Plan</div>", unsafe_allow_html=True)
                for step in rd.get("roadmap", []):
                    skills_html = " ".join([f"<span class='badge badge-green'>{s}</span>" for s in step.get("skills", [])])
                    resources_html = " ".join([f"<span class='badge badge-yellow'>{r}</span>" for r in step.get("resources", [])])
                    st.markdown(f"""<div class='roadmap-step'>
                        <div style='min-width:100px;font-weight:700;color:#60a5fa'>{step.get('month','')}</div>
                        <div style='flex:1'>
                            <div style='font-weight:600;margin-bottom:6px'>{step.get('focus','')}</div>
                            <div style='margin-bottom:4px'>{skills_html}</div>
                            <div style='margin-bottom:6px'>{resources_html}</div>
                            <div style='font-size:0.8rem;color:#10b981'>🎯 Milestone: {step.get('milestone','')}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)

        # ── TAB 6: AI CONTENT ────────────────────────────────────────────
        with tab6:
            st.markdown(f"<div class='feature-header'>✨ AI-Generated Content</div>", unsafe_allow_html=True)

            li_col, cv_col = st.columns(2)
            with li_col:
                st.markdown("**🔗 LinkedIn Bio Generator**")
                st.markdown("<div style='font-size:0.85rem;color:#9ca3af;margin-bottom:12px'>Auto-generate a compelling LinkedIn About section</div>", unsafe_allow_html=True)
                if st.button(t("gen_linkedin"), use_container_width=True):
                    with st.spinner(t("generating")):
                        try:
                            st.session_state["linkedin_bio"] = generate_linkedin_bio(resume_text, analysis)
                        except Exception as e:
                            st.error(f"Error: {e}")
                if st.session_state.get("linkedin_bio"):
                    st.markdown(f"<div class='section-card' style='margin-top:12px'>{st.session_state['linkedin_bio']}</div>", unsafe_allow_html=True)
                    st.download_button("⬇️ Download LinkedIn Bio", st.session_state["linkedin_bio"],
                                       file_name="linkedin_bio.txt", mime="text/plain")

            with cv_col:
                st.markdown("**📝 Cover Letter Generator**")
                st.markdown("<div style='font-size:0.85rem;color:#9ca3af;margin-bottom:12px'>Auto-generate a tailored cover letter for this job</div>", unsafe_allow_html=True)
                if st.button(t("gen_cover"), use_container_width=True):
                    with st.spinner(t("generating")):
                        try:
                            st.session_state["cover_letter"] = generate_cover_letter(resume_text, job_desc_saved, analysis)
                        except Exception as e:
                            st.error(f"Error: {e}")
                if st.session_state.get("cover_letter"):
                    st.markdown(f"<div class='section-card' style='margin-top:12px'>{st.session_state['cover_letter']}</div>", unsafe_allow_html=True)
                    st.download_button("⬇️ Download Cover Letter", st.session_state["cover_letter"],
                                       file_name="cover_letter.txt", mime="text/plain")


if __name__ == "__main__":
    main()
