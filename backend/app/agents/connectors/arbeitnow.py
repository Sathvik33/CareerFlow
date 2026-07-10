import httpx
import uuid
from datetime import datetime, timezone
from app.models.preference import UserPreference
from app.agents.connectors import JobSource

class ArbeitnowConnector(JobSource):
    async def fetch_jobs(self, url: str, preferences: UserPreference) -> list[dict]:
        jobs = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json().get("data", [])
                    
                    # Convert preferences to search terms
                    roles = preferences.roles or ["Software Engineer"]
                    skills = preferences.preferred_skills or []
                    locations = preferences.locations or []
                    
                    for item in data:
                        title = item.get("title", "")
                        description = item.get("description", "")
                        location = item.get("location", "")
                        is_remote = item.get("remote", False)
                        
                        text_to_search = f"{title} {description}".lower()
                        loc_to_search = location.lower()
                        
                        # Check role match
                        role_match = any(r.lower() in text_to_search for r in roles)
                        
                        # Check location match if locations specified
                        loc_match = True
                        if locations:
                            loc_match = False
                            for loc in locations:
                                if loc.lower() == "remote" and is_remote:
                                    loc_match = True
                                elif loc.lower() in loc_to_search:
                                    loc_match = True
                                    
                        if role_match and loc_match:
                            posted_at_raw = item.get("created_at")
                            posted_at = None
                            if posted_at_raw:
                                try:
                                    posted_at = datetime.fromtimestamp(posted_at_raw, tz=timezone.utc)
                                except Exception:
                                    pass

                            jobs.append({
                                "source": "Arbeitnow",
                                "external_id": item.get("slug") or str(uuid.uuid4()),
                                "company": item.get("company_name", "Unknown"),
                                "title": title,
                                "location": location,
                                "remote": is_remote,
                                "description": description,
                                "salary": None,
                                "apply_url": item.get("url", ""),
                                "company_logo": None,
                                "posted_date": posted_at,
                                "skills": item.get("tags", []),
                                "scraped_at": datetime.now(timezone.utc)
                            })
        except Exception as e:
            print(f"Error fetching from Arbeitnow: {e}")
        return jobs
