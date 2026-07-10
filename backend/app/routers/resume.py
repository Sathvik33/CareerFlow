import os
import pdfplumber
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.models.resume_embedding import ResumeEmbedding
from app.schemas.resume import ResumeResponse
from app.utils.security import scan_for_prompt_injection
from app.utils.privacy import mask_pii
from app.agents.embeddings import get_text_chunks, generate_embeddings
from app.agents.resume_parser import parse_resume
from app.models.preference import UserPreference
router = APIRouter(prefix="/resumes", tags=["Resumes"])

@router.post("/upload", response_model=ResumeResponse)
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{current_user.id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    raw_text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    raw_text += text + "\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")

    if scan_for_prompt_injection(raw_text):
        raise HTTPException(status_code=400, detail="Malicious content detected. Upload rejected.")

    safe_text = mask_pii(raw_text)

    existing_resumes = db.query(Resume).filter(Resume.user_id == current_user.id).count()
    is_default = existing_resumes == 0

    resume = Resume(
        user_id=current_user.id,
        title=file.filename,
        file_url=file_path,
        is_default=is_default,
        raw_text=safe_text
    )
    db.add(resume)
    db.flush()

    try:
        parsed_resume = parse_resume(safe_text)
        extracted_skills = parsed_resume.skills
        
        # FIX: Save structured json to resume
        resume.structured_json = parsed_resume.model_dump()
        
        pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
        if not pref:
            pref = UserPreference(
                user_id=current_user.id,
                roles=[],
                locations=[],
                experience_level="fresher",
                job_types=[],
                work_modes=[],
                preferred_skills=extracted_skills,
                salary_min=0,
                salary_max=0
            )
            db.add(pref)
        else:
            existing = set(pref.preferred_skills or [])
            new_skills = existing.union(set(extracted_skills))
            pref.preferred_skills = list(new_skills)
    except Exception as e:
        print(f"Failed to auto-extract skills: {e}")

    chunks = get_text_chunks(safe_text)
    if chunks:
        embeddings = generate_embeddings(chunks)
        for i, chunk in enumerate(chunks):
            emb_record = ResumeEmbedding(
                resume_id=resume.id,
                embedding=embeddings[i],
                chunk_type="auto_chunk"
            )
            db.add(emb_record)

    db.commit()
    db.refresh(resume)

    return resume

@router.get("/", response_model=list[ResumeResponse])
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Resume).filter(Resume.user_id == current_user.id).all()

@router.patch("/{resume_id}/set-default", response_model=ResumeResponse)
def set_default_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    db.query(Resume).filter(Resume.user_id == current_user.id).update({"is_default": False})
    resume.is_default = True
    db.commit()
    db.refresh(resume)

    return resume

@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return resume

@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
        
    db.delete(resume)
    db.commit()
    return None
