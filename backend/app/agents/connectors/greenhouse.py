import httpx
import uuid
from datetime import datetime, timezone
from app.models.preference import UserPreference
from app.agents.connectors import JobSource
from app.agents.connectors.utils import get_random_user_agent, role_matches

class GreenhouseConnector(JobSource):
    async def fetch_jobs(self, url: str, preferences: UserPreference) -> list[dict]:
        jobs = []
        roles = preferences.roles or ["engineer"]
        
        headers = {"User-Agent": get_random_user_agent()}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json().get("jobs", [])
                    company = url.split("/boards/")[1].split("/jobs")[0].capitalize() if "/boards/" in url else "Unknown"
                    for item in data:
                        title = item.get("title", "")
                        location = item.get("location", {}).get("name", "")
                        
                        text_to_search = f"{title} {location}"
                        
                        if role_matches(text_to_search, roles):
                            jobs.append({
                                "source": "Greenhouse",
                                "external_id": str(item.get("id", uuid.uuid4())),
                                "company": company,
                                "title": title,
                                "location": location,
                                "remote": "remote" in location.lower(),
                                "description": "",
                                "salary": None,
                                "apply_url": item.get("absolute_url", ""),
                                "company_logo": None,
                                "posted_date": None,
                                "skills": [],
                                "scraped_at": datetime.now(timezone.utc)
                            })
            except Exception as e:
                print(f"Error fetching from Greenhouse ({url}): {e}")
        return jobs
