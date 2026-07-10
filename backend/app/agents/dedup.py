from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.job import Job

def deduplicate_jobs(raw_jobs: list[dict], db: Session) -> list[Job]:
    """
    Deduplicates jobs in-memory and against the DB based on Company, Job Title, and Apply URL.
    Inserts non-duplicates into the database and returns newly inserted Job ORM objects.
    """
    new_jobs = []
    
    # Sort jobs by posted_date desc so we keep the newest if there are duplicates in raw_jobs
    def get_sort_key(j):
        return j.get('posted_date') or j.get('scraped_at')
        
    raw_jobs.sort(key=get_sort_key, reverse=True)
    
    seen = set()
    unique_raw_jobs = []
    
    for job_data in raw_jobs:
        company = job_data.get('company', '').lower().strip()
        title = job_data.get('title', '').lower().strip()
        apply_url = job_data.get('apply_url', '').strip()
        
        # Simple deduplication key
        dedup_key = (company, title, apply_url)
        if dedup_key in seen:
            continue
            
        seen.add(dedup_key)
        unique_raw_jobs.append(job_data)

    for job_data in unique_raw_jobs:
        # Check against DB
        company = job_data.get('company')
        title = job_data.get('title')
        apply_url = job_data.get('apply_url')
        
        exists = db.query(Job).filter(
            or_(
                Job.apply_url == apply_url,
                and_(
                    Job.company.ilike(company),
                    Job.title.ilike(title)
                )
            )
        ).first()
        
        if exists:
            continue
            
        stmt = insert(Job).values(**job_data).on_conflict_do_nothing(
            index_elements=['source', 'external_id']
        ).returning(Job.id)
        
        result = db.execute(stmt)
        inserted_row = result.fetchone()
        if inserted_row:
            db.commit()
            inserted_job = db.query(Job).filter_by(id=inserted_row[0]).first()
            if inserted_job:
                new_jobs.append(inserted_job)
        else:
            db.rollback()
            
    return new_jobs
