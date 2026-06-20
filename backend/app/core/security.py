from dotenv import load_dotenv
load_dotenv()
import os

from passlib.context import CryptContext
from datetime import date, timedelta, datetime
from jose import jwt, JWTError

pwd_context=CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(
        plain_password: str,
        hashed_password: str
):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
        data: dict,
        expires_delta: timedelta | None = None
):
    to_encode=data.copy()
    if expires_delta:
        expire=(
            datetime.utcnow() + expires_delta
        )
    else:
        expire=(
            datetime.utcnow()+timedelta(minutes=30)
        )

    to_encode.update(
        {"exp": expire}
    )

    encoded_jwt=jwt.encode(
        to_encode,
        os.getenv("SECRET_KEY"),
        algorithm=os.getenv("ALGORITHM")
    )

    return encoded_jwt

