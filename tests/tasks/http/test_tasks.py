from fastapi.testclient import TestClient

from src.config import setup_logger

logger = setup_logger()

CUSTOM_ROLE_TITLE = "Custom Role"

TEST_CACHE = {}


def test_create_task_for_user(client: TestClient, test_admin_user_headers: dict):
    response = client.post(
        "/tasks/user/task",
        headers=test_admin_user_headers,
        json={
            "task": "task tasks",
            "decscription": "description",
        },
    )
    assert response.status_code == 200, response.content
    assert response.json()["task"] == "task tasks"


def test_get_user_tasks(client: TestClient, test_admin_user_headers: dict):
    response = client.get("/tasks/user/task", headers=test_admin_user_headers)
    assert response.status_code == 200, response.json()
    assert len(response.json()["tasks"]) > 0


def test_get_user_task_by_ID(client: TestClient, test_admin_user_headers: dict):
    response = client.get("/tasks/user/task", headers=test_admin_user_headers)
    assert response.status_code == 200, response.json()

    task_id = response.json()["tasks"][0]["id"]

    response = client.get(
        f"/tasks/user/task/{task_id}", headers=test_admin_user_headers
    )
    assert response.status_code == 200, response.json()
    assert response.json()["id"] == task_id


def test_update_task(
    client: TestClient,
    test_admin_user_headers: dict,
):
    response = client.get("/tasks/user/task", headers=test_admin_user_headers)
    assert response.status_code == 200, response.json()

    task_id = response.json()["tasks"][0]["id"]
    task = response.json()["tasks"][0]["task"]
    description = response.json()["tasks"][0]["description"]

    response = client.put(
        f"/user/task{task_id}",
        headers=test_admin_user_headers,
        json={"task": task + " edited", "description": description + "edited"},
    )
    assert response.status_code == 200, response.json()

    assert response.json()["task"] == task + " edited"
    assert response.json()["description"] == description + "edited"


def test_mark_as_complete(
    client: TestClient,
    test_admin_user_headers: dict,
):
    response = client.get("/tasks/user/task", headers=test_admin_user_headers)
    assert response.status_code == 200, response.json()

    task_id = response.json()["tasks"][0]["id"]
    is_complete = True

    response = client.post(
        f"/user/task{task_id}",
        headers=test_admin_user_headers,
        json={"is_complete": is_complete},
    )
    assert response.status_code == 200, response.json()
    assert response.json()["is_complete"] == True


def test_delete_task(
    client: TestClient,
    test_admin_user_headers: dict,
   ):
    # * create a task
    response = client.post(
        "/user/task",
        headers=test_admin_user_headers,
        json={
            "task": "Test Role 1",
            "description": "test description",
        },
    )
    assert response.status_code == 200, response.content
    task_id = response.json()["id"]

    # * delete the task
    response = client.delete(f"/user/task{task_id}", headers=test_admin_user_headers)
    assert response.status_code == 200, response.json()
    result = client.get(
        f"/tasks/user/task/{task_id}", headers=test_admin_user_headers
    )
    assert result.status_code == 403
