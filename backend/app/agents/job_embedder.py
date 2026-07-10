from app.agents.embeddings import generate_embeddings
from app.models.job_embedding import JobEmbedding
from app.models.job import Job
from sqlalchemy.orm import Session

def embed_jobs(db: Session, jobs: list[Job]) -> None:
    """Generates and stores embeddings for a list of Job objects."""
    for job in jobs:
        # Skip if already has an embedding
        existing = db.query(JobEmbedding).filter_by(job_id=job.id).first()
        if existing:
            continue

        if not job.description:
            continue

        text = job.description[:2000]
        embeddings = generate_embeddings([text])
        if embeddings:
            emb_record = JobEmbedding(
                job_id=job.id,
                embedding=embeddings[0]
            )
            db.add(emb_record)

    db.commit()
