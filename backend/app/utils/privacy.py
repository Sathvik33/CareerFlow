import logging
import re
import spacy

logger = logging.getLogger(__name__)

_nlp = None
_nlp_load_attempted = False


def _get_nlp():
    """Lazy-load SpaCy NER model so startup never blocks or crashes if unavailable."""
    global _nlp, _nlp_load_attempted
    if _nlp_load_attempted:
        return _nlp

    _nlp_load_attempted = True
    try:
        _nlp = spacy.load("en_core_web_sm")
    except OSError:
        try:
            from spacy.cli import download
            download("en_core_web_sm")
            _nlp = spacy.load("en_core_web_sm")
        except Exception as exc:
            logger.warning(
                "Could not load or download SpaCy 'en_core_web_sm'; "
                "falling back to regex-only PII masking: %s",
                exc,
            )
            _nlp = None
    return _nlp


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

    # 4. Mask Names using SpaCy (if model is available)
    nlp = _get_nlp()
    if nlp is not None:
        doc = nlp(text)
        people = {ent.text for ent in doc.ents if ent.label_ == "PERSON"}
        for person in sorted(people, key=len, reverse=True):
            pattern = r'\b' + re.escape(person) + r'\b'
            text = re.sub(pattern, '[NAME]', text)

    return text
