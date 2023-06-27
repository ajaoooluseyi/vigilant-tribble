from datetime import datetime, timedelta
from email import header
import pytest
from fastapi.testclient import TestClient

from src.mail import fm
from src.config import Settings, setup_logger
from src.users.dependencies import anonymous_user
from src.users.services.users import UserService
from tests.users.http.conftest import login_test
from src.files.utils import hash_file, hash_bytes

from tests.files.service.test_service_files import FILE_PATH_UNDER_TEST

logger = setup_logger()

email_under_test = "1@regnify.com"
prefix = "http-user"


def test_root_endpoint(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200, response.json()
    assert "message" in response.json()
    assert response.json()["message"] == "Hello, Welcome to REGNIFY"


def test_list_scopes(client: TestClient, test_admin_user_headers: dict):
    response = client.get("/users/list-scopes", headers=test_admin_user_headers)
    assert response.status_code == 200, response.json()
    assert len(response.json()["scopes"]) > 0


def test_can_create_user_with_admin_signup_token(
    client: TestClient, test_admin_user_headers: dict, app_settings: Settings
) -> None:
    user_data = {
        "email": email_under_test,
        "password": "simplePass123",
        "last_name": "",
        "first_name": "",
    }

    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        response = client.post(
            "/users",
            json=user_data,
            headers={
                **test_admin_user_headers,
                "admin-signup-token": app_settings.admin_signup_token,
            },
        )
        assert response.status_code == 200, response.json()
        assert response.json()["is_active"] == True
        assert response.json()["is_super_admin"] == False

        # * test that the mail was not sent
        assert len(outbox) == 0

    # * the use can resend the invite
    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        response = client.post(f"/users/resend-invite?email={email_under_test}")
        assert response.status_code == 200, response.json()
        # * test that the mail was sent
        assert len(outbox) == 1

    user_data = {
        **user_data,
        "email": prefix + email_under_test,
        "is_super_admin": True,
    }
    response = client.post(
        "/users",
        json=user_data,
        headers={
            **test_admin_user_headers,
            "admin-signup-token": app_settings.admin_signup_token,
        },
    )
    assert response.status_code == 200, response.json()
    assert response.json()["is_active"] == True
    assert response.json()["is_super_admin"] == True

    # * when admin signup token is invalid, email must also be sent
    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        user_data = {**user_data, "email": "1" + prefix + email_under_test}
        response = client.post(
            "/users",
            json=user_data,
            headers={
                **test_admin_user_headers,
                "admin-signup-token": "THIS IS WRONG!",
            },
        )
        assert response.status_code == 200, response.json()
        assert response.json()["is_active"] == False
        assert response.json()["is_super_admin"] == False

        # * test the mail has been sent
        assert len(outbox) == 1
        assert outbox[0]["To"] == user_data["email"]

    # * create access begin and access end time
    access_end = datetime.utcnow() + timedelta(days=2)
    access_begin = datetime.utcnow() - timedelta(days=2)
    user_data = {
        **user_data,
        "email": "2" + prefix + email_under_test,
        "access_begin": str(access_begin),
        "access_end": str(access_end),
    }
    response = client.post(
        "/users",
        json=user_data,
        headers={
            **test_admin_user_headers,
            "admin-signup-token": app_settings.admin_signup_token,
        },
    )
    assert response.status_code == 200, response.json()
    assert response.json()["access_begin"] != None
    assert response.json()["access_end"] != None

    # * the user should not be able to login
    token = login_test(client, "2" + prefix + email_under_test, "simplePass123")
    assert token != None

    # * create a user with limited access time
    access_end = datetime.utcnow() - timedelta(days=1)
    access_begin = datetime.utcnow() - timedelta(days=2)
    user_data = {
        **user_data,
        "email": "3" + prefix + email_under_test,
        "access_begin": str(access_begin),
        "access_end": str(access_end),
    }
    response = client.post(
        "/users",
        json=user_data,
        headers={
            **test_admin_user_headers,
            "admin-signup-token": app_settings.admin_signup_token,
        },
    )
    assert response.status_code == 200, response.json()

    # * the user should not be able to login
    token = login_test(
        client, "3" + prefix + email_under_test, "simplePass123", response_code=401
    )

    assert token == None


def test_a_user_can_update_their_names(
    client: TestClient, test_admin_user_headers: dict, test_non_admin_user_headers: dict
):

    response = client.get("/users/token", headers=test_non_admin_user_headers)
    assert response.status_code == 200, response.content
    assert "id" in response.json()
    assert "last_login" in response.json()
    assert response.json()["last_login"] != None

    user_id_under_test = response.json()["id"]

    user_data = {
        "last_name": "Test 1",
        "first_name": "Test 2",
    }
    response = client.put(
        f"/users/{user_id_under_test}", json=user_data, headers=test_admin_user_headers
    )
    assert response.status_code == 200, response.content
    logger.info(response.json())
    assert response.json()["profile"]["last_name"] == "Test 1"
    assert response.json()["profile"]["first_name"] == "Test 2"
    assert len(response.json()["profile"]["avatar_url"]) > 0


def test_a_non_admin_user_can_not_change_their_active_status(
    client: TestClient, test_non_admin_user_headers: dict
):
    response = client.get("/users/token", headers=test_non_admin_user_headers)
    assert response.status_code == 200, response.content
    assert "id" in response.json()
    user_id_under_test = response.json()["id"]

    user_data = {"is_active": False}
    response = client.put(
        f"/users/{user_id_under_test}",
        json=user_data,
        headers=test_non_admin_user_headers,
    )
    assert response.status_code == 403, response.content


def test_an_admin_can_change_active_status_of_any_user(
    client: TestClient, test_admin_user_headers: dict, test_non_admin_user_headers: dict
):
    response = client.get("/users/token", headers=test_non_admin_user_headers)
    assert response.status_code == 200, response.content
    assert "id" in response.json()
    user_id_under_test = response.json()["id"]

    user_data = {"is_active": False}
    response = client.put(
        f"/users/{user_id_under_test}",
        json=user_data,
        headers=test_admin_user_headers,
    )
    assert response.status_code == 200, response.content

    # * the user will now be inactive
    response = client.get("/users/token", headers=test_non_admin_user_headers)
    assert response.status_code == 400, response.content

    user_data = {"is_active": True}
    response = client.put(
        f"/users/{user_id_under_test}",
        json=user_data,
        headers=test_admin_user_headers,
    )
    assert response.status_code == 200, response.content

    response = client.get("/users/token", headers=test_non_admin_user_headers)
    assert response.status_code == 200, response.content
    assert response.json()["is_active"] == True


def test_admin_can_change_a_user_password(
    client: TestClient,
    test_admin_user_headers: dict,
    test_non_admin_user_headers: dict,
    test_non_admin_user: dict,
    test_password: str,
):

    user_data = {"password": test_password}
    response = client.put(
        f"/users/{test_non_admin_user['id']}/admin-change-user-password",
        json=user_data,
        headers=test_admin_user_headers,
    )
    assert response.status_code == 200, response.content

    # * non admin can not change the password
    user_data = {"password": test_password}
    response = client.put(
        f"/users/{test_non_admin_user['id']}/admin-change-user-password",
        json=user_data,
        headers=test_non_admin_user_headers,
    )
    assert response.status_code == 403, response.content


@pytest.mark.asyncio
async def test_create_request_password(client: TestClient, test_non_admin_user: dict):
    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        response = client.post(
            f"/users/request-password-change?email=" + test_non_admin_user["email"],
        )
        assert response.status_code == 200, response.content

        # * test the mail has been sent
        assert len(outbox) == 1
        assert outbox[0]["To"] == test_non_admin_user["email"]


@pytest.mark.asyncio
async def test_user_can_change_password_with_token(
    client: TestClient, test_non_admin_user: dict, test_password, app_settings, test_db
):

    response = client.post(
        "/token",
        data={"username": test_non_admin_user["email"], "password": test_password},
    )
    assert response.status_code == 200, response.content

    user_service = UserService(
        requesting_user=anonymous_user(), db=test_db, app_settings=app_settings
    )
    reset_password_token = user_service.create_request_password(
        test_non_admin_user["email"]
    )

    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        response = client.put(
            "/users/change-user-password/",
            json={"token": reset_password_token.data, "new_password": "newPassword"},
        )
        assert response.status_code == 200, response.content

        # * test the mail has been sent
        assert len(outbox) == 1
        assert outbox[0]["To"] == test_non_admin_user["email"]

    response = client.post(
        "/token",
        data={"username": test_non_admin_user["email"], "password": test_password},
    )
    assert response.status_code == 401, response.content

    # * reset it back to the normal password
    reset_password_token = user_service.create_request_password(
        test_non_admin_user["email"]
    )

    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        response = client.put(
            "/users/change-user-password/",
            json={"token": reset_password_token.data, "new_password": test_password},
        )
        assert response.status_code == 200, response.content

        # * test the mail has been sent
        assert len(outbox) == 1
        assert outbox[0]["To"] == test_non_admin_user["email"]

    response = client.post(
        "/token",
        data={"username": test_non_admin_user["email"], "password": test_password},
    )
    assert response.status_code == 200, response.content


def test_upload_and_download_user_photo(
    client: TestClient,
    test_non_admin_user: dict,
    test_admin_user_headers: dict,
    test_non_admin_user_headers: dict,
):
    user_id = test_non_admin_user["id"]

    endpoint = f"/users/{user_id}/upload-photo"

    with open(FILE_PATH_UNDER_TEST, "rb") as f:
        response = client.put(
            endpoint, headers=test_non_admin_user_headers, files={"file_to_upload": f}
        )
        assert response.status_code == 200, response.json()

    # * admin can upload for another user  right?
    with open(FILE_PATH_UNDER_TEST, "rb") as f:
        response = client.put(
            endpoint, headers=test_admin_user_headers, files={"file_to_upload": f}
        )
        assert response.status_code == 200, response.json()

    endpoint = f"/users/{user_id}/download-photo"
    response = client.get(endpoint, headers=test_non_admin_user_headers)
    assert response.status_code == 200, response.content
    print(response.content)
    assert hash_bytes(response.content) == hash_file(FILE_PATH_UNDER_TEST)
