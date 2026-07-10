import httpx
import uuid
import urllib.parse
from datetime import datetime, timezone
from app.models.preference import UserPreference
from app.agents.connectors import JobSource
from app.agents.connectors.utils import get_random_user_agent

class WeWorkRemotelyConnector(JobSource):
    async def fetch_jobs(self, url: str, preferences: UserPreference) -> list[dict]:
        jobs = []
        try:
            headers = {"User-Agent": get_random_user_agent()}
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    html = response.text
                    try:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(html, "html.parser")
                        items = soup.select("article ul li")
                        for item in items:
                            a_tag = item.select_one("a")
                            if not a_tag:
                                continue
                            
                            company_elem = item.select_one(".company")
                            title_elem = item.select_one(".title")
                            region_elem = item.select_one(".region")
                            
                            if title_elem:
                                company = company_elem.text.strip() if company_elem else "Unknown"
                                title = title_elem.text.strip()
                                location = region_elem.text.strip() if region_elem else "Remote"
                                href = a_tag.get("href", "")
                                if href.startswith("/"):
                                    href = f"https://weworkremotely.com{href}"
                                    
                                jobs.append({
                                    "source": "WeWorkRemotely",
                                    "external_id": str(uuid.uuid4()),
                                    "company": company,
                                    "title": title,
                                    "location": location,
                                    "remote": True,
                                    "description": "",
                                    "salary": None,
                                    "apply_url": href,
                                    "company_logo": None,
                                    "posted_date": None,
                                    "skills": [],
                                    "scraped_at": datetime.now(timezone.utc)
                                })
                    except ImportError:
                        print("BeautifulSoup not installed. Skipping HTML parsing.")
        except Exception as e:
            print(f"Error fetching from WeWorkRemotely: {e}")
        return jobs
