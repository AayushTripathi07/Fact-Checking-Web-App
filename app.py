import json
import fitz
import streamlit as st

from claim_extractor import extract_claims
from verifier import verify_claim

st.set_page_config(page_title="AI Fact Checker", layout="wide")

st.title("🧠 AI Fact-Checking Web App")
st.write("Upload a PDF. Claims will be extracted and verified using live web data.")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

if uploaded_file:
    with st.spinner("📄 Extracting text from PDF..."):
        pdf_text = extract_text_from_pdf(uploaded_file)

    with st.spinner("🔍 Extracting claims..."):
        raw = extract_claims(pdf_text)
        try:
            claims = json.loads(raw)
        except json.JSONDecodeError:
            st.error("Failed to parse claims.")
            claims = []

    if not claims:
        st.warning("No verifiable claims found.")
    else:
        st.subheader(f"Found {len(claims)} claims")

        for i, c in enumerate(claims, 1):
            st.markdown(f"### Claim {i}")
            st.write(c["claim"])

            with st.spinner("🌐 Verifying with live web data..."):
                result = verify_claim(c["claim"])

            status = result.get("status", "Unknown")

            if status == "Verified":
                st.success("✅ Verified")
            elif status == "Inaccurate":
                st.warning("⚠️ Inaccurate")
            elif status == "False":
                st.error("❌ False")
            else:
                st.info("❓ Unknown")

            st.write(result.get("explanation", ""))
            st.divider()
