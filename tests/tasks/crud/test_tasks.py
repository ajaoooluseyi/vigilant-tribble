from src.tasks.crud.tasks import TaskCRUD
import pytest
from src.tasks.schemas import TaskCreate, TaskUpdate
from src.config import setup_logger
from src.exceptions import BaseConflictException, BaseNotFoundException
from src.pagination import OrderBy, OrderDirection
from src.users.crud.users import UserCRUD
from src.tasks.models import User, Task

logger = setup_logger()

CUSTOM_task_TITLE = "Custom task"


def test_get_user_tasks(task_crud: TaskCRUD, crud_user: User):
    created_tasks = task_crud.get_user_tasks(
        start=0,
        limit=1,
        user_id=(crud_user.id),
    )
    task_under_test = created_tasks[0]

    task = task_crud.get_user_task_by_ID(task_id=task_under_test.id, user_id=(crud_user.id))  # type: ignore
    assert isinstance(task, Task)
    assert task_under_test == task


def test_get_user_task_by_ID(task_crud: TaskCRUD, crud_user: User):
    created_tasks = task_crud.get_user_task_by_ID(
        start=0,
        limit=1,
        user_id=(crud_user.id),
    )
    task_under_test = created_tasks

    task = task_crud.get_user_task_by_ID(task_id=task_under_test.id, user_id=(crud_user.id))  # type: ignore
    assert isinstance(task, Task)
    assert task_under_test == task


def test_create_task_for_user(task_crud: TaskCRUD, crud_user: User):
    task_under_test = "3@regnify.com"
    description = "testdescription"
    task: Task = task_crud.create_task_for_user(
        TaskCreate(task=task_under_test,  description=description, owner_id=crud_user.id)  # type: ignore
    )
    assert task.username == task_under_test
    assert task.description == description


def test_update_task(task_crud: TaskCRUD, crud_user: User):
    task_under_test = "3@regnify.com"
    description = "testdescription"
    maketask: Task = task_crud.create_task_for_user(
        TaskCreate(task=task_under_test,  description=description, owner_id=crud_user.id)  # type: ignore
    )
    task_update_test = "update@regnify.com"
    updatedescription = "updatedescription"
    task: Task = task_crud.update_task(
        TaskUpdate(task=task_update_test,  description=updatedescription, owner_id=crud_user.id)  # type: ignore
    )
    assert task.task == task_update_test
    assert task.description == updatedescription


def test_mark_complete(task_crud: TaskCRUD, crud_user: User):
    is_complete = True
    task: Task = task_crud.mark_complete(
        TaskUpdate(task=is_complete,  task_id=, owner_id=crud_user.id)  # type: ignore
    )
    assert task.is_complete == is_complete

