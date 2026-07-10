import re

INJECTION_PATTERNS = [
    r"(?i)\bignore\s+(all\s+)?(previous\s+)?instructions\b",
    r"(?i)\bsystem\s+prompt\b",
    r"(?i)\bbypass\s+(the\s+)?rules\b",
    r"(?i)\byou\s+are\s+now\b",
    r"(?i)\bdisregard\b.*\binstructions\b",
    r"(?i)\bprint\s+(all\s+)?(previous\s+)?instructions\b"
]

def scan_for_prompt_injection(text: str) -> bool:
    """Returns True if a prompt injection is detected."""
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text):
            return True
    return False
