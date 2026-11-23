import asyncio
import json
import os
import subprocess
import sys
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
    default = int(os.environ.get("JOBSPY_RESULTS_WANTED", "5"))
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


_CHILD_SCRIPT = """
import json, sys

site = sys.argv[1]
search_term = sys.argv[2]
results_wanted = int(sys.argv[3])
location = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] else None
country = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] else None

try:
    from jobspy import scrape_jobs
    kwargs = {
        "site_name": [site],
        "search_term": search_term,
        "results_wanted": results_wanted,
        "hours_old": 72,
        "verbose": 0,
    }
    if location:
        kwargs["location"] = location
    if country and site in ("indeed", "glassdoor"):
        kwargs["country_indeed"] = country

    df = scrape_jobs(**kwargs)
    if df is not None and not df.empty:
        records = df.to_dict(orient="records")
        for r in records:
            for k, v in list(r.items()):
                if hasattr(v, "isoformat"):
                    r[k] = v.isoformat()
                elif str(v) == "nan" or v is None:
                    r[k] = None
        print(json.dumps(records))
    else:
        print("[]")
except Exception as e:
    print("[]")
"""


def _scrape_isolated_subprocess(site: str, preferences: UserPreference, results_wanted: int) -> list[dict]:
    """Runs JobSpy inside an isolated child process to protect the main Uvicorn process from tls-client-64.dll crashes."""
    queries = generate_queries(preferences)
    search_term = queries[0] if queries else "Software Engineer"
    location = preferences.locations[0] if preferences and preferences.locations else ""
    country = infer_indeed_country(location) if site in ("indeed", "glassdoor") else ""

    args = [
        sys.executable,
        "-c",
        _CHILD_SCRIPT,
        site,
        search_term,
        str(results_wanted),
        location,
        country,
    ]

    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=25.0)
        if proc.returncode != 0:
            print(f"JobSpy subprocess exited with code {proc.returncode} for {site}")
            return []

        stdout = proc.stdout.strip()
        if not stdout:
            return []

        raw_records = json.loads(stdout)
        jobs = []
        for row in raw_records:
            title = str(row.get("title") or "").strip()
            if not title:
                continue
            jobs.append(_normalize_row(row, site))
        return jobs
    except Exception as e:
        print(f"JobSpy isolated runner error for {site}: {e}")
        return []


class JobSpyConnector(JobSource):
    async def fetch_jobs(self, url: str, preferences: UserPreference) -> list[dict]:
        if os.environ.get("JOBSPY_ENABLED", "true").lower() in ("0", "false", "no"):
            return []

        site_key = _parse_site_from_url(url)
        if not site_key:
            return []

        site = SOURCE_TO_SITE.get(site_key.lower())
        if not site:
            return []

        results_wanted = _results_wanted_from_url(url)
        try:
            return await asyncio.to_thread(_scrape_isolated_subprocess, site, preferences, results_wanted)
        except Exception as e:
            print(f"Error fetching from JobSpy ({site}): {e}")
            return []
