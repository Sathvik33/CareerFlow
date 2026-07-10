import asyncio
import pandas as pd
from app.agents.url_generator import generate_dynamic_urls
from app.agents.connectors.arbeitnow import ArbeitnowConnector
from app.agents.connectors.remoteok import RemoteOKConnector
from app.agents.connectors.greenhouse import GreenhouseConnector
from app.agents.connectors.lever import LeverConnector
from app.agents.connectors.weworkremotely import WeWorkRemotelyConnector
from app.agents.connectors.workatastartup import WorkAtAStartupConnector
from app.agents.connectors.wellfound import WellfoundConnector
from app.agents.connectors.himalayas import HimalayasConnector
from app.agents.connectors.adzuna import AdzunaConnector
from app.models.preference import UserPreference

async def search_jobs(preferences: UserPreference, max_jobs: int = 50) -> list[dict]:
    """Uses Dynamic URL Generator to fetch jobs from all sources and cleans them with Pandas."""
    
    # 1. Generate URLs
    url_targets = generate_dynamic_urls(preferences)
    print(f"Generated {len(url_targets)} URLs to fetch.")
    
    # 2. Map sources to connector instances
    connector_map = {
        "Arbeitnow": ArbeitnowConnector(),
        "RemoteOK": RemoteOKConnector(),
        "Adzuna": AdzunaConnector(),
        "Greenhouse": GreenhouseConnector(),
        "Lever": LeverConnector(),
        "WeWorkRemotely": WeWorkRemotelyConnector(),
        "WorkAtAStartup": WorkAtAStartupConnector(),
        "Wellfound": WellfoundConnector(),
        "Himalayas": HimalayasConnector()
    }
    
    # 3. Create async tasks for each URL target
    tasks = []
    for target in url_targets:
        source = target.get("source")
        url = target.get("url")
        connector = connector_map.get(source)
        if connector:
            tasks.append(connector.fetch_jobs(url, preferences))
            
    # Gather jobs from all tasks
    results = await asyncio.gather(*tasks, return_exceptions=True)
    all_jobs = []
    
    for result in results:
        if isinstance(result, list):
            all_jobs.extend(result)
        elif isinstance(result, Exception):
            print(f"Connector task failed with exception: {result}")
            
    print(f"Raw jobs collected: {len(all_jobs)}")
    
    if not all_jobs:
        return []
        
    # --- Data Cleaning with Pandas ---
    df = pd.DataFrame(all_jobs)
    
    # 1. Clean strings (strip whitespace)
    string_cols = ["company", "title", "location", "description"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # 2. Handle missing or 'nan' values
    df.replace({"nan": "", "None": "", "Unknown": ""}, inplace=True)
    
    # 3. Fill missing locations with Remote if remote is true
    if "location" in df.columns and "remote" in df.columns:
        df.loc[(df["location"] == "") & (df["remote"] == True), "location"] = "Remote"
        
    # 4. Fill empty companies
    if "company" in df.columns:
        df["company"] = df["company"].replace("", "Unknown Company")
        
    # Convert back to list of dicts and ensure NaN/NaT are converted to None for PostgreSQL
    cleaned_jobs = df.where(pd.notnull(df), None).to_dict(orient="records")
    
    print(f"Total jobs after Pandas cleaning: {len(cleaned_jobs)}")
    return cleaned_jobs

