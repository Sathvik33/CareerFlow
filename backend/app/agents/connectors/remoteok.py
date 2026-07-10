import httpx
import uuid
from datetime import datetime, timezone
from dateutil import parser as date_parser
from app.models.preference import UserPreference
from app.agents.connectors import JobSource

class RemoteOKConnector(JobSource):
    async def fetch_jobs(self, url: str, preferences: UserPreference) -> list[dict]:
        jobs = []
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    for item in data[1:]: # index 0 is legal notice
                        
                        # Apply experience filter locally if available
                        desc = item.get("description", "").lower()
                        exp = (preferences.experience_level or "").lower()
                        if exp and exp not in desc and f"{exp} level" not in desc:
                            # It's a weak filter but we can skip if experience strongly mis-matches
                            pass # We won't strictly filter to get more results
                        
                        posted_at_raw = item.get("date")
                        posted_at = None
                        if posted_at_raw:
                            try:
                                posted_at = date_parser.parse(posted_at_raw)
                            except Exception:
                                pass
                                
                        salary_min = item.get("salary_min")
                        salary_max = item.get("salary_max")
                        salary = None
                        if salary_min and salary_max:
                            salary = f"${salary_min} - ${salary_max}"

                        jobs.append({
                            "source": "RemoteOK",
                            "external_id": item.get("id", str(uuid.uuid4())),
                            "company": item.get("company", "Unknown"),
                            "title": item.get("position", ""),
                            "location": item.get("location", "Remote"),
                            "remote": True,
                            "description": item.get("description", ""),
                            "salary": salary,
                            "apply_url": item.get("apply_url") or item.get("url", ""),
                            "company_logo": item.get("company_logo", ""),
                            "posted_date": posted_at,
                            "skills": item.get("tags", []),
                            "scraped_at": datetime.now(timezone.utc)
                        })
        except Exception as e:
            print(f"Error fetching from RemoteOK: {e}")
        return jobs
