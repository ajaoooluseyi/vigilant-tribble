from fastapi import APIRouter, Security

from src.config import setup_logger
from src.scopes import UserScope
from src.service import handle_result, success_service_result
from src.tasks.services.tasks import TaskService
from src.tasks.dependencies import get_current_active_user
from src.tasks import schemas

router = APIRouter(tags=["Tasks"], prefix="/tasks")

logger = setup_logger()


@router.get(
    "/user/task",
    response_model=list[schemas.TaskSchema],
)
def get_user_tasks(
    task_service: TaskService = Security(
        get_current_active_user, scopes=[UserScope.READ.value]
    ),
):
    task = task_service.get_user_tasks()
    return handle_result(task, list[schemas.TaskSchema])  # type: ignore


@router.get(
    "/user/task/{task_id}",
    response_model=schemas.TaskSchema,
)
def get_user_task_by_ID(
    task_id: int,
    task_service: TaskService = Security(
        get_current_active_user, scopes=[UserScope.READ.value]
    ),
):
    task = task_service.get_user_task_by_ID(task_id=task_id)
    return handle_result(task, schemas.TaskSchema)  # type: ignore


@router.post(
    "/user/task",
    response_model=schemas.TaskSchema,
)
def create_task_for_user(
    task: schemas.TaskCreate,
    task_service: TaskService = Security(
        get_current_active_user, scopes=[UserScope.CREATE.value]
    ),
):
    task = task_service.create_task_for_user(task)  # type: ignore
    return handle_result(task, schemas.TaskSchema)  # type: ignore


@router.put(
    "/user/task/{task_id}",
    response_model=schemas.TaskSchema,
)
def update_task(
    task_id: int,
    task: schemas.TaskCreate,
    task_service: TaskService = Security(
        get_current_active_user, scopes=[UserScope.UPDATE.value]
    ),
):
    task = task_service.update_task(task=task, task_id=task_id)  # type: ignore
    return handle_result(task, schemas.TaskSchema)  # type: ignore


@router.post(
    "/user/task/{task_id}",
    response_model=schemas.TaskSchema,
)
def mark_as_complete(
    task_id: int,
    task: schemas.TaskComplete,
    task_service: TaskService = Security(
        get_current_active_user, scopes=[UserScope.UPDATE.value]
    ),
):
    task = task_service.mark_as_complete(task_id, task)  # type: ignore
    return handle_result(task, schemas.TaskSchema)  # type: ignore


@router.delete("/user/task/{task_id}")
def delete_task(
    task_id: int,
    task_service: TaskService = Security(
        get_current_active_user, scopes=[UserScope.DELETE.value]
    ),
):
    result = task_service.delete_task(task_id)
    if result.success:
        return handle_result(success_service_result("Task deleted sucessfully"))  # type: ignore
    return handle_result(result)