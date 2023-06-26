from datetime import datetime, timedelta

from dependencies import get_db 
from services import verify_password, SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import models
import schemas
from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException, status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def authenticate_user(username: str, password: str, session: Session):
    user = get_user(session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def get_current_user(
    session: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(session=session, username=username)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user"
        )
    return current_user


def get_user(session: Session, username: str):
    return session.query(models.User).filter(models.User.username == username).first()


def get_users(session: Session):
    return session.query(models.User).all()


def create_user(session: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, hashed_password=user.hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
