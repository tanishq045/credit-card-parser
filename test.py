from banks import parse_pdf, extract_text_from_pdf, detect_bank
import re
import os

if __name__ == "__main__":
    # Define the folder containing the sample PDFs
    pdf_folder = "sample_input_pdfs"
    
    pdf_files_to_process = [
        "HDFC.pdf", 
        "AXIS.pdf", 
        "ICICI.pdf", 
        "IDFC.pdf", 
        "SYN.pdf"
    ]

    for pdf_file in pdf_files_to_process:
        # Create the full path to the PDF
        pdf_path = os.path.join(pdf_folder, pdf_file)
        
        if os.path.exists(pdf_path):
            print(f"--- Processing {pdf_path} ---")
            parsed_data = parse_pdf(pdf_path)
            print(parsed_data)
            print(f"--- Finished {pdf_file} ---\n")
        else:
            print(f"--- File not found: {pdf_path} ---\n")
