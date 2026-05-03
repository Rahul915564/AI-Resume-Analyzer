# AI Resume Analyzer & Job Matcher

An intelligent resume analysis tool powered by **Google Gemini AI** that evaluates your resume against job descriptions with ATS scoring, skill matching, and actionable improvement suggestions.

## Features

- PDF Resume Upload - Extracts text from your resume PDF
- Gemini AI Analysis - Deep analysis using Google Gemini 2.0 Flash
- ATS Score - Gauge chart showing your Applicant Tracking System compatibility (0-100)
- Skills Match - Radar chart comparing your skills to job requirements
- Missing Keywords - Bar chart of keywords to add to your resume
- Strengths and Weaknesses - Clear breakdown of your resume
- Improvement Suggestions - Actionable steps to improve your resume
- Rewritten Summary - AI-generated professional summary tailored to the job
- Hindi / English Toggle - Full bilingual UI support
- PDF Report Download - Download a formatted analysis report

## Tech Stack

- UI: Streamlit
- AI: Google Gemini 2.0 Flash (via google-genai)
- PDF Parsing: PyPDF2
- Charts: Plotly
- PDF Export: fpdf2

## Setup

1. Clone the repo
   git clone https://github.com/Rahul915564/AI-Resume-Analyzer.git
   cd AI-Resume-Analyzer

2. Install dependencies
   pip install streamlit google-genai PyPDF2 plotly fpdf2 python-dotenv

3. Set your Gemini API key
   export GEMINI_API_KEY=your_api_key_here
   Get your key at: https://aistudio.google.com/app/apikey

4. Run the app
   streamlit run app.py

## Usage

1. Upload your resume as a PDF
2. Paste the job description you want to target
3. Click Analyze Resume
4. Review your ATS score, matched/missing keywords, strengths and weaknesses
5. Download the PDF analysis report

## License

MIT License

