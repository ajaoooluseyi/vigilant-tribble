import pytest

from fastapi.testclient import TestClient
from src.main import app


TEST_CACHE = {}


def login_test(client: TestClient, username: str, password: str, response_code: int = 200):

    response = client.post(
        "/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == response_code, response.json()
    if response.status_code == 200:
        bToken = response.json()["access_token"]
        return {"Authorization": f"Bearer {bToken}"}

    return None


def signup_test(client: TestClient, username: str, password: str, response_code: int = 200):

    response = client.post(
        "/signup",
        data={"username": username, "password": password},
    )
    assert response.status_code == response_code, response.json()  
    return None


@pytest.fixture()
def client():
    """
    Get a TestClient instance that reads/write to the test database.
    """

    yield TestClient(app)
