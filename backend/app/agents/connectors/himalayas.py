import httpx
import uuid
from datetime import datetime, timezone
from app.models.preference import UserPreference
from app.agents.connectors import JobSource
from app.agents.connectors.utils import get_random_user_agent

class HimalayasConnector(JobSource):
    async def fetch_jobs(self, url: str, preferences: UserPreference) -> list[dict]:
        jobs = []
        headers = {"User-Agent": get_random_user_agent()}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    # Himalayas returns jobs in data["jobs"]
                    results = data.get("jobs", [])
                    for item in results:
                        title = item.get("title", "")
                        company = item.get("companyName", "Unknown")
                        apply_url = item.get("applicationLink", item.get("jobLink", ""))
                        
                        jobs.append({
                            "source": "Himalayas",
                            "external_id": str(item.get("id", uuid.uuid4())),
                            "company": company,
                            "title": title,
                            "location": item.get("location", "Remote"),
                            "remote": True,
                            "description": item.get("description", ""),
                            "salary": None,  # Often hidden or needs separate parsing
                            "apply_url": apply_url,
                            "company_logo": item.get("companyLogo", ""),
                            "posted_date": None,
                            "skills": [],
                            "scraped_at": datetime.now(timezone.utc)
                        })
        except Exception as e:
            print(f"Error fetching from Himalayas: {e}")
            
        return jobs
