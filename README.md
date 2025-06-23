# 🛡️ Vulnera — AI-Powered Code Vulnerability Scanner

**Vulnera** is a full-stack web application that allows users to upload a code folder or file for AI-assisted vulnerability scanning. It performs:

- 🔍 Static keyword-based analysis for potentially dangerous code patterns
- 🤖 AI (LLM) summarization of project and file intentions
- 🧠 Final LLM-based risk assessment with explanations per file
- ✅ Privacy-first: no summaries or findings are saved — your code stays private

---

## 📦 Features

- Upload entire code folders or individual files
- Multi-language support (Python, JS, Java, C/C++, C#, SQL, HTML, CSS, Go, Rust, Elixir, and more)
- Keyword-based static detection layer
- OpenAI GPT-4o-powered summarization and security analysis
- Modern UI built with React + Vite
- FastAPI backend API
- Uploads handled with streaming ZIP compression (no storage)
- Summary + danger decision per file and overall project

---

## 🌐 Live Demo

> [🔗 Try the app here](https://vulnera-5msn.onrender.com/)  
> (Frontend on Render, Backend on Render)

---
## Backend
- cd backend
- python -m venv .venv
- source .venv/bin/activate  # or .venv\Scripts\activate on Windows
- pip install -r requirements.txt
- uvicorn app.main:app --reload
---
## Frontend
- cd frontend
- npm install
- npm run dev


