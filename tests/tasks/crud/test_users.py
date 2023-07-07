from datetime import timedelta
from jose import jwt
from src.security import create_access_token
from src.tasks.crud.users import UserCRUD
from src.tasks.models import User
from src.tasks.schemas import UserCreate

from src.config import setup_logger

 
logger = setup_logger()


def test_create_access_token(app_settings):
    data = {
        "sub": "1@regnify.com",
    }
    access_token_expires = timedelta(minutes=app_settings.access_code_expiring_minutes)
    token = create_access_token(
        data,
        expires_delta=access_token_expires,
        secret_key=app_settings.secret_key,
        algorithm=app_settings.algorithm,
    )

    payload = jwt.decode(
        token=token,
        key=app_settings.secret_key,
        algorithms=[app_settings.algorithm],
    )

    assert "sub" in payload
    assert payload["sub"] == "1@regnify.com"


def test_create_user(test_db):
    user_under_test = "3@regnify.com"
    users_crud: UserCRUD = UserCRUD(session=test_db)
    user: User = users_crud.create_user(
        UserCreate(email=user_under_test,  password="3")  # type: ignore
    )
    assert user.username == user_under_test

