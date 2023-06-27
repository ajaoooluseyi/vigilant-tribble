from models import Task, User
import schemas
import dependencies
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status


class TasksCRUD:        
    def get_user_tasks(
        current_user: User = Depends(dependencies.get_current_active_user),
        session: Session = Depends(dependencies.get_db),
    ):
       task = session.query(Task).filter(Task.owner_id == current_user.id).all()
       if not task:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User Unauthorized"
            )
       return task

    def get_user_task_by_ID(
        task_id: int,
        current_user: User = Depends(dependencies.get_current_active_user),
        session: Session = Depends(dependencies.get_db),
    ):
        task = session.query(Task).filter(Task.owner_id == current_user.id, Task.id == task_id).first()    
        if not task:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User Unauthorized or Task does not exist",
            )
        return task


    def create_task_for_user(
        task: schemas.TaskCreate,
        current_user: User = Depends(dependencies.get_current_active_user),
        session: Session = Depends(dependencies.get_db),
    ):
        db_task = Task(
            task=task.task, description=task.description, owner_id=current_user.id
        )
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task

    def update_task(
        task_id: int,
        task: schemas.TaskBase,
        current_user: User = Depends(dependencies.get_current_active_user),
        session: Session = Depends(dependencies.get_db),
    ):
        task_to_update = (
            session.query(Task)
            .filter(Task.owner_id == current_user.id, Task.id == task_id)
            .first()
        )

        if not task_to_update:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User Unauthorized or Task does not exist",
            )
        
        task_to_update.task = task.task
        task_to_update.description = task.description

        session.commit()
        return task_to_update

    def mark_as_complete(
        task_id: int,
        task: schemas.TaskComplete,
        current_user: User = Depends(dependencies.get_current_active_user),
        session: Session = Depends(dependencies.get_db),
    ):
        task_to_update = (
            session.query(Task)
            .filter(Task.owner_id == current_user.id, Task.id == task_id)
            .first()
        )  

        if not task_to_update:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User Unauthorized or Task does not exist",
            )

        task_to_update.is_complete = task.is_complete

        session.commit()


        return task_to_update

    def delete_task(
        task_id: int,
        current_user: User = Depends(dependencies.get_current_active_user),
        session: Session = Depends(dependencies.get_db),
    ):
        task = (
            session.query(Task)
            .filter(Task.owner_id == current_user.id, Task.id == task_id)
            .first()
        )

        if not task:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User Unauthorized or Task ID does not exist",
            )

        session.delete(task)
        session.commit()
        session.close()
        return {"Success": "Task deleted!"}

