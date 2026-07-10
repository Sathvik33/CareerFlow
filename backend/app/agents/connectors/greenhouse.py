import httpx
import uuid
from datetime import datetime, timezone
from app.models.preference import UserPreference
from app.agents.connectors import JobSource

class GreenhouseConnector(JobSource):
    async def fetch_jobs(self, url: str, preferences: UserPreference) -> list[dict]:
        jobs = []
        roles = [r.lower() for r in (preferences.roles or ["engineer"])]
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json().get("jobs", [])
                    company = url.split("/boards/")[1].split("/jobs")[0].capitalize() if "/boards/" in url else "Unknown"
                    for item in data:
                        title = item.get("title", "")
                        location = item.get("location", {}).get("name", "")
                        
                        text_to_search = f"{title} {location}".lower()
                        
                        if any(r in text_to_search for r in roles):
                            jobs.append({
                                "source": "Greenhouse",
                                "external_id": str(item.get("id", uuid.uuid4())),
                                "company": company.capitalize(),
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
