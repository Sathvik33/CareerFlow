import os
import random

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
        return float(os.environ.get("CONNECTOR_TIMEOUT_SECONDS", "90"))
    except ValueError:
        return 90.0


async def fetch_with_crawlee(url: str, wait_seconds: float = 2.0) -> str:
    from crawlee import Request
    from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext

    html_holder: dict[str, str] = {"html": ""}

    crawler = PlaywrightCrawler(
        max_requests_per_crawl=1,
        max_crawl_depth=0,
        headless=True,
        browser_type="chromium",
    )

    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext) -> None:
        page = context.page
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=30_000)
        except Exception:
            pass
        if wait_seconds > 0:
            await page.wait_for_timeout(int(wait_seconds * 1000))
        html_holder["html"] = await page.content()

    try:
        await crawler.run([Request.from_url(url)])
    except Exception as e:
        print(f"Crawlee error fetching {url}: {e}")
        return ""

    return html_holder["html"]


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
