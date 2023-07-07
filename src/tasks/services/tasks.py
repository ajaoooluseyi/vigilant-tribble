# from typing import Union

from sqlalchemy.orm import Session

from src.config import Settings, setup_logger
from src.exceptions import (
    GeneralException,
)

from src.service import (
    BaseService,
    ServiceResult,
    failed_service_result,
    success_service_result
)
from src.tasks import schemas
from src.tasks.crud.tasks import TaskCRUD


class TaskService(BaseService):
    def __init__(
        self, requesting_user: schemas.UserSchema, db: Session, app_settings: Settings
    ) -> None:
        super().__init__(requesting_user, db)  # type: ignore
        self.task_crud = TaskCRUD(db)
        self.requesting_user = requesting_user
        self.app_settings: Settings = (
            app_settings  # add your settings to general settings or change file route
        )
        self.logger = setup_logger()

        if requesting_user is None:
            raise GeneralException("Requesting User was not provided.")

    def create_task_for_user(
        self,
        taskdata: schemas.TaskCreate,
    ):
        try:
            new_task = self.task_crud.create_task_for_user(
                user_id=self.requesting_user.id,
                task=taskdata.task,
                description=taskdata.description,  # type: ignore
            )
            return success_service_result(schemas.TaskOut.from_orm(new_task))
        except GeneralException as raised_exception:
            return failed_service_result(raised_exception)
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

        #  return ServiceResult(data=new_task, success=True)

    def get_user_tasks(self):
        try:
            db_tasks = self.task_crud.get_user_tasks(user_id=self.requesting_user.id)

            return success_service_result(schemas.TaskOut.from_orm(db_tasks))  # return ServiceResult(data=db_tasks, success=True)
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

    def get_user_task_by_ID(self, task_id: int):
        try:
            db_task = self.task_crud.get_user_task_by_ID(
                user_id=self.requesting_user.id, task_id=task_id
            )

            return success_service_result(schemas.TaskOut.from_orm(db_task))  # return ServiceResult(data=db_task, success=True)
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

    def update_task(self, task_id: int, task: schemas.TaskUpdate):
        try:
            db_task = self.task_crud.update_task(
                task_id=task_id, user_id=self.requesting_user.id, task=task.task, description=task.description
            )

            return success_service_result(schemas.TaskOut.from_orm(db_task))  # return ServiceResult(data=db_task, success=True)
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

    def mark_as_complete(
        self,
        task_id: int,
        task: schemas.TaskComplete,
    ):
        try:
            db_task = self.task_crud.mark_as_complete(
                task_id=task_id, user_id=self.requesting_user.id, task=task
            )

            return success_service_result(schemas.TaskOut.from_orm(db_task))  # return ServiceResult(data=db_task, success=True)
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

    def delete_task(
        self,
        task_id: int,
    ):
        try:
            db_task = self.task_crud.delete_task(
                task_id=task_id, user_id=self.requesting_user.id
            )
            return ServiceResult(data=db_task, success=True)
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)
