import pytest

from src.tasks.crud.users import UserCRUD
from src.tasks.models import User
from src.tasks.schemas import UserCreate

from src.config import Settings, setup_logger
from src.tasks.services.tasks import TaskService
from src.tasks.services.users import UserService

logger = setup_logger()

TEST_CACHE = {}


@pytest.fixture()
def user_service(test_db, test_user):
    if "user_service" in TEST_CACHE:
        return TEST_CACHE["user_service"]

    user_service = UserService(
        db=test_db, requesting_user=test_user, app_settings=Settings()
    )

    TEST_CACHE["user_service"] = user_service

    return user_service


@pytest.fixture()
def task_service(test_db, test_user):
    if "task_service" in TEST_CACHE:
        return TEST_CACHE["role_service"]

    task_service = TaskService(
        db=test_db, requesting_user=test_user, app_settings=Settings()
    )

    TEST_CACHE["task_service"] = task_service

    return task_service


@pytest.fixture()
def test_user(test_db):
    user_under_test = "simpleUser@regnify.com"

    users_crud: UserCRUD = UserCRUD(session=test_db)
    if users_crud.get_user(user_under_test):
        return users_crud.get_user(user_under_test)

    user: User = users_crud.create_user(
        UserCreate(username=user_under_test, password="3")  # type: ignore
    )
    assert user.username == user_under_test
    return user