import re
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback if not downloaded during setup
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def mask_pii(text: str) -> str:
    """Masks Emails, Phones, URLs, and Names from raw text."""
    # 1. Mask Emails
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    text = re.sub(email_pattern, '[EMAIL]', text)

    # 2. Mask Phone Numbers (basic international and local formats)
    phone_pattern = r'\+?\d[\d -]{8,12}\d'
    text = re.sub(phone_pattern, '[PHONE]', text)

    # 3. Mask URLs (LinkedIn, Github, Leetcode, personal sites)
    url_pattern = r'(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})'
    text = re.sub(url_pattern, '[URL]', text)

    # 4. Mask Names using SpaCy
    doc = nlp(text)
    # Reconstruct text so we don't mess up offsets
    # However, replacing strings directly is easier for a simple PII stripper
    # We sort entities by length descending to avoid replacing partial strings
    people = set([ent.text for ent in doc.ents if ent.label_ == "PERSON"])
    
    # Sort by length descending to replace longest first (e.g., "John Doe" before "John")
    for person in sorted(people, key=len, reverse=True):
        # Only replace word boundaries to avoid replacing "mark" in "marketing" if SpaCy mistakenly tagged "mark" as a person.
        # It's a simplistic approach but functional.
        pattern = r'\b' + re.escape(person) + r'\b'
        text = re.sub(pattern, '[NAME]', text)
            
    return text
