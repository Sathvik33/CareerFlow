from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.preference import UserPreference
from app.schemas.preferences import PreferenceCreate, PreferenceUpdate, PreferenceResponse

router = APIRouter(prefix="/preferences", tags=["Preferences"])

@router.post("/", response_model=PreferenceResponse)
def create_preferences(
    preference_in: PreferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if pref:
        raise HTTPException(status_code=400, detail="Preferences already exist for this user.")

    new_pref = UserPreference(
        user_id=current_user.id,
        **preference_in.model_dump()
    )
    db.add(new_pref)
    db.commit()
    db.refresh(new_pref)
    return new_pref

@router.get("/", response_model=PreferenceResponse)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        pref = UserPreference(
            user_id=current_user.id,
            roles=[],
            locations=[],
            experience_level="fresher",
            job_types=[],
            work_modes=[],
            preferred_skills=[],
            salary_min=0,
            salary_max=0
        )
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return pref

@router.put("/", response_model=PreferenceResponse)
def update_preferences(
    preference_in: PreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    
    if not pref:
        # Auto-create with provided data (upsert behavior)
        pref = UserPreference(
            user_id=current_user.id,
            roles=[],
            locations=[],
            experience_level="fresher",
            job_types=[],
            work_modes=[],
            preferred_skills=[],
            salary_min=0,
            salary_max=0
        )
        db.add(pref)
        db.flush()

    update_data = preference_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(pref, key, value)

    db.commit()
    db.refresh(pref)
    return pref

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        raise HTTPException(status_code=404, detail="Preferences not found.")

    db.delete(pref)
    db.commit()
    return None
