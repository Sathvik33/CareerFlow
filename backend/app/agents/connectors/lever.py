import httpx
import uuid
from datetime import datetime, timezone
from app.models.preference import UserPreference
from app.agents.connectors import JobSource

class LeverConnector(JobSource):
    async def fetch_jobs(self, url: str, preferences: UserPreference) -> list[dict]:
        jobs = []
        roles = [r.lower() for r in (preferences.roles or ["engineer"])]
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    company = url.split("/postings/")[1].split("?")[0].capitalize() if "/postings/" in url else "Unknown"
                    for item in data:
                        title = item.get("text", "")
                        location = item.get("categories", {}).get("location", "")
                        description = item.get("descriptionPlain", "")
                        
                        text_to_search = f"{title} {location}".lower()
                        
                        if any(r in text_to_search for r in roles):
                            posted_at_raw = item.get("createdAt")
                            posted_at = None
                            if posted_at_raw:
                                try:
                                    posted_at = datetime.fromtimestamp(posted_at_raw / 1000.0, tz=timezone.utc)
                                except Exception:
                                    pass
                                    
                            jobs.append({
                                "source": "Lever",
                                "external_id": item.get("id", str(uuid.uuid4())),
                                "company": company.capitalize(),
                                "title": title,
                                "location": location,
                                "remote": "remote" in location.lower() or "remote" in title.lower(),
                                "description": description,
                                "salary": None,
                                "apply_url": item.get("applyUrl") or item.get("hostedUrl", ""),
                                "company_logo": None,
                                "posted_date": posted_at,
                                "skills": [],
                                "scraped_at": datetime.now(timezone.utc)
                            })
            except Exception as e:
                print(f"Error fetching from Lever ({url}): {e}")
        return jobs
