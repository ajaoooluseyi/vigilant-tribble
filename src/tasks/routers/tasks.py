from .. dependencies import engine, get_db
from .. models import Base, User
from .. import schemas
from .. import services

from sqlalchemy.orm import Session

from fastapi import Depends, APIRouter, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

Base.metadata.create_all(bind=engine)

router = APIRouter(tags=["Tasks"])


# CRUD


@router.get(
    "/user/task",
    response_model=list[schemas.TaskSchema],
    status_code=status.HTTP_200_OK,
)
def get_user_tasks(
    current_user: User = Depends(services.get_current_active_user),
    session: Session = Depends(get_db),
):
    task = get_user_tasks(current_user, session)
    return task


@router.get(
    "/user/task/{task_id}",
    response_model=schemas.TaskSchema,
    status_code=status.HTTP_200_OK,
)
def get_user_task_by_ID(
    task_id: int,
    current_user: User = Depends(services.get_current_active_user),
    session: Session = Depends(get_db),
):
    task = get_user_task_by_ID(task_id, current_user, session)

    return task


@router.post(
    "/user/task", response_model=schemas.TaskSchema, status_code=status.HTTP_201_CREATED
)
def create_task_for_user(
    task: schemas.TaskCreate,
    current_user: User = Depends(services.get_current_active_user),
    session: Session = Depends(get_db),
):
    db_task = create_task_for_user(task, current_user, session)
    return db_task


@router.put(
    "/user/task/{task_id}",
    response_model=schemas.TaskSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
def update_task(
    task_id: int,
    task: schemas.TaskBase,
    current_user: User = Depends(services.get_current_active_user),
    session: Session = Depends(get_db),
):
    task_to_update = update_task(task_id, task, current_user, session)
    return task_to_update


@router.post(
    "/user/task/{task_id}",
    response_model=schemas.TaskSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
def mark_as_complete(
    task_id: int,
    task: schemas.TaskComplete,
    current_user: User = Depends(services.get_current_active_user),
    session: Session = Depends(get_db),
):
    task_to_update = mark_as_complete(task_id, task, current_user, session)
    return task_to_update


@router.delete("/user/task/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(
    task_id: int,
    current_user: User = Depends(services.get_current_active_user),
    session: Session = Depends(get_db),
):
    delete_task(task_id, current_user, session)
    return {"Success": "Task deleted!"}
