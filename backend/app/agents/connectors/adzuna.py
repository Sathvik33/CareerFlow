import httpx
import uuid
from datetime import datetime, timezone
from dateutil import parser as date_parser
from app.models.preference import UserPreference
from app.agents.connectors import JobSource

class AdzunaConnector(JobSource):
    async def fetch_jobs(self, url: str, preferences: UserPreference) -> list[dict]:
        jobs = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    for item in results:
                        posted_at_raw = item.get("created")
                        posted_at = None
                        if posted_at_raw:
                            try:
                                posted_at = date_parser.parse(posted_at_raw)
                            except Exception:
                                pass
                                
                        loc_obj = item.get("location", {})
                        location = ", ".join(loc_obj.get("area", []))
                        
                        salary_min = item.get("salary_min")
                        salary_max = item.get("salary_max")
                        salary = None
                        if salary_min and salary_max:
                            salary = f"${salary_min} - ${salary_max}"
                            
                        company_obj = item.get("company", {})
                        company = company_obj.get("display_name", "Unknown")

                        jobs.append({
                            "source": "Adzuna",
                            "external_id": str(item.get("id", uuid.uuid4())),
                            "company": company,
                            "title": item.get("title", ""),
                            "location": location,
                            "remote": "remote" in location.lower(),
                            "description": item.get("description", ""),
                            "salary": salary,
                            "apply_url": item.get("redirect_url", ""),
                            "company_logo": None,
                            "posted_date": posted_at,
                            "skills": [],
                            "scraped_at": datetime.now(timezone.utc)
                        })
        except Exception as e:
            print(f"Error fetching from Adzuna: {e}")
        return jobs
