import streamlit as st
import os
import json
import plotly.graph_objects as go
import plotly.express as px
from dotenv import load_dotenv
import PyPDF2
import httpx
from groq import Groq
from fpdf import FPDF
import io
import re
import tempfile

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")


def get_ai_response(prompt):
    client = Groq(
        api_key=GROQ_API_KEY,
        http_client=httpx.Client()
    )
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

st.set_page_config(
    page_title="AI Resume Analyzer & Job Matcher",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

TRANSLATIONS = {
    "en": {
        "title": "AI Resume Analyzer & Job Matcher",
        "subtitle": "Powered by Google Gemini AI",
        "upload_resume": "Upload Your Resume (PDF)",
        "job_description": "Paste Job Description",
        "job_desc_placeholder": "Paste the full job description here...",
        "analyze_btn": "Analyze Resume",
        "analyzing": "Analyzing your resume with AI...",
        "ats_score": "ATS Score",
        "skills_match": "Skills Match",
        "missing_keywords": "Missing Keywords",
        "strengths": "Strengths",
        "weaknesses": "Weaknesses",
        "suggestions": "Improvement Suggestions",
        "rewritten_summary": "Rewritten Resume Summary",
        "download_report": "Download Analysis Report (PDF)",
        "language_toggle": "Language / भाषा",
        "no_api_key": "Please set your GROQ_API_KEY environment variable.",
        "no_resume": "Please upload a resume PDF.",
        "no_job_desc": "Please paste a job description.",
        "upload_help": "Supported format: PDF only",
        "results_header": "Analysis Results",
        "overview": "Overview",
        "detailed": "Detailed Analysis",
        "resume_summary_tab": "Resume Summary",
        "score_gauge": "ATS Compatibility Score",
        "match_radar": "Skills Match Overview",
        "keywords_chart": "Missing Keywords Impact",
        "strengths_label": "Key Strengths",
        "weaknesses_label": "Areas to Improve",
        "suggestions_label": "Actionable Suggestions",
        "summary_label": "AI-Rewritten Professional Summary",
        "sidebar_title": "How It Works",
        "sidebar_step1": "1. Upload your resume PDF",
        "sidebar_step2": "2. Paste the job description",
        "sidebar_step3": "3. Click Analyze Resume",
        "sidebar_step4": "4. Review AI-powered insights",
        "sidebar_step5": "5. Download your report",
        "report_ready": "Your PDF report is ready!",
        "error_parse": "Could not parse AI response. Please try again.",
        "resume_preview": "Resume Text Preview",
    },
    "hi": {
        "title": "AI रिज्यूमे विश्लेषक और जॉब मैचर",
        "subtitle": "Google Gemini AI द्वारा संचालित",
        "upload_resume": "अपना रिज्यूमे अपलोड करें (PDF)",
        "job_description": "जॉब विवरण पेस्ट करें",
        "job_desc_placeholder": "यहाँ पूरा जॉब विवरण पेस्ट करें...",
        "analyze_btn": "रिज्यूमे का विश्लेषण करें",
        "analyzing": "AI से आपके रिज्यूमे का विश्लेषण हो रहा है...",
        "ats_score": "ATS स्कोर",
        "skills_match": "कौशल मिलान",
        "missing_keywords": "गायब कीवर्ड",
        "strengths": "ताकत",
        "weaknesses": "कमज़ोरियां",
        "suggestions": "सुधार सुझाव",
        "rewritten_summary": "फिर से लिखा गया रिज्यूमे सारांश",
        "download_report": "विश्लेषण रिपोर्ट डाउनलोड करें (PDF)",
        "language_toggle": "Language / भाषा",
        "no_api_key": "कृपया अपना GROQ_API_KEY सेट करें।",
        "no_resume": "कृपया एक रिज्यूमे PDF अपलोड करें।",
        "no_job_desc": "कृपया जॉब विवरण पेस्ट करें।",
        "upload_help": "समर्थित प्रारूप: केवल PDF",
        "results_header": "विश्लेषण परिणाम",
        "overview": "अवलोकन",
        "detailed": "विस्तृत विश्लेषण",
        "resume_summary_tab": "रिज्यूमे सारांश",
        "score_gauge": "ATS संगतता स्कोर",
        "match_radar": "कौशल मिलान अवलोकन",
        "keywords_chart": "गायब कीवर्ड प्रभाव",
        "strengths_label": "मुख्य ताकत",
        "weaknesses_label": "सुधार के क्षेत्र",
        "suggestions_label": "कार्रवाई योग्य सुझाव",
        "summary_label": "AI-पुनर्लिखित पेशेवर सारांश",
        "sidebar_title": "यह कैसे काम करता है",
        "sidebar_step1": "1. अपना रिज्यूमे PDF अपलोड करें",
        "sidebar_step2": "2. जॉब विवरण पेस्ट करें",
        "sidebar_step3": "3. रिज्यूमे विश्लेषण करें पर क्लिक करें",
        "sidebar_step4": "4. AI-संचालित अंतर्दृष्टि की समीक्षा करें",
        "sidebar_step5": "5. अपनी रिपोर्ट डाउनलोड करें",
        "report_ready": "आपकी PDF रिपोर्ट तैयार है!",
        "error_parse": "AI प्रतिक्रिया पार्स नहीं हो सकी। कृपया पुनः प्रयास करें।",
        "resume_preview": "रिज्यूमे टेक्स्ट पूर्वावलोकन",
    }
}


def t(key):
    lang = st.session_state.get("lang", "en")
    return TRANSLATIONS[lang].get(key, TRANSLATIONS["en"].get(key, key))


def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()


def analyze_resume_with_gemini(resume_text, job_description):
    prompt = f"""
You are an expert ATS (Applicant Tracking System) and career coach. Analyze the following resume against the job description and return a detailed JSON analysis.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return ONLY a valid JSON object (no markdown, no code blocks) with this exact structure:
{{
  "ats_score": <integer 0-100>,
  "skills_match_percentage": <integer 0-100>,
  "missing_keywords": [
    {{"keyword": "string", "importance": <integer 1-10>}}
  ],
  "matched_keywords": ["string"],
  "strengths": ["string"],
  "weaknesses": ["string"],
  "improvement_suggestions": ["string"],
  "rewritten_summary": "string",
  "category_scores": {{
    "Technical Skills": <integer 0-100>,
    "Experience": <integer 0-100>,
    "Education": <integer 0-100>,
    "Keywords": <integer 0-100>,
    "Formatting": <integer 0-100>
  }}
}}
"""
    raw = get_ai_response(prompt).strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"```$", "", raw)
    return json.loads(raw)


def render_ats_gauge(score, label):
    color = "#e74c3c" if score < 40 else "#f39c12" if score < 70 else "#2ecc71"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": label, "font": {"size": 18}},
        number={"suffix": "/100", "font": {"size": 36}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 40], "color": "#fde8e8"},
                {"range": [40, 70], "color": "#fef9e7"},
                {"range": [70, 100], "color": "#eafaf1"},
            ],
            "threshold": {
                "line": {"color": color, "width": 4},
                "thickness": 0.75,
                "value": score,
            },
        },
    ))
    fig.update_layout(height=300, margin=dict(t=40, b=20, l=20, r=20))
    return fig


def render_radar_chart(category_scores, label):
    categories = list(category_scores.keys())
    values = list(category_scores.values())
    values.append(values[0])
    categories.append(categories[0])

    fig = go.Figure(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        fillcolor="rgba(52, 152, 219, 0.2)",
        line=dict(color="rgba(52, 152, 219, 0.9)", width=2),
        marker=dict(size=6, color="rgba(52, 152, 219, 1)"),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10))
        ),
        title=dict(text=label, font=dict(size=16)),
        height=380,
        margin=dict(t=60, b=20, l=40, r=40),
        showlegend=False,
    )
    return fig


def render_keywords_bar(missing_keywords):
    if not missing_keywords:
        return None
    keywords = [k["keyword"] for k in missing_keywords[:12]]
    importance = [k["importance"] for k in missing_keywords[:12]]
    colors = ["#e74c3c" if i >= 8 else "#f39c12" if i >= 5 else "#3498db" for i in importance]
    fig = go.Figure(go.Bar(
        x=importance,
        y=keywords,
        orientation="h",
        marker_color=colors,
        text=importance,
        textposition="outside",
    ))
    fig.update_layout(
        title=dict(text=t("keywords_chart"), font=dict(size=16)),
        xaxis=dict(title="Importance (1-10)", range=[0, 12]),
        yaxis=dict(autorange="reversed"),
        height=max(300, len(keywords) * 36),
        margin=dict(t=60, b=40, l=20, r=60),
    )
    return fig


def generate_pdf_report(analysis, resume_text, job_desc):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 12, "AI Resume Analyzer - Analysis Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(127, 140, 141)
    pdf.cell(0, 8, "Powered by Google Gemini AI", ln=True, align="C")
    pdf.ln(6)

    pdf.set_draw_color(52, 152, 219)
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    def section_header(title):
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(41, 128, 185)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_text_color(44, 62, 80)

    def body_text(text):
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(44, 62, 80)
        safe = text.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 7, safe)

    def bullet_list(items, label=""):
        if label:
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(44, 62, 80)
            pdf.cell(0, 8, label, ln=True)
        pdf.set_font("Helvetica", "", 11)
        for item in items:
            safe = f"  • {item}".encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(0, 7, safe)
        pdf.ln(2)

    section_header("Score Summary")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(90, 9, f"ATS Score: {analysis['ats_score']}/100", border=1, align="C")
    pdf.cell(90, 9, f"Skills Match: {analysis['skills_match_percentage']}%", border=1, align="C", ln=True)
    pdf.ln(6)

    section_header("Category Scores")
    for cat, score in analysis.get("category_scores", {}).items():
        pdf.set_font("Helvetica", "", 11)
        bar_width = int(score * 1.4)
        pdf.set_fill_color(46, 204, 113) if score >= 70 else pdf.set_fill_color(243, 156, 18) if score >= 40 else pdf.set_fill_color(231, 76, 60)
        pdf.cell(60, 7, f"  {cat}", ln=False)
        pdf.cell(bar_width, 7, "", fill=True, ln=False)
        pdf.cell(0, 7, f" {score}%", ln=True)
    pdf.ln(4)

    section_header("Strengths")
    bullet_list(analysis.get("strengths", []))

    section_header("Weaknesses")
    bullet_list(analysis.get("weaknesses", []))

    section_header("Improvement Suggestions")
    bullet_list(analysis.get("improvement_suggestions", []))

    section_header("Missing Keywords")
    kw_list = [f"{k['keyword']} (importance: {k['importance']}/10)" for k in analysis.get("missing_keywords", [])]
    bullet_list(kw_list)

    section_header("AI-Rewritten Professional Summary")
    body_text(analysis.get("rewritten_summary", ""))

    output = io.BytesIO()
    pdf_bytes = pdf.output()
    output.write(bytes(pdf_bytes))
    output.seek(0)
    return output


def main():
    if "lang" not in st.session_state:
        st.session_state["lang"] = "en"
    if "analysis" not in st.session_state:
        st.session_state["analysis"] = None
    if "resume_text" not in st.session_state:
        st.session_state["resume_text"] = ""

    with st.sidebar:
        st.markdown(f"### {t('language_toggle')}")
        lang_choice = st.radio(
            "Select Language",
            options=["English", "हिंदी"],
            index=0 if st.session_state["lang"] == "en" else 1,
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state["lang"] = "en" if lang_choice == "English" else "hi"

        st.markdown("---")
        st.markdown(f"### {t('sidebar_title')}")
        st.markdown(f"""
{t('sidebar_step1')}  
{t('sidebar_step2')}  
{t('sidebar_step3')}  
{t('sidebar_step4')}  
{t('sidebar_step5')}
""")
        st.markdown("---")
        if not GROQ_API_KEY:
            st.error(t("no_api_key"))

    st.title(f"📄 {t('title')}")
    st.caption(t("subtitle"))
    st.markdown("---")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader(f"📤 {t('upload_resume')}")
        uploaded_file = st.file_uploader(
            "Upload Resume PDF",
            type=["pdf"],
            help=t("upload_help"),
            label_visibility="collapsed",
        )
        if uploaded_file:
            with st.expander(t("resume_preview"), expanded=False):
                text = extract_text_from_pdf(uploaded_file)
                st.text_area("Resume Text", text[:3000] + ("..." if len(text) > 3000 else ""), height=200, label_visibility="collapsed")
            st.session_state["resume_text"] = text
            st.success(f"✅ Resume loaded — {len(text)} characters extracted")

    with col2:
        st.subheader(f"📋 {t('job_description')}")
        job_desc = st.text_area(
            "Job Description",
            placeholder=t("job_desc_placeholder"),
            height=220,
            label_visibility="collapsed",
        )

    st.markdown("")
    analyze_col = st.columns([1, 2, 1])[1]
    with analyze_col:
        analyze_btn = st.button(
            f"🔍 {t('analyze_btn')}",
            use_container_width=True,
            type="primary",
        )

    if analyze_btn:
        if not GROQ_API_KEY:
            st.error(t("no_api_key"))
        elif not st.session_state.get("resume_text"):
            st.warning(t("no_resume"))
        elif not job_desc.strip():
            st.warning(t("no_job_desc"))
        else:
            with st.spinner(t("analyzing")):
                progress = st.progress(0)
                import time
                for i in range(0, 60, 10):
                    time.sleep(0.1)
                    progress.progress(i)
                try:
                    analysis = analyze_resume_with_gemini(
                        st.session_state["resume_text"], job_desc
                    )
                    for i in range(60, 101, 10):
                        time.sleep(0.05)
                        progress.progress(i)
                    st.session_state["analysis"] = analysis
                    st.session_state["job_desc"] = job_desc
                    progress.empty()
                except json.JSONDecodeError:
                    progress.empty()
                    st.error(t("error_parse"))
                except Exception as e:
                    progress.empty()
                    st.error(f"Error: {e}")

    if st.session_state.get("analysis"):
        analysis = st.session_state["analysis"]
        st.markdown("---")
        st.subheader(f"📊 {t('results_header')}")

        tab1, tab2, tab3 = st.tabs([
            f"📈 {t('overview')}",
            f"🔍 {t('detailed')}",
            f"✍️ {t('resume_summary_tab')}",
        ])

        with tab1:
            m1, m2, m3 = st.columns(3)
            with m1:
                score = analysis["ats_score"]
                color = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
                st.metric(f"{color} {t('ats_score')}", f"{score}/100")
            with m2:
                match = analysis["skills_match_percentage"]
                color = "🟢" if match >= 70 else "🟡" if match >= 40 else "🔴"
                st.metric(f"{color} {t('skills_match')}", f"{match}%")
            with m3:
                missing_count = len(analysis.get("missing_keywords", []))
                st.metric(f"🔑 {t('missing_keywords')}", str(missing_count))

            g_col, r_col = st.columns(2)
            with g_col:
                st.plotly_chart(
                    render_ats_gauge(analysis["ats_score"], t("score_gauge")),
                    use_container_width=True,
                )
            with r_col:
                if analysis.get("category_scores"):
                    st.plotly_chart(
                        render_radar_chart(analysis["category_scores"], t("match_radar")),
                        use_container_width=True,
                    )

            if analysis.get("missing_keywords"):
                kw_fig = render_keywords_bar(analysis["missing_keywords"])
                if kw_fig:
                    st.plotly_chart(kw_fig, use_container_width=True)

        with tab2:
            s_col, w_col = st.columns(2)
            with s_col:
                st.markdown(f"#### ✅ {t('strengths_label')}")
                for s in analysis.get("strengths", []):
                    st.markdown(f"- {s}")

            with w_col:
                st.markdown(f"#### ⚠️ {t('weaknesses_label')}")
                for w in analysis.get("weaknesses", []):
                    st.markdown(f"- {w}")

            st.markdown(f"#### 💡 {t('suggestions_label')}")
            for i, suggestion in enumerate(analysis.get("improvement_suggestions", []), 1):
                st.markdown(f"**{i}.** {suggestion}")

            if analysis.get("matched_keywords"):
                st.markdown("#### ✅ Matched Keywords")
                cols = st.columns(4)
                for idx, kw in enumerate(analysis["matched_keywords"]):
                    cols[idx % 4].success(kw)

            if analysis.get("missing_keywords"):
                st.markdown(f"#### ❌ {t('missing_keywords')}")
                cols = st.columns(4)
                for idx, kw in enumerate(analysis["missing_keywords"]):
                    importance = kw.get("importance", 5)
                    label = f"{kw['keyword']} ({importance}/10)"
                    if importance >= 8:
                        cols[idx % 4].error(label)
                    elif importance >= 5:
                        cols[idx % 4].warning(label)
                    else:
                        cols[idx % 4].info(label)

        with tab3:
            st.markdown(f"#### ✍️ {t('summary_label')}")
            st.info(analysis.get("rewritten_summary", ""))

        st.markdown("---")
        pdf_bytes = generate_pdf_report(
            analysis,
            st.session_state.get("resume_text", ""),
            st.session_state.get("job_desc", ""),
        )
        st.success(f"📥 {t('report_ready')}")
        st.download_button(
            label=f"⬇️ {t('download_report')}",
            data=pdf_bytes,
            file_name="resume_analysis_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
