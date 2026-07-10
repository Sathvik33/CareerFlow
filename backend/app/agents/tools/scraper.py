import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool

def simulate_dummy_login(session: requests.Session, url: str):
    """Simulates a logged-in state by injecting generic authentication cookies and tokens."""
    # Add fake cookies that might trick soft login walls into thinking we are authenticated
    domain = url.split("/")[2] if "//" in url else url.split("/")[0]
    session.cookies.set("session_id", "dummy_session_12345", domain=domain)
    session.cookies.set("auth_token", "dummy_token_abcdef", domain=domain)
    session.cookies.set("logged_in", "true", domain=domain)
    session.cookies.set("user_email", "scraper_dummy@example.com", domain=domain)

@tool
def scrape_website(url: str) -> str:
    """Scrapes the text content from a given website URL using advanced headers and dummy login states to bypass anti-bot walls."""
    try:
        session = requests.Session()
        
        # Use advanced headers to mimic a real Chrome browser on Windows
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        }
        
        session.headers.update(headers)
        simulate_dummy_login(session, url)
        
        response = session.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        # Limit to 5000 chars to avoid blowing up context window
        return text[:5000]
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"
