import pytest
from fastapi.testclient import TestClient


from src.main import app
from src.tasks.crud.users import UserCRUD
from src.tasks.schemas import UserCreate

TEST_CACHE = {}
test_password = "testpass"

@pytest.fixture()
def client():
    """
    Get a TestClient instance that reads/write to the test database.
    """

    yield TestClient(app)


def login_test(
    client: TestClient, email: str, password: str, response_code: int = 200
):
    response = client.post(
        "/login",
        data={"email": email, "password": password},
    )
    assert response.status_code == response_code, response.json()
    if response.status_code == 200:
        bToken = response.json()["access_token"]
        return {"Authorization": f"Bearer {bToken}"}

    return None


def signup_test(
    client: TestClient, email: str, password: str, response_code: int = 200
):

    response = client.post(
        "/signup",
        data={"email": email, "password": password},
    )
    assert response.status_code == response_code, response.json()
    assert response.status_code == response_code, response.json()
    return None


@pytest.fixture()
def test_admin_user(
    client: TestClient, test_db, test_password: str, test_email: str
) -> dict:
    if "test_email" in TEST_CACHE:
        return TEST_CACHE["test_email"]

    user_crud = UserCRUD(db=test_db)
    user_created = user_crud.create_user(
        UserCreate(
            is_super_admin=True,
            email=test_email,  # type: ignore
            password=test_password,
        ),
    )
    assert user_created.email == test_email


@pytest.fixture()
def test_admin_user_headers(
    client: TestClient, admin_user=test_admin_user
):
    response = client.post(
        "/login", data={"email": admin_user.email, "password": test_password}
    )
    assert response.status_code == 200, response.json()
    bToken = response.json()["access_token"]
    return {"Authorization": f"Bearer {bToken}"}
