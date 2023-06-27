import pytest

from fastapi.testclient import TestClient
from src.main import app
from src.users.crud.users import UserCRUD
from src.users.schemas import UserCreate


TEST_CACHE = {}


def login_test(client: TestClient, email: str, password: str, response_code: int = 200):

    response = client.post(
        "/token",
        data={"username": email, "password": password},
    )
    assert response.status_code == response_code, response.json()
    if response.status_code == 200:
        bToken = response.json()["access_token"]
        return {"Authorization": f"Bearer {bToken}"}

    return None


@pytest.fixture()
def client():
    """
    Get a TestClient instance that reads/write to the test database.
    """

    yield TestClient(app)


@pytest.fixture()
def test_admin_user(
    client: TestClient, test_db, test_password: str, test_super_admin_email: str
) -> dict:
    if "test_super_admin_email" in TEST_CACHE:
        return TEST_CACHE["test_super_admin_email"]

    user_crud = UserCRUD(db=test_db)
    user_created = user_crud.create_user(
        UserCreate(
            email=test_super_admin_email,  # type: ignore
            first_name="Simple",
            last_name="User",
            password=test_password,
        ),
        should_make_active=True,
        is_super_admin=True,
    )
    assert user_created.email == test_super_admin_email
    assert user_created.is_active
    assert user_created.is_super_admin
    assert user_created.profile.last_name == "User"
    assert user_created.profile.first_name == "Simple"

    TEST_CACHE["test_super_admin_email"] = user_created.__dict__

    return user_created.__dict__


@pytest.fixture()
def test_non_admin_user(
    client: TestClient, test_db, test_password: str, test_non_admin_user_email: str
) -> dict:
    if "test_non_admin_user_email" in TEST_CACHE:
        return TEST_CACHE["test_non_admin_user_email"]

    user_crud = UserCRUD(db=test_db)
    user_created = user_crud.create_user(
        UserCreate(
            email=test_non_admin_user_email,  # type: ignore
            first_name="Simple",
            last_name="User",
            password=test_password,
        ),
        should_make_active=True,
    )
    assert user_created.email == test_non_admin_user_email
    assert user_created.is_active
    assert not user_created.is_super_admin
    assert user_created.profile.last_name == "User"
    assert user_created.profile.first_name == "Simple"

    TEST_CACHE["test_non_admin_user_email"] = user_created.__dict__

    return user_created.__dict__


@pytest.fixture()
def test_user_without_any_roles_user(
    client: TestClient,
    test_db,
    test_password: str,
    test_user_without_any_roles_email: str,
) -> dict:
    if "test_user_without_any_roles_user" in TEST_CACHE:
        return TEST_CACHE["test_user_without_any_roles_user"]

    user_crud = UserCRUD(db=test_db)
    user_created = user_crud.create_user(
        UserCreate(
            email=test_user_without_any_roles_email,  # type: ignore
            first_name="Simple",
            last_name="User",
            password=test_password,
        ),
        should_make_active=True,
    )
    assert user_created.email == test_user_without_any_roles_email
    assert user_created.is_active
    assert not user_created.is_super_admin
    assert user_created.profile.last_name == "User"
    assert user_created.profile.first_name == "Simple"

    TEST_CACHE["test_user_without_any_roles_user"] = user_created.__dict__

    return user_created.__dict__


@pytest.fixture()
def test_admin_user_headers(
    client: TestClient, test_admin_user, test_super_admin_email: str, test_password: str
):
    response = client.post(
        "/token", data={"username": test_super_admin_email, "password": test_password}
    )
    assert response.status_code == 200, response.json()
    bToken = response.json()["access_token"]
    return {"Authorization": f"Bearer {bToken}"}


@pytest.fixture()
def test_non_admin_user_headers(
    client: TestClient,
    test_non_admin_user,
    test_non_admin_user_email: str,
    test_password: str,
):
    response = client.post(
        "/token",
        data={"username": test_non_admin_user_email, "password": test_password},
    )
    assert response.status_code == 200, response.json()
    bToken = response.json()["access_token"]
    return {"Authorization": f"Bearer {bToken}"}


@pytest.fixture()
def test_user_without_any_roles_user_headers(
    client: TestClient,
    test_user_without_any_roles_user,
    test_user_without_any_roles_email: str,
    test_password: str,
):
    response = client.post(
        "/token",
        data={"username": test_user_without_any_roles_email, "password": test_password},
    )
    assert response.status_code == 200, response.json()
    bToken = response.json()["access_token"]
    return {"Authorization": f"Bearer {bToken}"}
