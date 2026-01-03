import re
from typing import Optional

# Regex patterns
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
ROLE_KEYWORDS = ["Software Engineer", "Developer", "Manager", "Analyst", "Lead", "Architect", "Designer", "Consultant"]
ADDRESS_KEYWORDS = ["Street", "Avenue", "Road", "Rd", "St", "Ave", "Drive", "Dr", "Lane", "Ln", "City", "State", "Zip", "Country"]

def extract_email(text: str) -> Optional[str]:
    match = re.search(EMAIL_REGEX, text)
    return match.group(0).lower() if match else None

def extract_name(text: str) -> str:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if lines:
        first_line = lines[0]
        if len(first_line) < 50 and "@" not in first_line:
            return first_line
    return "Not Found"

def extract_address(text: str) -> str:
    lines = [l.strip() for l in text.split("\n")]
    for line in lines:
        if any(kw in line for kw in ADDRESS_KEYWORDS) and len(line) < 100:
            return line
    return "Not Found"

def extract_job_role(text: str) -> str:
    lines = [l.strip() for l in text.split("\n")]
    for line in lines:
        if any(kw.lower() in line.lower() for kw in ROLE_KEYWORDS) and len(line) < 60:
            return line
    return "Not Found"
