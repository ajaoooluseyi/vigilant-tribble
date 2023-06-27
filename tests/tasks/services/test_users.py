from datetime import timedelta
from jose import jwt
from src.tasks.services.users import create_access_token, access_token_expires
from src.task.config import settings


def test_create_access_token(app_settings):
    data = {
        "username": settings.TEST_USERNAME,
        "password": settings.TEST_PASS,
    }
    access_token_expires_minutes = timedelta(minutes=access_token_expires)
    token = create_access_token(
        data,
        expires_delta=access_token_expires_minutes,
    )

    payload = jwt.decode(
        token=token,
        key=settings.secret_key,
        algorithms=[app_settings.algorithm],
    )

    assert "sub" in payload
    assert payload["sub"] == "testuser"
