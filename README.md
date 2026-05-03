# 🚀 AI Resume Analyzer & Job Matcher

<div align="center">

![AI Resume Analyzer](https://img.shields.io/badge/AI-Resume%20Analyzer-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**An AI-powered resume analyzer that helps job seekers match their resume to job descriptions using Groq LLaMA 3.3**

[🌐 Live Demo](https://ai-resume-analyzer-hjtow7scxs239j38hzsmat.streamlit.app) • [📋 Report Bug](https://github.com/Rahul915564/AI-Resume-Analyzer/issues) • [✨ Request Feature](https://github.com/Rahul915564/AI-Resume-Analyzer/issues)

</div>

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 📊 **ATS Score** | Get an ATS compatibility score out of 100 |
| 🎯 **Skills Match** | Visual skills match overview with radar charts |
| 🔍 **Detailed Analysis** | Strengths, weaknesses, missing keywords |
| 🎤 **Interview Prep** | 10 AI-generated interview questions with answers |
| 🗺️ **Career Roadmap** | Personalized 6-month learning plan |
| ✍️ **LinkedIn Bio** | Auto-generate your LinkedIn summary |
| 📝 **Cover Letter** | AI-written cover letter for the job |
| 📄 **PDF Report** | Download full analysis as PDF |
| 🌙 **Dark/Light Mode** | Beautiful Glassmorphism UI |
| 🌐 **Hindi Support** | Bilingual (English/Hindi) interface |

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit + Custom CSS (Glassmorphism UI)
- **AI Engine**: Groq API — LLaMA 3.3 70B Versatile
- **PDF Parsing**: PyPDF2
- **Charts**: Plotly (Gauge, Radar, Bar)
- **PDF Export**: ReportLab
- **Language**: Python 3.11

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Rahul915564/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your Groq API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> Get your free API key at [console.groq.com](https://console.groq.com)

### 4. Run the app

```bash
streamlit run app.py
```

---

## 📋 Requirements

```
streamlit==1.32.0
groq==0.4.2
PyPDF2==3.0.1
plotly==5.18.0
reportlab==4.1.0
python-dotenv==1.0.0
httpx
```

---

## 🎯 How to Use

1. **Upload Resume** — Upload your resume as a PDF file
2. **Paste Job Description** — Copy and paste the target job description
3. **Click Analyze** — Let the AI analyze your resume
4. **Review Results** — Check your ATS score, skills match, and detailed feedback
5. **Download Report** — Export the full analysis as a PDF

---

## 📸 Screenshots

| Dark Mode | Light Mode |
|-----------|------------|
| Glassmorphism dark UI with purple/blue gradients | Clean light gray cards with visible borders |

---

## 🤖 AI Features

- **ATS Scoring** — Rates resume compatibility against the job description
- **Skills Radar** — Visual breakdown across Technical, Experience, Education, Projects, Formatting
- **Salary Estimate** — AI-predicted salary range based on skills and level
- **Career Level Detection** — Junior / Mid-Level / Senior / Lead / Executive
- **Missing Keywords** — Prioritized list of keywords to add
- **Interview Questions** — 10 Behavioral, Technical, and Situational Q&A pairs
- **6-Month Roadmap** — Month-by-month skill-building plan with resources and milestones
- **LinkedIn Bio** — First-person professional summary ready to paste
- **Cover Letter** — Tailored, job-specific cover letter under 400 words

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙌 Author

**Rahul** — [@Rahul915564](https://github.com/Rahul915564)

---

<div align="center">
Made with ❤️ using Groq LLaMA 3.3 & Streamlit
</div>
