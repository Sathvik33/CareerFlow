import uuid
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from app.models.preference import UserPreference
from app.agents.connectors import JobSource
from app.agents.connectors.utils import fetch_with_crawlee, role_matches


class WorkAtAStartupConnector(JobSource):
    async def fetch_jobs(self, url: str, preferences: UserPreference) -> list[dict]:
        jobs = []
        try:
            html = await fetch_with_crawlee(url)
            if not html:
                print(f"WorkAtAStartup: empty HTML for {url}")
                return []

            soup = BeautifulSoup(html, "html.parser")
            seen = set()

            # YC Work at a Startup job cards are linked with /jobs/<id>
            job_links = soup.find_all(
                "a",
                href=lambda h: h and h.startswith("/jobs/") and h.split("/jobs/")[1].isdigit()
            )

            roles = preferences.roles or ["engineer"]

            for a in job_links:
                href = a["href"]
                if href in seen:
                    continue
                seen.add(href)

                text_parts = [p.strip() for p in a.get_text("\n").split("\n") if p.strip()]
                if not text_parts:
                    continue

                company = text_parts[0] if len(text_parts) >= 1 else "YC Startup"
                title = text_parts[2] if len(text_parts) >= 3 else text_parts[-1]
                loc_salary = text_parts[3] if len(text_parts) >= 4 else ""

                if not title or len(title) < 3:
                    continue

                if not role_matches(title, roles):
                    continue

                apply_url = f"https://www.workatastartup.com{href}"

                jobs.append({
                    "source": "WorkAtAStartup",
                    "external_id": str(uuid.uuid4()),
                    "company": company,
                    "title": title,
                    "location": loc_salary or "Remote / Hybrid",
                    "remote": "remote" in loc_salary.lower() if loc_salary else True,
                    "description": text_parts[1] if len(text_parts) >= 2 else "",
                    "salary": loc_salary if "$" in loc_salary else None,
                    "apply_url": apply_url,
                    "company_logo": "",
                    "posted_date": None,
                    "skills": [],
                    "scraped_at": datetime.now(timezone.utc),
                })
        except Exception as e:
            print(f"Error fetching from WorkAtAStartup: {e}")

        return jobs
