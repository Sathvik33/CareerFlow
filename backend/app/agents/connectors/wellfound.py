import uuid
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from app.models.preference import UserPreference
from app.agents.connectors import JobSource
from app.agents.connectors.utils import fetch_with_crawlee, role_matches


class WellfoundConnector(JobSource):
    async def fetch_jobs(self, url: str, preferences: UserPreference) -> list[dict]:
        jobs = []
        try:
            html = await fetch_with_crawlee(url)
            if not html:
                print(f"Wellfound: empty HTML for {url}")
                return []

            soup = BeautifulSoup(html, "html.parser")
            seen = set()

            # Target Wellfound job links: /jobs/<id>-<slug>
            job_links = soup.find_all(
                "a",
                href=lambda h: h and h.startswith("/jobs/")
                and not h.startswith("/jobs/signup")
                and not h.startswith("/jobs/l/")
                and not h.startswith("/jobs/r/")
            )

            roles = preferences.roles or ["engineer"]

            for a in job_links:
                href = a["href"]
                title = a.get_text(strip=True)
                if not title or len(title) < 4 or href in seen:
                    continue
                seen.add(href)

                if not role_matches(title, roles):
                    continue

                apply_url = f"https://wellfound.com{href}" if href.startswith("/") else href

                # Check if parent card has company or location text
                parent = a.find_parent("div")
                company = "Wellfound Startup"
                location = "Remote / Hybrid"
                if parent:
                    comp_link = parent.find("a", href=lambda h: h and "/company/" in h)
                    if comp_link and comp_link.get_text(strip=True):
                        company = comp_link.get_text(strip=True)

                jobs.append({
                    "source": "Wellfound",
                    "external_id": str(uuid.uuid4()),
                    "company": company,
                    "title": title,
                    "location": location,
                    "remote": True,
                    "description": "",
                    "salary": None,
                    "apply_url": apply_url,
                    "company_logo": "",
                    "posted_date": None,
                    "skills": [],
                    "scraped_at": datetime.now(timezone.utc),
                })
        except Exception as e:
            print(f"Error fetching from Wellfound: {e}")

        return jobs
