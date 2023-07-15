from sqlalchemy.orm import Session
from fastapi import Depends
from src.auth.dependencies import get_current_active_user
from src.config import Settings
from src.database import get_db_sess
from src.service import get_settings

from src.users.schemas import UserOut
from src.tasks.services.tasks import TaskService


def initiate_task_service(
    current_user: UserOut = Depends(get_current_active_user),
    db: Session = Depends(get_db_sess),
    app_settings: Settings = Depends(get_settings),
):
    return TaskService(requesting_user=current_user, db=db, app_settings=app_settings)
