from dotenv import load_dotenv
load_dotenv()
import os
from typing import Optional
from fastapi import Header
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User


def get_current_user(
        authorization: str | None = Header(None),
        db: Session = Depends(get_db)):
    print("Inside get curr user")
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )
    try:
        token = authorization.split(" ")[1]
    except:
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization Header"
        )
    try:
        payload=jwt.decode(
            token,
            os.getenv("SECRET_KEY"),
            algorithms=[os.getenv("ALGORITHM")]
        )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    user_id=payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )
    user=db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    return user