import re

# Validation Functions
def extract_name(text):
    """Extracts a name from user input if mentioned in 'My name is ...' or 'I am ...' format."""
    match = re.search(r"my name is ([A-Za-z ]{2,})", text, re.IGNORECASE)
    if not match:  
        match = re.search(r"i am ([A-Za-z ]{2,})", text, re.IGNORECASE)
    return match.group(1).strip() if match else text.strip()

def is_valid_email(email):
    """Checks if email format is valid."""
    return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email))

def extract_email(text):
    """Extracts email from user input."""
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else None

def is_valid_phone(phone):
    """Checks if phone number is valid (10 digits)."""
    return bool(re.match(r"^\d{10}$", phone))

def extract_phone(text):
    """Extracts phone number from user input."""
    match = re.search(r"\b\d{10}\b", text)
    return match.group(0) if match else None
