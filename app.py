import os
import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai
from dotenv import load_dotenv

# ===================== ENV & GEMINI CONFIG =====================

# Load .env FIRST
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("❌ GEMINI_API_KEY not found in .env file")
    st.stop()

# Configure Gemini ONLY ONCE (Streamlit-safe)
genai.configure(api_key=GEMINI_API_KEY)

# ===================== PDF UTILS =====================

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file using PyPDF2."""
    reader = PdfReader(pdf_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text

# ===================== GEMINI LOGIC =====================

def generate_questions(pdf_text):
    """Generate top 5 important questions using Gemini AI."""

    prompt = f"""
You are an AI that extracts the most important questions from a document.

Read the following PDF content and generate the TOP 5 MOST IMPORTANT questions.
Rules:
- Questions must be open-ended
- Thought-provoking
- Concept-focused
- NO MCQs
- NO answers

PDF CONTENT:
{pdf_text}
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        if response and hasattr(response, "text"):
            return response.text.strip()
        else:
            return "⚠️ No response received from Gemini."

    except Exception as e:
        return f"❌ Error occurred: {str(e)}"

# ===================== STREAMLIT UI =====================

def main():
    st.set_page_config(
        page_title="PDF Important Question Extractor",
        layout="wide"
    )

    st.title("📄 PDF Important Question Extractor (Gemini AI)")
    st.write(
        "Upload a PDF file to extract its content and generate the **Top 5 most important questions**."
    )

    pdf_file = st.file_uploader("Upload a PDF", type=["pdf"])

    if pdf_file:
        pdf_text = extract_text_from_pdf(pdf_file)

        st.subheader("📌 Extracted PDF Content (Preview)")
        st.text_area(
            "PDF Text Preview",
            pdf_text[:500] + " ...",
            height=200
        )

        if st.button("🚀 Generate Important Questions"):
            with st.spinner("Generating questions using Gemini AI..."):
                questions = generate_questions(pdf_text)

            st.subheader("✅ Top 5 Important Questions")
            st.write(questions)

# ===================== ENTRY POINT =====================

# Streamlit automatically reruns this file — DO NOT use __main__ logic
main()
