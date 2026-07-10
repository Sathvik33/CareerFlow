import os
import urllib.parse
from app.models.preference import UserPreference

def generate_queries(preferences: UserPreference) -> list[str]:
    """Generate 3-5 optimized search queries based on user preferences."""
    queries = []
    
    roles = preferences.roles if preferences and preferences.roles else ["Software Engineer"]
    skills = preferences.preferred_skills if preferences and preferences.preferred_skills else []
    
    for role in roles[:3]:
        safe_role = role.replace("/", " ")
        queries.append(safe_role)
        if skills:
            for skill in skills[:2]:
                queries.append(f"{safe_role} {skill}")
    
    # Add an explicit remote query if requested
    if preferences and preferences.locations and "remote" in [l.lower() for l in preferences.locations]:
        queries.append(f"Remote {roles[0]}")
        
    unique_queries = list(dict.fromkeys(queries))
    return unique_queries[:5]

def generate_dynamic_urls(preferences: UserPreference, target_websites: list[str] = None) -> list[dict]:
    """Generates dynamic search URLs for every supported job source."""
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
    
    # 1. Arbeitnow
    urls.append({
        "source": "Arbeitnow",
        "url": "https://www.arbeitnow.com/api/job-board-api"
    })
    
    # 2. RemoteOK
    urls.append({
        "source": "RemoteOK",
        "url": "https://remoteok.com/api"
    })
    
    # 3. Adzuna
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
            country = "in" if "india" in primary_location.lower() or "hyderabad" in primary_location.lower() else "us"
            
            urls.append({
                "source": "Adzuna",
                "url": f"https://api.adzuna.com/v1/api/jobs/{country}/search/1?{query_string}"
            })
            
    # 4. USAJobs
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
            
    # 5. Greenhouse (Dynamic company slugs)
    greenhouse_companies = ["openai", "stripe", "notion", "figma"]
    for company in greenhouse_companies:
        urls.append({
            "source": "Greenhouse",
            "url": f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
        })
        
    # 6. Lever
    lever_companies = ["netflix", "canva", "anthropic"]
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
        
    # 8. Work at a Startup
    for query in queries:
        encoded_query = urllib.parse.quote(query)
        urls.append({
            "source": "WorkAtAStartup",
            "url": f"https://www.workatastartup.com/jobs?query={encoded_query}"
        })
        
    # 9. Wellfound
    for query in queries:
        encoded_query = urllib.parse.quote(query)
        urls.append({
            "source": "Wellfound",
            "url": f"https://wellfound.com/jobs?query={encoded_query}"
        })
        
    # 10. Himalayas
    for query in queries:
        params = {
            "q": query,
            "page": 1
        }
        if primary_location and primary_location.lower() != "remote":
            # Very naive country code inference for example
            params["country"] = "IN" if "india" in primary_location.lower() or "hyderabad" in primary_location.lower() else "US"
        if job_type:
            params["employment_type"] = job_type
        if exp_level:
            # Map common user inputs to Himalayas expected formats
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
        
    if allowed_sources:
        urls = [u for u in urls if u["source"].lower() in allowed_sources]
        
    return urls
