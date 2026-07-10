from rank_bm25 import BM25Okapi
import math

def compute_bm25_score(resume_raw_text: str, jd_raw_text: str) -> float:
    if not resume_raw_text or not jd_raw_text:
        return 0.0

    resume_tokens = resume_raw_text.lower().split()
    jd_tokens = jd_raw_text.lower().split()

    if not resume_tokens or not jd_tokens:
        return 0.0

    bm25 = BM25Okapi([jd_tokens])
    score = bm25.get_scores(resume_tokens)[0]

    # Soft normalization using tanh: maps unbounded BM25 score to 0-100
    normalized_score = math.tanh(score / 10.0) * 100.0
    return round(max(0.0, min(100.0, normalized_score)), 2)
