import asyncio
import os
import random
import httpx

from dotenv import load_dotenv

load_dotenv()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


def get_random_user_agent() -> str:
    return random.choice(USER_AGENTS)


def connector_timeout_seconds() -> float:
    try:
        return float(os.environ.get("CONNECTOR_TIMEOUT_SECONDS", "15"))
    except ValueError:
        return 15.0


async def fetch_with_crawlee(url: str, wait_seconds: float = 1.5) -> str:
    """Fetches page content asynchronously using httpx with browser headers and SSL verification bypassed."""
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Ch-Ua": '"Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
    }
    try:
        async with httpx.AsyncClient(headers=headers, timeout=12.0, verify=False, follow_redirects=True) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                return resp.text
            print(f"fetch_with_crawlee: status {resp.status_code} for {url}")
            return ""
    except Exception as e:
        print(f"fetch_with_crawlee error for {url}: {e}")
        return ""


def role_matches(text_to_search: str, roles: list[str]) -> bool:
    text = text_to_search.lower()
    for role in roles:
        role = role.lower()
        if role in text:
            return True

        safe_role = role.replace("/", " ").replace("-", " ")
        generic_words = {"and", "for", "the", "with", "developer", "engineer", "manager", "specialist", "expert"}
        keywords = [w for w in safe_role.split() if len(w) > 2 and w not in generic_words]

        if keywords and any(k in text for k in keywords):
            return True

        if not keywords and safe_role in text:
            return True

    return False
