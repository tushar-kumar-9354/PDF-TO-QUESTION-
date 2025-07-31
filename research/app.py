import os
import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file using PyPDF2."""
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def generate_questions(pdf_text):
    """Generate top 5 important questions using Gemini AI."""
    prompt = (
        "You are an AI that extracts the most important questions from a document. "
        "Read the following PDF content and generate the **top 5 most important** questions "
        "that best summarize the key concepts and information. "
        "The questions should be open-ended, thought-provoking, and relevant to understanding the material. "
        "Do NOT generate multiple-choice questions. "
        "PDF Content:\n" + pdf_text
    )

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # Initialize model
        response = model.generate_content(prompt)

        if response and hasattr(response, 'text'):
            return response.text
        else:
            return "Error: No response from Gemini API"

    except Exception as e:
        return f"Error occurred: {str(e)}"

def main():
    st.set_page_config(page_title="PDF Important Question Extractor", layout="wide")
    st.title("PDF Important Question Extractor using Gemini API")
    st.write("Upload a PDF file to extract its content and generate the **top 5 most important** questions.")

    pdf_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if pdf_file is not None:
        pdf_text = extract_text_from_pdf(pdf_file)
        st.subheader("Extracted PDF Content (Preview)")
        st.text_area("PDF Text", pdf_text[:500] + " ...", height=200)

        if st.button("Generate Important Questions"):
            with st.spinner("Generating questions..."):
                questions = generate_questions(pdf_text)
            st.subheader("Top 5 Important Questions")
            st.write(questions)
            print(questions)  # Log questions to console for debugging
        print("PDF file uploaded and processed successfully.")

if __name__ == '__main__':
    print("Starting the PDF Question Extractor app...")
    print("Ensure you have set your API key in the .env file or directly in the code.")
    print("in app.py line 61 or in if __name__ == '__main__': replace 'own_api_key' with your actual API key.")
    genai.configure(api_key="own_api_key")  # Replace with your real API key
    main()
