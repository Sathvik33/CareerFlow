import asyncio
import os
import random
import re

import pandas as pd
from app.agents.url_generator import generate_dynamic_urls
from app.agents.connectors.arbeitnow import ArbeitnowConnector
from app.agents.connectors.remoteok import RemoteOKConnector
from app.agents.connectors.greenhouse import GreenhouseConnector
from app.agents.connectors.lever import LeverConnector
from app.agents.connectors.usajobs import USAJobsConnector
from app.agents.connectors.weworkremotely import WeWorkRemotelyConnector
from app.agents.connectors.workatastartup import WorkAtAStartupConnector
from app.agents.connectors.wellfound import WellfoundConnector
from app.agents.connectors.himalayas import HimalayasConnector
from app.agents.connectors.adzuna import AdzunaConnector
from app.agents.connectors.jobspy import JobSpyConnector
from app.agents.connectors.utils import connector_timeout_seconds
from app.models.preference import UserPreference

_jobspy = JobSpyConnector()

CONNECTOR_MAP = {
    "Arbeitnow": ArbeitnowConnector(),
    "RemoteOK": RemoteOKConnector(),
    "Adzuna": AdzunaConnector(),
    "Greenhouse": GreenhouseConnector(),
    "Lever": LeverConnector(),
    "USAJobs": USAJobsConnector(),
    "WeWorkRemotely": WeWorkRemotelyConnector(),
    "WorkAtAStartup": WorkAtAStartupConnector(),
    "Wellfound": WellfoundConnector(),
    "Himalayas": HimalayasConnector(),
    "Indeed": _jobspy,
    "LinkedIn": _jobspy,
    "Glassdoor": _jobspy,
    "Google": _jobspy,
    "ZipRecruiter": _jobspy,
    "Naukri": _jobspy,
}


async def _fetch_with_timeout(connector, url: str, preferences: UserPreference):
    timeout = connector_timeout_seconds()
    try:
        return await asyncio.wait_for(
            connector.fetch_jobs(url, preferences),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        print(f"Connector timed out after {timeout}s for {url}")
        return []
    except Exception as e:
        print(f"Connector failed for {url}: {e}")
        return e


async def search_jobs(
    preferences: UserPreference,
    max_jobs: int = 50,
    target_websites: list[str] = None,
) -> list[dict]:
    url_targets = generate_dynamic_urls(preferences, target_websites)
    print(f"Generated {len(url_targets)} URLs to fetch.")

    max_concurrent = int(os.environ.get("CONNECTOR_MAX_CONCURRENT", "8"))
    sem = asyncio.Semaphore(max_concurrent)

    async def _bounded(target):
        source = target.get("source")
        url = target.get("url")
        connector = CONNECTOR_MAP.get(source)
        if not connector:
            return []
        async with sem:
            return await _fetch_with_timeout(connector, url, preferences)

    tasks = [_bounded(t) for t in url_targets]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    all_jobs = []

    for result in results:
        if isinstance(result, list):
            all_jobs.extend(result)
        elif isinstance(result, Exception):
            print(f"Connector task failed with exception: {result}")

    if preferences and preferences.roles:
        role_words = set()
        stopwords = {"a", "an", "the", "of", "and", "in", "to", "for", "with", "on", "at"}
        for r in preferences.roles:
            words = re.findall(r"\b[a-z0-9]+\b", r.lower())
            for w in words:
                if w not in stopwords:
                    role_words.add(w)

        if role_words:
            filtered_jobs = []
            for job in all_jobs:
                title_words = set(
                    re.findall(r"\b[a-z0-9]+\b", str(job.get("title", "")).lower())
                )
                desc = str(job.get("description", "")).lower()

                if any(w in title_words for w in role_words) or any(
                    r.lower().strip() in desc for r in preferences.roles if r.strip()
                ):
                    filtered_jobs.append(job)
            all_jobs = filtered_jobs

    if preferences and preferences.experience_level:
        exp = preferences.experience_level.lower()
        exclude_words = []
        if exp in ["student", "fresher", "junior"]:
            exclude_words = [
                "senior", "lead", "principal", "staff", "manager",
                "director", "architect", "sr.",
            ]
        elif exp == "mid":
            exclude_words = [
                "principal", "staff", "director", "architect",
                "intern", "student", "entry", "trainee",
            ]
        elif exp == "senior":
            exclude_words = [
                "junior", "intern", "student", "entry", "fresher", "trainee", "jr.",
            ]

        if exclude_words:
            all_jobs = [
                job
                for job in all_jobs
                if not any(
                    word in str(job.get("title", "")).lower().split()
                    for word in exclude_words
                )
            ]

    random.shuffle(all_jobs)

    limit = max_jobs * 2
    if len(all_jobs) > limit:
        all_jobs = all_jobs[:limit]

    print(f"Total raw jobs collected across all sources (capped for speed): {len(all_jobs)}")

    if not all_jobs:
        return []

    df = pd.DataFrame(all_jobs)

    string_cols = ["company", "title", "location", "description"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].apply(
                lambda x: x.encode("cp1252", "ignore").decode("cp1252")
                if isinstance(x, str)
                else x
            )

    df.replace({"nan": "", "None": "", "Unknown": ""}, inplace=True)

    if "location" in df.columns and "remote" in df.columns:
        df.loc[(df["location"] == "") & (df["remote"] == True), "location"] = "Remote"

    if "company" in df.columns:
        df["company"] = df["company"].replace("", "Unknown Company")

    cleaned_jobs = df.where(pd.notnull(df), None).to_dict(orient="records")

    def clean_nulls_and_win1252(obj):
        if not isinstance(obj, (bool, list, dict)) and pd.isna(obj):
            return None
        if isinstance(obj, str):
            return obj.encode("cp1252", "ignore").decode("cp1252")
        elif isinstance(obj, list):
            return [clean_nulls_and_win1252(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: clean_nulls_and_win1252(v) for k, v in obj.items()}
        return obj

    cleaned_jobs = [clean_nulls_and_win1252(job) for job in cleaned_jobs]

    print(f"Total jobs after Pandas cleaning: {len(cleaned_jobs)}")
    return cleaned_jobs
