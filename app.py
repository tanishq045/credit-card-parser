import streamlit as st
import tempfile
import os
from banks import parse_pdf, extract_text_from_pdf

st.set_page_config(layout="wide")
st.title("💳 Credit Card Statement Parser")
st.write("Upload a PDF statement from Axis, HDFC, ICICI, IDFC, or Syndicate Bank to extract key information.")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Save the uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_pdf_path = tmp.name

    try:
        # Process the PDF
        with st.spinner('Parsing statement...'):
            parsed_data = parse_pdf(tmp_pdf_path)
        
        st.success("✅ Parsing Complete!")
        
        # Display the extracted data
        st.subheader("Extracted Data")
        st.json(parsed_data)

        # Optional: Show raw text for debugging
        with st.expander("Show Raw Extracted Text"):
            raw_text = extract_text_from_pdf(tmp_pdf_path)
            st.text_area("Raw Text", raw_text, height=300)

    except Exception as e:
        st.error(f"An error occurred during parsing: {e}")
        st.error("This might be an unsupported bank or a new statement format.")
    
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_pdf_path):
            os.remove(tmp_pdf_path)
