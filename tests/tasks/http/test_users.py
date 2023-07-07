from fastapi.testclient import TestClient

from src.config import setup_logger

logger = setup_logger()

user_under_test = "1@regnify.com"
prefix = "http-user"


def test_read_users(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200, response.json()


def test_read_user(client: TestClient) -> None:
    response = client.get("/1")
    assert response.status_code == 200, response.json()
