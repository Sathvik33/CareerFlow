import httpx
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from app.models.preference import UserPreference
from app.agents.connectors import JobSource
from app.agents.connectors.utils import get_random_user_agent, role_matches


class WeWorkRemotelyConnector(JobSource):
    async def fetch_jobs(self, url: str, preferences: UserPreference) -> list[dict]:
        jobs = []
        try:
            headers = {"User-Agent": get_random_user_agent()}
            async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    text = response.text
                    # Check if RSS feed response
                    if "<rss" in text or "<channel>" in text or url.endswith(".rss"):
                        try:
                            root = ET.fromstring(text.encode("utf-8", errors="ignore"))
                            items = root.findall(".//item")
                            for item in items:
                                raw_title = item.findtext("title") or ""
                                link = item.findtext("link") or ""
                                desc = item.findtext("description") or ""
                                pub_date_str = item.findtext("pubDate") or None

                                # Title is commonly formatted as "Company: Role"
                                parts = raw_title.split(":", 1)
                                if len(parts) == 2:
                                    company, title = parts[0].strip(), parts[1].strip()
                                else:
                                    company, title = "Remote Company", raw_title.strip()

                                if not title:
                                    continue

                                roles = preferences.roles if preferences and preferences.roles else None
                                if roles and not role_matches(title, roles):
                                    continue

                                jobs.append({
                                    "source": "WeWorkRemotely",
                                    "external_id": str(uuid.uuid4()),
                                    "company": company,
                                    "title": title,
                                    "location": "Remote",
                                    "remote": True,
                                    "description": desc[:500] if desc else "",
                                    "salary": None,
                                    "apply_url": link or "https://weworkremotely.com",
                                    "company_logo": None,
                                    "posted_date": pub_date_str,
                                    "skills": [],
                                    "scraped_at": datetime.now(timezone.utc),
                                })
                        except Exception as e:
                            print(f"Error parsing WeWorkRemotely RSS: {e}")
                    else:
                        # Fallback HTML parsing
                        try:
                            from bs4 import BeautifulSoup
                            soup = BeautifulSoup(text, "html.parser")
                            items = soup.select("article ul li")
                            for item in items:
                                a_tag = item.select_one("a")
                                if not a_tag:
                                    continue
                                company_elem = item.select_one(".company")
                                title_elem = item.select_one(".title")
                                region_elem = item.select_one(".region")
                                if title_elem:
                                    company = company_elem.text.strip() if company_elem else "Unknown"
                                    title = title_elem.text.strip()
                                    location = region_elem.text.strip() if region_elem else "Remote"
                                    href = a_tag.get("href", "")
                                    if href.startswith("/"):
                                        href = f"https://weworkremotely.com{href}"
                                    jobs.append({
                                        "source": "WeWorkRemotely",
                                        "external_id": str(uuid.uuid4()),
                                        "company": company,
                                        "title": title,
                                        "location": location,
                                        "remote": True,
                                        "description": "",
                                        "salary": None,
                                        "apply_url": href,
                                        "company_logo": None,
                                        "posted_date": None,
                                        "skills": [],
                                        "scraped_at": datetime.now(timezone.utc),
                                    })
                        except ImportError:
                            pass
        except Exception as e:
            print(f"Error fetching from WeWorkRemotely: {e}")
        return jobs
