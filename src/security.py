from datetime import datetime, timedelta
from typing import Any

from passlib.context import CryptContext

from sqlalchemy.orm import Session

from jose import jwt

from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException
from fastapi import status
from src.auth.exceptions import invalid_auth_credentials_exception
from src.users import models
from src.users.exceptions import UserNotFoundException

from src.users.schemas import UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token", scopes={"me": "Read information about the current user."}
)


def fake_hash_password(password: str):
    return "fakehashed" + password


def decode_token(token: str, secret_key: str, algorithm: str):
    payload = jwt.decode(
        token=token,
        key=secret_key,
        algorithms=[algorithm],
    )

    return payload


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def get_user(db: Session, username: str) -> models.User:
    user: models.User = db.query(models.User).filter(models.User.email == username).first()  # type: ignore
    if not user:
        raise UserNotFoundException(f"User with email {username} not found")

    # * Load the user_roles
    user.user_roles

    return user


def authenticate_user(db: Session, username: str, password: str):
    user: UserInDB = get_user(db, username)

    if user.access_end is not None and user.access_end < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You can not longer have access to the system. Contact admin.",
        )

    if not verify_password(password, str(user.hashed_password)):
        raise invalid_auth_credentials_exception()

    return user


def create_access_token(
    data: dict[str, Any],
    secret_key: str,
    algorithm: str,
    expires_delta: timedelta = None,  # type: ignore
):
    to_encode: dict[str, Any] = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)

    return encoded_jwt
