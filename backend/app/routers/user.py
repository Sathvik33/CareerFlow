from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import Token
from app.models.user import User
from app.core.security import hash_password, verify_password
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.core.security import create_access_token, create_refresh_token
from app.core.auth import get_current_user
from jose import jwt, JWTError
import os
from pydantic import BaseModel

class RefreshRequest(BaseModel):
    refresh_token: str


router=APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/signup")
def signup(user: UserCreate, db:Session=Depends(get_db)):
    existing_email=db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="User already exists, Please Login"
        )
    hashed_password=hash_password(user.password)

    new_user=User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password
    )

    try:
        db.add(new_user)
        db.commit()
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    return {"message": "User created successfully"}


@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=404,
            detail="Invalid Credentials"
        )

    if not verify_password(
        user.password,
        existing_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Credentials"
        )

    token = create_access_token(
        data={
            "sub": str(existing_user.id)
        }
    )

    refresh_token = create_refresh_token(
        data={
            "sub": str(existing_user.id)
        }
    )

    return {
        "token": token,
        "refresh_token": refresh_token,
        "message": "Login successful"
    }

@router.post("/refresh")
def refresh_access_token(request: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(
            request.refresh_token,
            os.getenv("SECRET_KEY"),
            algorithms=[os.getenv("ALGORITHM")]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    new_token = create_access_token(data={"sub": str(existing_user.id)})
    return {
        "token": new_token,
        "message": "Token refreshed successfully"
    }


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User=Depends(get_current_user),
):
    return current_user

from app.schemas.user import UserUpdate

@router.put("/me", response_model=UserResponse)
def update_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.email is not None:
        existing = db.query(User).filter(User.email == user_update.email).first()
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = user_update.email
    if user_update.password is not None:
        current_user.password_hash = hash_password(user_update.password)
        
    db.commit()
    db.refresh(current_user)
    return current_user

@router.delete("/me", status_code=204)
def delete_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.delete(current_user)
    db.commit()
    return None