from typing import Union
from src.tasks import models, schemas
from sqlalchemy.orm import Session
from src.security import get_password_hash
from src.exceptions import GeneralException
from src.config import setup_logger
from sqlalchemy.exc import IntegrityError


class UserCRUD:
    def __init__(self, session: Session) -> None:
        self.db = session
        self.logger = setup_logger()

    def get_user(self, username: str):
        return (
            self.db.query(models.User).filter(models.User.username == username).first()
        )

    def get_user_by_id(self, user_id: int) -> Union[models.User, None]:
        return self.db.query(models.User).filter(models.User.id == user_id).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> list[models.User]:
        return self.db.query(models.User).offset(skip).limit(limit).all()

    def get_total_users(self) -> int:
        return self.db.query(models.User).count()

    def create_user(self, user: schemas.UserCreate):
        try:
            hashed_password = get_password_hash(password=user.password)
            db_user = models.User(
                username=user.username, hashed_password=hashed_password
            )
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError as raised_exception:
            self.logger.exception(raised_exception)
            self.logger.error(raised_exception)
            raise GeneralException("A user with that username already exist.")
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            self.logger.error(raised_exception)
            raise GeneralException(str(raised_exception))
        finally:
            self.db.rollback()
