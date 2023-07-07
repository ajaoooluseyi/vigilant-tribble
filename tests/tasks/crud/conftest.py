import pytest

from src.tasks.crud.tasks import TaskCRUD
from src.tasks.crud.users import UserCRUD
from src.tasks.models import User
from src.task.schemas import UserCreate


@pytest.fixture()
def user_crud(test_db):
    return UserCRUD(db=test_db)

@pytest.fixture()
def task_crud(test_db):
    return TaskCRUD(db=test_db)


@pytest.fixture()
def crud_username():
    return "crud_user@regnify.com"


@pytest.fixture()
def crud_username_2():
    return "crud_user_2@regnify.com"


@pytest.fixture()
def crud_user(test_db, crud_username) -> User:
    users_crud: UserCRUD = UserCRUD(db=test_db)
    user: User = users_crud.get_user(crud_username)
    if not user:
        user: User = users_crud.create_user(
            UserCreate(username=crud_username,  password="3")  # type: ignore
        )
    return user


@pytest.fixture()
def crud_user_2(test_db, crud_username_2) -> User:
    users_crud: UserCRUD = UserCRUD(db=test_db)
    user: User = users_crud.get_user_by_email(crud_username_2)
    if not user:
        user: User = users_crud.create_user(
            UserCreate(email=crud_username_2, password="3")  # type: ignore
        )
    return user
