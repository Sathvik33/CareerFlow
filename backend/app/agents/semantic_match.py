import numpy as np
from sqlalchemy.orm import Session
from app.models.resume_embedding import ResumeEmbedding
from app.models.job_embedding import JobEmbedding

def compute_semantic_score(db: Session, resume_id: str, job_id: str) -> float:
    # Get embeddings from DB
    resume_emb_record = db.query(ResumeEmbedding).filter_by(resume_id=resume_id).first()
    job_emb_record = db.query(JobEmbedding).filter_by(job_id=job_id).first()

    if not resume_emb_record or not job_emb_record:
        return 0.0

    v1 = np.array(resume_emb_record.embedding)
    v2 = np.array(job_emb_record.embedding)

    # Cosine similarity
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)

    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0

    similarity = dot_product / (norm_v1 * norm_v2)
    return max(0.0, min(100.0, float(similarity) * 100))
