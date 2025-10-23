# 💳 Credit Card Statement Parser

🚀 **Live Demo**  
You can try the parser live with your own PDF statements using the deployed Streamlit app:  
👉 [https://tanishq045-credit-card-parser-app-eqj5jo.streamlit.app/](https://tanishq045-credit-card-parser-app-eqj5jo.streamlit.app/)

---

## 🎯 Objective
This project is a **Python-based PDF parser** designed to extract key data points from credit card statements across **5 major Indian credit card issuers**.  
The parser handles varied PDF layouts and uses **regular expressions** to find and extract the required information.

---

## 🗂️ Project Structure

```
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
```

---

## ✨ Features

### 🔹 Supports 5 Major Banks
- Axis Bank  
- HDFC Bank  
- ICICI Bank  
- IDFC First Bank  
- Syndicate Bank  

### 🔹 Data Extraction
The parser extracts the following **10 key data points**:
1. Bank Name  
2. Cardholder Name  
3. Card Last 4 Digits  
4. Statement Date  
5. Payment Due Date  
6. Total Amount Due  
7. Minimum Amount Due  
8. Credit Limit  
9. Available Credit Limit  
10. Statement Period (Start & End)

---

## ⚙️ How to Run Locally

### 1️⃣ Installation
Make sure you have **Python 3** installed.  
Clone this repository and install dependencies:

```bash
pip install -r requirements.txt
```

---

### 2️⃣ Run the Command-Line Test
To verify the parser against all sample PDFs in the `sample_input_pdfs` folder, run:

```bash
python test.py
```

---

### 3️⃣ Run the Interactive Web App
To start the **Streamlit web application** locally, run:

```bash
streamlit run app.py
```

This will open a page in your web browser where you can upload a PDF and see the results instantly.

---
