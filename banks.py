import re
from typing import Dict, Any

try:
    import pdfplumber
except Exception:
    pdfplumber = None

def detect_bank(text):
    text_upper = text.upper()
    if "AXIS BANK" in text_upper:
        return "Axis Bank"
    elif "ICICI BANK" in text_upper:
        return "ICICI Bank"
    elif "IDFC FIRST BANK" in text_upper:
        return "IDFC First Bank"
    elif "SYNDICATE BANK" in text_upper or "GLOBAL CREDIT CARD" in text_upper:
        return "Syndicate Bank"
    elif "HDFC BANK" in text_upper:
        return "HDFC Bank"
    elif "SBI CARD" in text_upper or "STATE BANK OF INDIA" in text_upper:
        return "SBI Card"
    else:
        return "Unknown"


def parse_axis_bank(text):
    data = {
        "bank_name": "Axis Bank",
        "cardholder_name": None,
        "card_last_4": "",
        "total_amount_due": None,
        "minimum_amount_due": None,
        "statement_period_start": None,
        "statement_period_end": None,
        "payment_due_date": None,
        "statement_date": None,
        "credit_limit": "",
        "available_credit_limit": ""
    }

    # 1. Cardholder Name
    name_match = re.search(r'Name\s*[:\-]?\s*([A-Z][A-Z\s]+)', text)
    if not name_match:
        name_match = re.search(r'([A-Z][A-Z\s]+)\s+Statement', text)
    data["cardholder_name"] = name_match.group(1).strip() if name_match else None

    # 2. Card last 4 digits
    last4_match = re.search(r'(?:\*{4}|[Xx]{4})\s*(\d{4})', text)
    data["card_last_4"] = last4_match.group(1) if last4_match else ""

    # 3. Total Payment Due, Minimum Payment Due, Dates
    pattern = re.search(
        r'Total\s*Payment\s*Due.*?(\d{1,3}(?:,\d{3})*\.\d{2})\s*Dr'
        r'.*?Minimum\s*Payment\s*Due.*?(\d{1,3}(?:,\d{3})*\.\d{2})\s*Dr'
        r'.*?Statement\s*Period.*?(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})'
        r'.*?Payment\s*Due\s*Date.*?(\d{2}/\d{2}/\d{4})'
        r'.*?Statement\s*Generation\s*Date.*?(\d{2}/\d{2}/\d{4})',
        text,
        re.S
    )

    if pattern:
        data["total_amount_due"] = pattern.group(1)
        data["minimum_amount_due"] = pattern.group(2)
        data["statement_period_start"] = pattern.group(3)
        data["statement_period_end"] = pattern.group(4)
        data["payment_due_date"] = pattern.group(5)
        data["statement_date"] = pattern.group(6)
    else:
        # Backup pattern — sometimes missing labels
        fallback = re.search(
            r'(\d{1,3}(?:,\d{3})*\.\d{2})\s*Dr.*?(\d{1,3}(?:,\d{3})*\.\d{2})\s*Dr.*?(\d{2}/\d{2}/\d{4}).*?(\d{2}/\d{2}/\d{4}).*?(\d{2}/\d{2}/\d{4}).*?(\d{2}/\d{2}/\d{4})',
            text,
            re.S
        )
        if fallback:
            data["total_amount_due"] = fallback.group(1)
            data["minimum_amount_due"] = fallback.group(2)
            data["statement_period_start"] = fallback.group(3)
            data["statement_period_end"] = fallback.group(4)
            data["payment_due_date"] = fallback.group(5)
            data["statement_date"] = fallback.group(6)
        # else: fields remain None

    # 4. Credit Limits (Updated with new regex from AXIS_raw.txt)
    credit_match = re.search(
        r'Credit\s*Limit\s*Available\s*Credit\s*Limit'
        r'.*?' # Match any characters, including newlines
        r'([\d,]+\.\d{2})'  # Grp 1: Credit Limit
        r'\s*([\d,]+\.\d{2})', # Grp 2: Available Credit Limit
        text,
        re.DOTALL | re.IGNORECASE
    )
    if credit_match:
        data["credit_limit"] = credit_match.group(1).strip()
        data["available_credit_limit"] = credit_match.group(2).strip()

    return data

def parse_icici_bank(text):
    data = {
        "bank_name": "ICICI Bank",
        "cardholder_name": "",
        "card_last_4": "",
        "statement_date": "",
        "minimum_amount_due": "",
        "total_amount_due": "",
        "payment_due_date": "",
        "statement_period_start": "",
        "statement_period_end": "",
        "credit_limit": "",
        "available_credit_limit": ""
    }

    # Normalize weird dashes and backticks, but DO NOT collapse all whitespace.
    text = text.replace("—", "-")
    text = text.replace("`", " ") # Remove backticks seen in the raw text

    # 1. Cardholder name
    name_match = re.search(
        r'Customer\s*Name\s*(?:Card\s*Account\s*No)?\s+([A-Z][A-Z\s]+?)\s+\d{4}',
        text
    )
    data["cardholder_name"] = name_match.group(1).strip() if name_match else ""

    # 2. Card last 4 digits
    last4 = re.search(r'Card Number\s*:\s*[\dXx\s]+(\d{4})', text)
    if not last4:
        last4 = re.search(r'XXXX\s+(\d{4})', text)
    data["card_last_4"] = last4.group(1) if last4 else ""

    # 3. Statement Date, Minimum Due, Total Due
    pattern = re.search(
        r'Statement\s*Date\s*Minimum\s*Amount\s*Due\s*Your\s*Total\s*Amount\s*Due'
        r'.*?' # Match any characters, including newlines
        r'(\d{2}/\d{2}/\d{4})' # Grp 1: Statement Date
        r'\s*([\d,]+\.\d{2})'  # Grp 2: Minimum Amount
        r'.*?' # Match any characters, including newlines
        r'([\d,]+\.\d{2})',   # Grp 3: Total Amount
        text,
        re.DOTALL | re.IGNORECASE
    )
    
    if pattern:
        data["statement_date"] = pattern.group(1).strip()
        data["minimum_amount_due"] = pattern.group(2).strip()
        data["total_amount_due"] = pattern.group(3).strip()

    # 4. Payment due date
    due_date = re.search(r'Due\s*Date\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})', text)
    data["payment_due_date"] = due_date.group(1).strip() if due_date else ""

    # 5. Statement Period
    period_match = re.search(
        r'Statement\s*Period\s*:\s*From\s*(\d{2}/\d{2}/\d{4})\s*to\s*(\d{2}/\d{2}/\d{4})',
        text,
        re.IGNORECASE
    )
    if period_match:
        data["statement_period_start"] = period_match.group(1).strip()
        data["statement_period_end"] = period_match.group(2).strip()

    # 6. Credit Limits
    credit_match = re.search(
        r'Credit\s*Limit\s*Available\s*Credit'
        r'.*?' # Match any characters, including newlines
        r'([\d,]+\.\d{2})'  # Grp 1: Credit Limit
        r'\s*([\d,]+\.\d{2})', # Grp 2: Available Credit
        text,
        re.DOTALL | re.IGNORECASE
    )
    if credit_match:
        data["credit_limit"] = credit_match.group(1).strip()
        data["available_credit_limit"] = credit_match.group(2).strip()

    return data


def parse_idfc_bank(text):
    data = {
        "bank_name": "IDFC First Bank",
        "cardholder_name": "",
        "statement_date": "",
        "payment_due_date": "",
        "total_amount_due": "",
        "minimum_amount_due": "",
        "credit_limit": "",
        "available_credit_limit": "",
        "statement_period_start": "",
        "statement_period_end": "",
        "card_last_4": ""
    }
    
    # Normalize 'r' symbol as it might be 'r' or '₹' and standardize spacing
    text = re.sub(r'\s+[r₹]\s+', ' r ', text) 
    
    # 1. Cardholder name
    name_match = re.search(r'Customer Name\s*:\s*([A-Za-z\s]+?)\s*Card Number', text)
    if not name_match:
        name_match = re.search(r'^([A-Za-z\s]+?)\s*Statement Date', text, re.MULTILINE)
    data["cardholder_name"] = name_match.group(1).strip() if name_match else ""

    # 2. Card last 4 digits
    last4_match = re.search(r'Card Number\s*[:\s]*[\d*]+(\d{4})', text)
    data["card_last_4"] = last4_match.group(1).strip() if last4_match else ""

    # 3. Statement Date & Payment Due Date
    dates_match = re.search(
        r'Statement Date\s*Payment Due Date'
        r'.*?' # Match any characters, including newlines
        r'(\d{2}/\d{2}/\d{4})' # Grp 1: Statement Date
        r'\s*(\d{2}/\d{2}/\d{4})', # Grp 2: Payment Due Date
        text,
        re.DOTALL | re.IGNORECASE
    )
    if dates_match:
        data["statement_date"] = dates_match.group(1).strip()
        data["payment_due_date"] = dates_match.group(2).strip()

    # 4. Total Amount Due & Minimum Amount Due
    amounts_match = re.search(
        r'Total Amount Due\s*Minimum Amount Due'
        r'.*?' # Match any characters, including newlines
        r'r\s*([\d,]+\.\d{2})' # Grp 1: Total Amount Due
        r'\s*r\s*([\d,]+\.\d{2})', # Grp 2: Minimum Amount Due
        text,
        re.DOTALL | re.IGNORECASE
    )
    if amounts_match:
        data["total_amount_due"] = amounts_match.group(1).strip()
        data["minimum_amount_due"] = amounts_match.group(2).strip()

    # 5. Credit Limit & Available Credit Limit
    # The raw text has 'r 1,92,000' (no .00), so we make the decimals optional
    credit_match = re.search(
        r'Credit Limit\s*Available Credit Limit'
        r'.*?' # Match any characters, including newlines
        r'r\s*([\d,]+(?:\.\d{2})?)' # Grp 1: Credit Limit
        r'\s*r\s*([\d,]+(?:\.\d{2})?)', # Grp 2: Available Credit Limit
        text,
        re.DOTALL | re.IGNORECASE
    )
    if credit_match:
        data["credit_limit"] = credit_match.group(1).strip()
        data["available_credit_limit"] = credit_match.group(2).strip()

    # 6. Statement Period
    period_match = re.search(
        r'Statement Period'
        r'.*?'
        r'From:\s*(\d{2}/\d{2}/\d{4})\s*To:\s*(\d{2}/\d{2}/\d{4})',
        text,
        re.DOTALL | re.IGNORECASE
    )
    if period_match:
        data["statement_period_start"] = period_match.group(1).strip()
        data["statement_period_end"] = period_match.group(2).strip()

    return data

def parse_syndicate_bank(text):
    data = {
        "bank_name": "Syndicate Bank",
        "cardholder_name": "",
        "card_last_4": "",
        "statement_date": "",
        "payment_due_date": "",
        "total_amount_due": "",
        "minimum_amount_due": "",
        "credit_limit": "",
        "available_credit_limit": ""
    }

    # 1. Cardholder name
    name_match = re.search(r'Name\s*(MR\.\s*[A-Z\s]+?)\s*Credit Card No', text)
    data["cardholder_name"] = name_match.group(1).strip() if name_match else ""

    # 2. Amounts and Last 4 Digits
    amounts_match = re.search(
        r'Card Account Number\s*Total Payment Due\s*Minimum Payment Due'
        r'.*?' # Match any characters, including newlines
        r'(\d{4})\s*([\d,]+\.\d{2})\s*([\d,]+\.\d{2})',
        text,
        re.DOTALL | re.IGNORECASE
    )
    if amounts_match:
        data["card_last_4"] = amounts_match.group(1).strip()
        data["total_amount_due"] = amounts_match.group(2).strip()
        data["minimum_amount_due"] = amounts_match.group(3).strip()

    # 3. Dates (Format: DD MMM YYYY)
    dates_match = re.search(
        r'Statement Date\s*Payment Due Date'
        r'.*?' # Match any characters, including newlines
        r'(\d{2}\s[A-Z]{3}\s\d{4})' # Grp 1: Statement Date
        r'\s*(\d{2}\s[A-Z]{3}\s\d{4})', # Grp 2: Payment Due Date
        text,
        re.DOTALL | re.IGNORECASE
    )
    if dates_match:
        data["statement_date"] = dates_match.group(1).strip()
        data["payment_due_date"] = dates_match.group(2).strip()

    # 4. Credit Limits
    credit_match = re.search(
        r'Credit\s*Limit\s*Available\s*Credit\s*Limit'
        r'.*?' # Match any characters, including newlines
        r'([\d,]+\.\d{2})'  # Grp 1: Credit Limit
        r'\s*([\d,]+\.\d{2})', # Grp 2: Available Credit Limit
        text,
        re.DOTALL | re.IGNORECASE
    )
    if credit_match:
        data["credit_limit"] = credit_match.group(1).strip()
        data["available_credit_limit"] = credit_match.group(2).strip()

    # 5. Fallback for last 4, if not in the amounts block
    if not data["card_last_4"]:
        last4_match = re.search(r'Credit Card No\s*[\dXx\s]+(\d{4})', text)
        data["card_last_4"] = last4_match.group(1).strip() if last4_match else ""

    return data

def parse_hdfc_bank(text: str) -> Dict[str, Any]:
    data = {
        "bank_name": "HDFC Bank",
        "cardholder_name": "",
        "card_last_4": "",
        "statement_date": "",
        "payment_due_date": "",
        "total_amount_due": "",
        "minimum_amount_due": "",
        "credit_limit": "",
        "available_credit_limit": ""
    }

    # Updated name regex based on HDFC_raw.txt
    name_match = re.search(r"N\s*a\s*m\s*e\s*:?\s*([A-Z][A-Z\s]+?)\s+Statement", text, re.IGNORECASE)
    if not name_match:
         name_match = re.search(r"\brd\s+([A-Z][A-Z\s]+?)\s+Statement\b", text) # Keep old one as fallback
    data["cardholder_name"] = name_match.group(1).strip() if name_match else ""

    last4_match = re.search(r"Card\s*No[: ]*[\dXx\s]+(\d{4})", text)
    data["card_last_4"] = last4_match.group(1) if last4_match else ""

    stmt_date_match = re.search(r"Statement\s*Date[: ]*([0-9]{2}/[0-9]{2}/[0-9]{4})", text)
    data["statement_date"] = stmt_date_match.group(1) if stmt_date_match else ""

    # Combined regex for Dates and Amounts (FIXED)
    due_info_match = re.search(
        r'Payment\s*Due\s*Date\s*Total\s*Dues\s*Minimum\s*Amount\s*Due'
        r'.*?' # Match any characters, including newlines
        r'(\d{2}/\d{2}/\d{4})'  # Grp 1: Payment Due Date
        r'\s*([\d,]+\.\d{2})'   # Grp 2: Total Dues
        r'\s*([\d,]+\.\d{2})',  # Grp 3: Minimum Amount Due
        text,
        re.DOTALL | re.IGNORECASE
    )
    
    if due_info_match:
        data["payment_due_date"] = due_info_match.group(1).strip()
        data["total_amount_due"] = due_info_match.group(2).strip()
        data["minimum_amount_due"] = due_info_match.group(3).strip()
    
    # Updated Credit Limits (from HDFC_raw.txt)
    # Handles optional decimals, e.g., "30,000" and "0.00"
    credit_match = re.search(
        r'Credit\s*Limit\s*Available\s*Credit\s*Limit'
        r'.*?' # Match any characters, including newlines
        r'([\d,]+(?:\.\d{2})?)'  # Grp 1: Credit Limit (optional decimals)
        r'\s*([\d,]+(?:\.\d{2})?)', # Grp 2: Available Credit Limit (optional decimals)
        text,
        re.DOTALL | re.IGNORECASE
    )
    if credit_match:
        data["credit_limit"] = credit_match.group(1).strip()
        data["available_credit_limit"] = credit_match.group(2).strip()

    return data


def extract_data(text):
    bank = detect_bank(text)
    if bank == "Axis Bank":
        return parse_axis_bank(text)
    elif bank == "ICICI Bank":
        return parse_icici_bank(text)
    elif bank == "IDFC First Bank":
        return parse_idfc_bank(text)
    elif bank == "Syndicate Bank":
        return parse_syndicate_bank(text)
    elif bank == "HDFC Bank":
        return parse_hdfc_bank(text)
    else:
        return {"bank_name": "Unknown", "raw_text": text}


def extract_text_from_pdf(pdf_path: str) -> str:
    if pdfplumber is None:
        raise RuntimeError("pdfplumber is not installed. Please install pdfplumber to parse PDFs.")
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text += (page_text + "\n")
    return text


def parse_pdf(pdf_path: str) -> Dict[str, Any]:
    text = extract_text_from_pdf(pdf_path)
    return extract_data(text)

