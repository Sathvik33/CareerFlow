import random
import time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

def get_random_user_agent() -> str:
    """Returns a random strong User-Agent string."""
    return random.choice(USER_AGENTS)

def fetch_with_selenium(url: str) -> str:
    """
    Synchronous helper to fetch fully rendered HTML using Headless Chrome.
    Must be called via asyncio.to_thread() to avoid blocking the event loop.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={get_random_user_agent()}")
    options.add_argument("--window-size=1920,1080")
    
    # Initialize driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.set_page_load_timeout(30)
        driver.get(url)
        # Give JS heavy sites a little time to render
        time.sleep(3.0)
        html = driver.page_source
        return html
    except Exception as e:
        print(f"Selenium error fetching {url}: {e}")
        return ""
    finally:
        driver.quit()

def role_matches(text_to_search: str, roles: list[str]) -> bool:
    """
    Robust role matching to handle complex user preferences like 'AI/ML Engineer'.
    Instead of failing when the exact string isn't found, it checks if the core keywords are present.
    """
    text = text_to_search.lower()
    for role in roles:
        role = role.lower()
        if role in text:
            return True
            
        # Handle cases like "AI/ML Engineer" by splitting and checking meaningful keywords
        safe_role = role.replace("/", " ").replace("-", " ")
        # Filter out generic words to avoid false positives
        generic_words = {"and", "for", "the", "with", "developer", "engineer", "manager", "specialist", "expert"}
        keywords = [w for w in safe_role.split() if len(w) > 2 and w not in generic_words]
        
        # If any specific keyword (like "ai", "ml", "react") matches, we consider it a hit
        if keywords and any(k in text for k in keywords):
            return True
            
        # If no specific keywords (e.g. they literally only typed "Engineer"), just check the original
        if not keywords and safe_role in text:
            return True
            
    return False
