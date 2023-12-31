from src.config import Settings
from src.service import ServiceResult
from src.tasks.schemas import TaskCreate, TaskOut, TaskUpdate, TaskComplete
from src.tasks.services.tasks import TaskService

prefix = "testtasks"
CUSTOM_Task_NAME = f"{prefix}Custom task"

# * utils


def test_get_user_tasks(db, test_user):
    task_service = TaskService(
        db=db, app_settings=Settings(), requesting_user=test_user
    )
    result = task_service.get_user_tasks(
        start=0,
        limit=10,
    )
    assert isinstance(result, ServiceResult)
    assert result.success
    assert isinstance(result.data, TaskOut)
    assert result.data.total > 0
    assert isinstance(result.data.tasks, list)

    return result.data.tasks


def test_create_task_for_user(test_db, test_user):
    task_service = TaskService(
        db=test_db, app_settings=Settings(), requesting_user=test_user
    )
    task_result = task_service.create_task_for_user(
        TaskCreate(task=CUSTOM_Task_NAME, description="description")
    )
    assert isinstance(task_result, ServiceResult)
    assert task_result.success
    assert task_result.data.task == CUSTOM_Task_NAME

    task_name = CUSTOM_Task_NAME + " 2"
    task_result = task_service.create_task(
        TaskCreate(task=task_name, description="description")
    )
    assert isinstance(task_result, ServiceResult)
    assert task_result.success
    assert task_result.data.task == task_name


def test_get_user_task_by_ID(test_db, test_user):
    task_service = TaskService(
        db=test_db, app_settings=Settings(), requesting_user=test_user
    )
    task = task_service.get_user_tasks()
    assert task.data.total > 0
    result = task_service.get_user_task_by_ID(task[0].id)
   
    assert isinstance(result, ServiceResult)
    assert result.success

    # * get a task that does not exist
    result = task_service.get_user_task_by_ID(99969699)

    assert isinstance(result, ServiceResult)
    assert not result.success


def test_update_task(test_db, test_user):
    task_service = TaskService(
        db=test_db, app_settings=Settings(), requesting_user=test_user
    )
    tasks = task_service.get_user_tasks()
    assert tasks.data.total > 0
    result = task_service.get_user_task_by_ID(tasks[0].id)

    assert isinstance(result, ServiceResult)
    assert isinstance(result.data, TaskOut)
    task = result.data

    update = TaskUpdate(task="updated task", description="updated description")

    edited_result = task_service.update_task(
        task.id, task=update
    )
    assert isinstance(edited_result, ServiceResult)

    result = task_service.get_user_task_by_ID(task.id)
    assert isinstance(result, ServiceResult)
    assert isinstance(result.data, TaskOut)
    assert edited_result.data.task == update.task
    assert edited_result.data.description == update.description


def test_mark_as_complete(test_db, test_user):
    task_service = TaskService(
        db=test_db, app_settings=Settings(), requesting_user=test_user
    )
    tasks = task_service.get_user_tasks()
    result = task_service.get_user_task_by_ID(tasks[0].id)

    assert isinstance(result, ServiceResult)
    assert isinstance(result.data, TaskOut)
    task = result.data
    complete = TaskComplete(is_complete=True)

    edited_result = task_service.mark_as_complete(
        task.id, task=complete
    )
    assert isinstance(edited_result, ServiceResult)

    result = task_service.get_user_task_by_ID(task.id)
    assert isinstance(result, ServiceResult)
    assert isinstance(result.data, TaskOut)
    assert edited_result.data.is_complete == complete.is_complete


def test_delete_task(test_db, test_user):
    task_service = TaskService(
        requesting_user=test_user, db=test_db, app_settings=Settings()
    )

    tasks = task_service.get_user_tasks()
    task = tasks[0]
    assert isinstance(task, TaskOut)

    # * delete the task
    delete_result = task_service.delete_task(task.id)
    assert delete_result.success
    result = task_service.get_user_task_by_ID(task.id)
    assert not result.success