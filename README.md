Credit Card Statement Parser

Objective

This project is a Python-based PDF parser designed to extract key data points from credit card statements across 5 major Indian credit card issuers.

The parser handles varied PDF layouts and uses regular expressions to find and extract the required information.

Project Structure

credit-card-parser/
├── sample_input_pdfs/   # Sample PDFs for testing
│   ├── AXIS.pdf
│   ├── HDFC.pdf
│   ├── ICICI.pdf
│   ├── IDFC.pdf
│   └── SYN.pdf
├── app.py               # Interactive Streamlit web app
├── banks.py             # Core parsing logic and regex
├── test.py              # Command-line script to test all sample PDFs
├── .gitignore           # Files and folders to ignore for Git
├── README.md            # This file
└── requirements.txt     # Project dependencies


Features

Supports 5 Major Banks:

Axis Bank

HDFC Bank

ICICI Bank

IDFC First Bank

Syndicate Bank

Data Extraction: The parser extracts 10 data points:

Bank Name

Cardholder Name

Card Last 4 Digits

Statement Date

Payment Due Date

Total Amount Due

Minimum Amount Due

Credit Limit

Available Credit Limit

Statement Period (Start & End)

How to Run

1. Installation

The project requires Python 3.

Clone this repository.

Install the required dependencies:

pip install -r requirements.txt


2. Run the Command-Line Test

To verify the parser against all sample PDFs in the sample_input_pdfs folder, run test.py:

python test.py


3. Run the Interactive Web App

To start the Streamlit web application for an interactive demonstration:

streamlit run app.py


This will open a page in your web browser where you can upload a PDF and see the results instantly.