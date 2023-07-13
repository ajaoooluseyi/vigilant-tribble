from src.tasks import models
from src.exceptions import GeneralException
from src.config import setup_logger
from src.tasks import schemas
from sqlalchemy.orm import Session


class TaskCRUD:
    def __init__(self, session: Session) -> None:
        self.db = session
        self.logger = setup_logger()

    def get_user_tasks(self, user_id: int):
        return self.db.query(models.Task).filter(models.Task.owner_id == user_id).all()

    def get_user_task_by_ID(self, user_id: int, task_id: int):
        return (
            self.db.query(models.Task)
            .filter(models.Task.owner_id == user_id, models.Task.id == task_id)
            .first()
        )

    def create_task_for_user(self, user_id: int, task: schemas.TaskCreate):
        try:
            db_task = models.Task(
                task=task.task, description=task.description, owner_id=user_id
            )
            self.db.add(db_task)
            self.db.commit()
            self.db.refresh(db_task)
            return db_task
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            self.logger.error(raised_exception)
            raise GeneralException(str(raised_exception))
        finally:
            self.db.rollback()

    def update_task(self, task_id: int, user_id: int, task: str, description: str = None )-> models.Task: 
        try:
            task_to_update = (
                self.db.query(models.Task)
                .filter(models.Task.owner_id == user_id, models.Task.id == task_id)
                .first()
            )
            if task:
                setattr(task_to_update, "task", task)

            if description:
                setattr(task_to_update, "description", description)

            self.db.add(task_to_update)
            self.db.commit()
            self.db.refresh(task_to_update)

            return task_to_update  # type: ignore
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            self.logger.error(raised_exception)
            raise GeneralException(str(raised_exception))
        finally:
            self.db.rollback()

    def mark_as_complete(
        self, task_id: int, user_id: int,
        task: schemas.TaskComplete,
    ):
        try:
            task_to_update = (
                self.db.query(models.Task)
                .filter(models.Task.owner_id == user_id, models.Task.id == task_id)
                .first()
            )

            setattr(task_to_update, "is_complete", task.is_complete)
            self.db.add(task_to_update)
            self.db.commit()
            self.db.refresh(task_to_update)
            return task_to_update
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            self.logger.error(raised_exception)
            raise GeneralException(str(raised_exception))
        finally:
            self.db.rollback()

    def delete_task(
        self, task_id: int, user_id: int,
    ):
        task = (
            self.db.query(models.Task)
            .filter(models.Task.owner_id == user_id, models.Task.id == task_id)
            .first()
        )

        if task is None:
            raise GeneralException("The task does not exist.")
        total_user_tasks_to_delete = (
           self.db.delete(task)
        )    

        return total_user_tasks_to_delete
    
    def total_tasks(self, user_id: int) -> int:  # type: ignore
        query = self.db.query(models.Task)
        if user_id:
            query = query.filter(models.Task.owner_id == user_id)

        return query.count()

