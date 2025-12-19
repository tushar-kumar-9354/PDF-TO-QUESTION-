import os
import time
import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai
from dotenv import load_dotenv

# ===================== ENV & GEMINI CONFIG =====================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("❌ GEMINI_API_KEY not found in .env file")
    st.stop()

# Configure Gemini ONCE
genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-2.0-flash"  # faster + stable

# ===================== PDF UTILS =====================

def extract_text_from_pdf(pdf_file, max_chars=6000):
    """Extract and LIMIT text from PDF to avoid timeout."""
    reader = PdfReader(pdf_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
        if len(text) >= max_chars:
            break

    return text[:max_chars]

# ===================== GEMINI LOGIC =====================

def generate_questions(pdf_text, retries=2):
    """Generate top 5 important questions using Gemini AI (timeout safe)."""

    prompt = f"""
Generate exactly 5 IMPORTANT, OPEN-ENDED questions
that help understand the core concepts of the document.

Rules:
- No MCQs
- No answers
- Clear and concise questions

DOCUMENT CONTENT:
{pdf_text}
"""

    model = genai.GenerativeModel(MODEL_NAME)

    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)

            if response and hasattr(response, "text"):
                return response.text.strip()

        except Exception as e:
            if "DeadlineExceeded" in str(e):
                time.sleep(2)  # small backoff
            else:
                return f"❌ Error: {str(e)}"

    return "❌ Gemini timed out. Try a smaller PDF."

# ===================== STREAMLIT UI =====================

def main():
    st.set_page_config(
        page_title="PDF Important Question Extractor",
        layout="wide"
    )

    st.title("📄 PDF Important Question Extractor (Gemini AI)")
    st.write(
        "Upload a PDF and generate **Top 5 Important Questions** safely."
    )

    pdf_file = st.file_uploader("Upload a PDF", type=["pdf"])

    if pdf_file:
        pdf_text = extract_text_from_pdf(pdf_file)

        st.subheader("📌 PDF Content Preview (Limited)")
        st.text_area(
            "PDF Text",
            pdf_text,
            height=200
        )

        if st.button("🚀 Generate Important Questions"):
            with st.spinner("Generating questions..."):
                questions = generate_questions(pdf_text)

            st.subheader("✅ Top 5 Important Questions")
            st.write(questions)

# ===================== RUN =====================

main()
