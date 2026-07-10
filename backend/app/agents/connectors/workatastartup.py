import asyncio
import uuid
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from app.models.preference import UserPreference
from app.agents.connectors import JobSource
from app.agents.connectors.utils import fetch_with_selenium, role_matches

class WorkAtAStartupConnector(JobSource):
    async def fetch_jobs(self, url: str, preferences: UserPreference) -> list[dict]:
        jobs = []
        try:
            # Execute Selenium synchronously in a separate thread so it runs parallelly
            html = await asyncio.to_thread(fetch_with_selenium, url)
            if not html:
                return []
                
            soup = BeautifulSoup(html, "html.parser")
            
            # Very basic best-effort parsing for YC WaaS job listings
            job_elements = soup.find_all("div", class_=lambda c: c and ("job" in c.lower() or "role" in c.lower()))
            
            for el in job_elements[:10]: # Process top 10 matches
                title_el = el.find(["h2", "h3", "h4", "a", "span", "div"], class_=lambda c: c and ("title" in c.lower() or "name" in c.lower()))
                
                # Fallback to any strong/b or link if title specific class not found
                if not title_el:
                    title_el = el.find(["a"])
                    
                if not title_el:
                    continue
                    
                title = title_el.get_text(strip=True)
                if not title or len(title) < 4:
                    continue
                    
                link_el = el.find("a", href=True)
                apply_url = ("https://www.workatastartup.com" + link_el["href"]) if link_el and link_el["href"].startswith("/") else (link_el["href"] if link_el else url)
                
                # Check if role matches preferences
                roles = preferences.roles or ["engineer"]
                if not role_matches(title, roles):
                    continue
                    
                jobs.append({
                    "source": "WorkAtAStartup",
                    "external_id": str(uuid.uuid4()),
                    "company": "YC Startup",
                    "title": title,
                    "location": "Remote",
                    "remote": True,
                    "description": "",
                    "salary": None,
                    "apply_url": apply_url,
                    "company_logo": "",
                    "posted_date": None,
                    "skills": [],
                    "scraped_at": datetime.now(timezone.utc)
                })
        except Exception as e:
            print(f"Error fetching from WorkAtAStartup: {e}")
            
        return jobs
