import os
import urllib.parse
from app.models.preference import UserPreference

JOBSPY_SOURCES = (
    "Indeed",
    "LinkedIn",
    "Glassdoor",
    "Google",
    "ZipRecruiter",
    "Naukri",
)

JOBSPY_SITE_KEYS = {
    "Indeed": "indeed",
    "LinkedIn": "linkedin",
    "Glassdoor": "glassdoor",
    "Google": "google",
    "ZipRecruiter": "zip_recruiter",
    "Naukri": "naukri",
}


def is_india_location(location: str) -> bool:
    if not location:
        return False
    loc = location.lower()
    india_tokens = (
        "india", "hyderabad", "bengaluru", "bangalore", "mumbai", "delhi",
        "chennai", "pune", "kolkata", "noida", "gurgaon", "gurugram", "ahmedabad",
    )
    return any(t in loc for t in india_tokens)


def infer_indeed_country(location: str) -> str:
    if is_india_location(location):
        return "India"
    return "USA"


def is_remote_preference(preferences: UserPreference | None) -> bool:
    if not preferences or not preferences.locations:
        return False
    return any("remote" in (l or "").lower() for l in preferences.locations)


def generate_queries(preferences: UserPreference) -> list[str]:
    queries = []

    roles = preferences.roles if preferences and preferences.roles else ["Software Engineer"]
    skills = preferences.preferred_skills if preferences and preferences.preferred_skills else []

    for role in roles[:3]:
        safe_role = role.replace("/", " ")
        queries.append(safe_role)
        if skills:
            for skill in skills[:2]:
                queries.append(f"{safe_role} {skill}")

    if preferences and preferences.locations and "remote" in [l.lower() for l in preferences.locations]:
        queries.append(f"Remote {roles[0]}")

    unique_queries = list(dict.fromkeys(queries))
    return unique_queries[:5]


def _jobspy_enabled() -> bool:
    return os.environ.get("JOBSPY_ENABLED", "true").lower() not in ("0", "false", "no")


def _jobspy_results_wanted() -> int:
    try:
        return max(1, min(int(os.environ.get("JOBSPY_RESULTS_WANTED", "20")), 50))
    except ValueError:
        return 20


def generate_dynamic_urls(preferences: UserPreference, target_websites: list[str] = None) -> list[dict]:
    queries = generate_queries(preferences)
    urls = []

    allowed_sources = [w.lower() for w in target_websites] if target_websites else None

    primary_location = ""
    if preferences and preferences.locations:
        primary_location = preferences.locations[0]

    exp_level = preferences.experience_level or ""
    job_type = preferences.job_types[0] if preferences and preferences.job_types else ""
    salary_min = preferences.salary_min or ""
    salary_max = preferences.salary_max or ""

    urls.append({
        "source": "Arbeitnow",
        "url": "https://www.arbeitnow.com/api/job-board-api"
    })

    urls.append({
        "source": "RemoteOK",
        "url": "https://remoteok.com/api"
    })

    app_id = os.environ.get("ADZUNA_APP_ID", "")
    app_key = os.environ.get("ADZUNA_APP_KEY", "")
    if app_id and app_key:
        for query in queries:
            params = {
                "app_id": app_id,
                "app_key": app_key,
                "what": query,
                "results_per_page": 50,
                "sort_by": "date"
            }
            if primary_location:
                params["where"] = primary_location
            if salary_min:
                params["salary_min"] = salary_min
            if salary_max:
                params["salary_max"] = salary_max

            query_string = urllib.parse.urlencode(params)
            country = "in" if is_india_location(primary_location) else "us"

            urls.append({
                "source": "Adzuna",
                "url": f"https://api.adzuna.com/v1/api/jobs/{country}/search/1?{query_string}"
            })

    for query in queries:
        params = {
            "Keyword": query,
            "ResultsPerPage": 100
        }
        if primary_location:
            params["LocationName"] = primary_location
        query_string = urllib.parse.urlencode(params)
        urls.append({
            "source": "USAJobs",
            "url": f"https://data.usajobs.gov/api/search?{query_string}"
        })

    greenhouse_companies = [
        "openai", "stripe", "notion", "figma", "discord",
        "twitch", "reddit", "pinterest", "asana", "datadog",
        "snowflake", "hashicorp", "doordash", "instacart", "okta",
        "gitlab", "coursera", "duolingo", "plaid", "roblox"
    ]
    for company in greenhouse_companies:
        urls.append({
            "source": "Greenhouse",
            "url": f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
        })

    lever_companies = [
        "netflix", "canva", "anthropic", "yelp", "quora",
        "atlassian", "palantir", "peloton", "robinhood", "shopify",
        "kiva", "eventbrite", "lyft", "github", "hootsuite"
    ]
    for company in lever_companies:
        urls.append({
            "source": "Lever",
            "url": f"https://api.lever.co/v0/postings/{company}?mode=json"
        })

    for query in queries:
        encoded_query = urllib.parse.quote(query)
        urls.append({
            "source": "WeWorkRemotely",
            "url": f"https://weworkremotely.com/remote-jobs/search?term={encoded_query}"
        })

    for query in queries:
        encoded_query = urllib.parse.quote(query)
        urls.append({
            "source": "WorkAtAStartup",
            "url": f"https://www.workatastartup.com/jobs?query={encoded_query}"
        })

    for query in queries:
        encoded_query = urllib.parse.quote(query)
        urls.append({
            "source": "Wellfound",
            "url": f"https://wellfound.com/jobs?query={encoded_query}"
        })

    for query in queries:
        params = {
            "q": query,
            "page": 1
        }
        if primary_location and primary_location.lower() != "remote":
            params["country"] = "IN" if is_india_location(primary_location) else "US"
        if job_type:
            params["employment_type"] = job_type
        if exp_level:
            level = exp_level.lower()
            if "fresh" in level or "entry" in level or "student" in level:
                params["seniority"] = "entry-level"
            elif "junior" in level:
                params["seniority"] = "junior"
            elif "senior" in level:
                params["seniority"] = "senior"
            elif "mid" in level:
                params["seniority"] = "mid-level"
            elif "lead" in level:
                params["seniority"] = "lead"

        query_string = urllib.parse.urlencode(params)
        urls.append({
            "source": "Himalayas",
            "url": f"https://himalayas.app/jobs/api/search?{query_string}"
        })

    if _jobspy_enabled():
        rw = _jobspy_results_wanted()
        india = is_india_location(primary_location)
        for source_name, site_key in JOBSPY_SITE_KEYS.items():
            if source_name == "Naukri" and not india:
                continue
            urls.append({
                "source": source_name,
                "url": f"jobspy://{site_key}?results_wanted={rw}",
            })

    if allowed_sources:
        host_aliases = {
            "boards.greenhouse.io": "greenhouse",
            "jobs.lever.co": "lever",
            "remoteok.com": "remoteok",
        }
        normalized = set(allowed_sources)
        for a in list(allowed_sources):
            if a in host_aliases:
                normalized.add(host_aliases[a])
        urls = [u for u in urls if u["source"].lower() in normalized]

    return urls
