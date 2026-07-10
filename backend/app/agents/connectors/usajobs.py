import os
import httpx
import uuid
from datetime import datetime, timezone
from app.models.preference import UserPreference
from app.agents.connectors import JobSource

class USAJobsConnector(JobSource):
    async def fetch_jobs(self, url: str, preferences: UserPreference) -> list[dict]:
        jobs = []
        try:
            auth_key = os.environ.get("USAJOBS_AUTH_KEY", "")
            headers = {
                "User-Agent": "careerflow@example.com",
                "Authorization-Key": auth_key
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    search_result = data.get("SearchResult", {})
                    items = search_result.get("SearchResultItems", [])
                    
                    for item in items:
                        job_data = item.get("MatchedObjectDescriptor", {})
                        title = job_data.get("PositionTitle", "")
                        company = job_data.get("OrganizationName", "USAJobs")
                        apply_url = job_data.get("PositionURI", "")
                        
                        locations = job_data.get("PositionLocation", [])
                        loc_name = locations[0].get("LocationName", "USA") if locations else "USA"
                        
                        salary_min = job_data.get("PositionRemuneration", [{}])[0].get("MinimumRange")
                        salary_max = job_data.get("PositionRemuneration", [{}])[0].get("MaximumRange")
                        salary = None
                        if salary_min and salary_max:
                            salary = f"${salary_min} - ${salary_max}"
                            
                        jobs.append({
                            "source": "USAJobs",
                            "external_id": str(job_data.get("PositionID", uuid.uuid4())),
                            "company": company,
                            "title": title,
                            "location": loc_name,
                            "remote": "Remote" in loc_name or "Anywhere" in loc_name,
                            "description": job_data.get("UserArea", {}).get("Details", {}).get("JobSummary", ""),
                            "salary": salary,
                            "apply_url": apply_url,
                            "company_logo": "",
                            "posted_date": None,
                            "skills": [],
                            "scraped_at": datetime.now(timezone.utc)
                        })
        except Exception as e:
            print(f"Error fetching from USAJobs: {e}")
            
        return jobs
