from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import Token
from app.models.user import User
from app.core.security import hash_password, verify_password
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.core.security import create_access_token
from app.core.auth import get_current_user


router=APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/signup", response_model=UserResponse)
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
        db.refresh(new_user)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    return new_user


@router.post("/login", response_model=Token)
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

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_me(
    current_user: User=Depends(get_current_user),
):
    print("Inside Get Me")
    return current_user


from fastapi import Header

@router.get("/test")
def test(
    authorization: str | None = Header(None)
):
    return {
        "authorization": authorization
    }