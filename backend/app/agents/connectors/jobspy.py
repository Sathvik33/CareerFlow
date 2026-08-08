import asyncio
import os
import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv

load_dotenv()

from app.agents.connectors import JobSource
from app.agents.url_generator import generate_queries, infer_indeed_country, is_remote_preference
from app.models.preference import UserPreference

SOURCE_TO_SITE = {
    "indeed": "indeed",
    "linkedin": "linkedin",
    "glassdoor": "glassdoor",
    "google": "google",
    "ziprecruiter": "zip_recruiter",
    "zip_recruiter": "zip_recruiter",
    "naukri": "naukri",
}


def _parse_site_from_url(url: str) -> str | None:
    if not url:
        return None
    raw = url.strip()
    if raw.startswith("jobspy://"):
        parsed = urlparse(raw)
        return parsed.netloc or parsed.path.lstrip("/")
    if raw.startswith("jobspy:"):
        return raw.split(":", 1)[1].split("?")[0]
    return raw.lower()


def _results_wanted_from_url(url: str) -> int:
    default = int(os.environ.get("JOBSPY_RESULTS_WANTED", "20"))
    default = max(1, min(default, 50))
    if not url or "://" not in url:
        return default
    qs = parse_qs(urlparse(url).query)
    if "results_wanted" in qs:
        try:
            return max(1, min(int(qs["results_wanted"][0]), 50))
        except ValueError:
            pass
    return default


def _proxy_list() -> list[str] | None:
    raw = os.environ.get("JOBSPY_PROXIES", "").strip()
    if not raw:
        return None
    proxies = [p.strip() for p in raw.split(",") if p.strip()]
    return proxies or None


def _normalize_row(row: dict, site: str) -> dict:
    title = str(row.get("title") or "").strip()
    company = str(row.get("company") or "").strip() or "Unknown Company"
    location = str(row.get("location") or "").strip()
    description = str(row.get("description") or row.get("description_text") or "").strip()
    apply_url = str(row.get("job_url") or row.get("job_url_direct") or "").strip()
    external = str(row.get("id") or apply_url or uuid.uuid4())
    is_remote = bool(row.get("is_remote")) or ("remote" in location.lower() if location else False)

    salary = None
    min_amt = row.get("min_amount")
    max_amt = row.get("max_amount")
    currency = row.get("currency") or ""
    if min_amt or max_amt:
        salary = f"{min_amt or ''}–{max_amt or ''} {currency}".strip()

    source_label = {
        "indeed": "Indeed",
        "linkedin": "LinkedIn",
        "glassdoor": "Glassdoor",
        "google": "Google",
        "zip_recruiter": "ZipRecruiter",
        "naukri": "Naukri",
    }.get(site, site.title())

    return {
        "source": source_label,
        "external_id": external,
        "company": company,
        "title": title,
        "location": location or ("Remote" if is_remote else ""),
        "remote": is_remote,
        "description": description,
        "salary": salary,
        "apply_url": apply_url,
        "company_logo": None,
        "posted_date": row.get("date_posted"),
        "skills": [],
        "scraped_at": datetime.now(timezone.utc),
    }


def _scrape_sync(site: str, preferences: UserPreference, results_wanted: int) -> list[dict]:
    from jobspy import scrape_jobs

    queries = generate_queries(preferences)
    search_term = queries[0] if queries else "Software Engineer"
    location = ""
    if preferences and preferences.locations:
        location = preferences.locations[0]

    kwargs = {
        "site_name": [site],
        "search_term": search_term,
        "location": location or None,
        "results_wanted": results_wanted,
        "hours_old": 72,
        "verbose": 0,
    }

    if site in ("indeed", "glassdoor"):
        kwargs["country_indeed"] = infer_indeed_country(location)

    if is_remote_preference(preferences):
        kwargs["is_remote"] = True

    proxies = _proxy_list()
    if proxies:
        kwargs["proxies"] = proxies

    if site == "linkedin":
        kwargs["linkedin_fetch_description"] = os.environ.get(
            "JOBSPY_LINKEDIN_FETCH_DESCRIPTION", "false"
        ).lower() in ("1", "true", "yes")

    df = scrape_jobs(**kwargs)
    if df is None or getattr(df, "empty", True):
        return []

    jobs = []
    for row in df.to_dict(orient="records"):
        title = str(row.get("title") or "").strip()
        if not title:
            continue
        jobs.append(_normalize_row(row, site))
    return jobs


class JobSpyConnector(JobSource):
    async def fetch_jobs(self, url: str, preferences: UserPreference) -> list[dict]:
        if os.environ.get("JOBSPY_ENABLED", "true").lower() in ("0", "false", "no"):
            return []

        site_key = _parse_site_from_url(url)
        if not site_key:
            print("JobSpyConnector: missing site in url")
            return []

        site = SOURCE_TO_SITE.get(site_key.lower())
        if not site:
            print(f"JobSpyConnector: unsupported site '{site_key}'")
            return []

        results_wanted = _results_wanted_from_url(url)
        try:
            return await asyncio.to_thread(_scrape_sync, site, preferences, results_wanted)
        except Exception as e:
            print(f"Error fetching from JobSpy ({site}): {e}")
            return []
