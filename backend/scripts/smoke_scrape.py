from __future__ import annotations

import asyncio
import os
import sys
from types import SimpleNamespace

BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)


def _prefs(role: str = "Software Engineer", location: str = "Hyderabad") -> SimpleNamespace:
    return SimpleNamespace(
        roles=[role],
        preferred_skills=["Python", "React"],
        locations=[location],
        experience_level="mid",
        job_types=["fulltime"],
        salary_min=None,
        salary_max=None,
    )


def _smoke_relevant(title: str, roles: list[str]) -> bool:
    from app.agents.connectors.utils import role_matches

    if role_matches(title, roles):
        return True
    t = (title or "").lower()
    for role in roles:
        r = (role or "").lower()
        if "engineer" in r and "engineer" in t:
            return True
        if "developer" in r and "developer" in t:
            return True
        if "analyst" in r and "analyst" in t:
            return True
    return False


async def _test_jobspy_board(site_label: str, site_key: str, prefs, min_jobs: int = 10):
    from app.agents.connectors.jobspy import JobSpyConnector

    connector = JobSpyConnector()
    url = f"jobspy://{site_key}?results_wanted=15"
    print(f"\n=== JobSpy {site_label} ===")
    jobs = await connector.fetch_jobs(url, prefs)
    print(f"Fetched {len(jobs)} jobs")

    if jobs:
        for j in jobs[:3]:
            print(f"  - {j.get('title')} @ {j.get('company')} ({j.get('location')})")

    roles = prefs.roles
    hits = sum(1 for j in jobs if _smoke_relevant(str(j.get("title") or ""), roles))
    hit_rate = (hits / len(jobs)) if jobs else 0.0
    print(f"relevance hit rate: {hit_rate:.0%} ({hits}/{len(jobs)})")

    ok = len(jobs) >= min_jobs and hit_rate >= 0.6
    return ok, len(jobs), hit_rate, jobs


async def _test_greenhouse():
    from app.agents.connectors.greenhouse import GreenhouseConnector

    prefs = _prefs()
    print("\n=== Greenhouse API (stripe) ===")
    connector = GreenhouseConnector()
    jobs = await connector.fetch_jobs(
        "https://boards-api.greenhouse.io/v1/boards/stripe/jobs",
        prefs,
    )
    if not jobs:
        prefs_loose = _prefs(role="Engineer")
        jobs = await connector.fetch_jobs(
            "https://boards-api.greenhouse.io/v1/boards/stripe/jobs",
            prefs_loose,
        )
    print(f"Fetched {len(jobs)} jobs")
    for j in jobs[:3]:
        print(f"  - {j.get('title')} @ {j.get('company')}")
    return len(jobs) > 0, jobs


async def _test_crawlee():
    from app.agents.connectors.utils import fetch_with_crawlee

    print("\n=== Crawlee / Playwright HTML fetch ===")
    url = "https://www.workatastartup.com/jobs?query=software%20engineer"
    html = await fetch_with_crawlee(url, wait_seconds=3.0)
    length = len(html or "")
    print(f"HTML length: {length}")
    if length == 0:
        print("Crawlee returned empty HTML.")
        return False, 0
    print("Crawlee returned non-empty HTML.")
    return True, length


async def _test_linkedin_best_effort(prefs):
    from app.agents.connectors.jobspy import JobSpyConnector

    print("\n=== LinkedIn (best-effort) ===")
    connector = JobSpyConnector()
    jobs = await connector.fetch_jobs("jobspy://linkedin?results_wanted=5", prefs)
    print(f"Fetched {len(jobs)} LinkedIn jobs")
    if not jobs:
        print("LinkedIn empty/rate-limited — set JOBSPY_PROXIES if needed.")
    else:
        for j in jobs[:2]:
            print(f"  - {j.get('title')} @ {j.get('company')}")
    return jobs


async def main() -> int:
    os.environ.setdefault("JOBSPY_RESULTS_WANTED", "15")
    os.environ.setdefault("CONNECTOR_TIMEOUT_SECONDS", "120")

    location = os.environ.get("SMOKE_LOCATION", "Hyderabad")
    role = os.environ.get("SMOKE_ROLE", "Software Engineer")
    prefs = _prefs(role=role, location=location)

    print(f"Smoke prefs: role={role!r} location={location!r}")

    from app.agents.url_generator import is_india_location

    india = is_india_location(location)
    board_chain = (
        [("Naukri", "naukri"), ("Indeed", "indeed"), ("Google", "google")]
        if india
        else [("Indeed", "indeed"), ("Google", "google"), ("ZipRecruiter", "zip_recruiter")]
    )

    mega_ok = False
    mega_label, mega_n, mega_rate = board_chain[0][0], 0, 0.0
    for label, key in board_chain:
        ok, n, rate, _ = await _test_jobspy_board(label, key, prefs, min_jobs=10)
        mega_label, mega_n, mega_rate = label, n, rate
        if ok:
            mega_ok = True
            break
        print(f"\n{label} did not meet criteria; trying next board...")

    gh_ok, _ = await _test_greenhouse()
    crawlee_ok, _ = await _test_crawlee()
    await _test_linkedin_best_effort(prefs)

    print("\n========== SMOKE SUMMARY ==========")
    print(f"JobSpy mega-board ({mega_label}): {'PASS' if mega_ok else 'FAIL'} "
          f"({mega_n} jobs, {mega_rate:.0%} role hit)")
    print(f"Greenhouse API: {'PASS' if gh_ok else 'FAIL'}")
    print(f"Crawlee HTML: {'PASS' if crawlee_ok else 'FAIL'}")

    if mega_ok and gh_ok:
        print("OVERALL: PASS")
        return 0

    print("OVERALL: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
