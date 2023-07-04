from typing import Union

from sqlalchemy.orm import Session

from src.config import Settings, setup_logger
from src.exceptions import (
    GeneralException,
)

from src.security import verify_password
from src.service import (
    BaseService,
    ServiceResult,
    failed_service_result,
    success_service_result,
)
from src.tasks import schemas
from src.tasks.crud.users import UserCRUD
from src.users.exceptions import DuplicateUserException, UserNotFoundException
from src.tasks.models import User


class UserService(BaseService):
    def __init__(
        self, requesting_user: schemas.UserSchema, db: Session, app_settings: Settings
    ) -> None:
        super().__init__(requesting_user, db)
        self.users_crud = UserCRUD(db)
        self.requesting_user = requesting_user
        self.app_settings: Settings = (
            app_settings  # add your settings to general settings or change file route
        )
        self.logger = setup_logger()

        """if requesting_user is None:
            raise GeneralException("Requesting User was not provided.")
        """
            
    def create_user(
        self,
        user: schemas.UserCreate,
    ) -> ServiceResult[Union[User, None]]:
        db_user = self.users_crud.get_user(username=user.username)
        if db_user:
            return ServiceResult(
                data=None,
                success=False,
                exception=DuplicateUserException(
                    f"The username is already registered. Try another one."
                ),
            )
        try:
            created_user = self.users_crud.create_user(user)
        except GeneralException as raised_exception:
            return failed_service_result(raised_exception)
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

        return ServiceResult(data=created_user, success=True)

    def get_users(self, skip: int = 0, limit: int = 10) -> ServiceResult:
        try:
            db_users = self.users_crud.get_users(skip=skip, limit=limit)
            total_db_users = self.users_crud.get_total_users()

            users_data = {"total": total_db_users, "data": db_users}
            return ServiceResult(data=users_data, success=True)
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

    def get_user_by_id(self, user_id: int) -> ServiceResult[Union[User, None]]:
        try:
            db_user: User = self.users_crud.get_user_by_id(id=user_id)  # type: ignore
            if not db_user:
                return ServiceResult(
                    data=None,
                    success=False,
                    exception=UserNotFoundException(f"User with ID {id} not found"),
                )

            return success_service_result(db_user)
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

    def get_user(self, username: str) -> ServiceResult[Union[User, None]]:
        try:
            db_user: User = self.users_crud.get_user(username)  # type: ignore
            if not db_user:
                return ServiceResult(
                    data=None,
                    success=False,
                    exception=UserNotFoundException(
                        f"User with username {username} not found"
                    ),
                )
            return success_service_result(db_user)
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

    def authenticate_user(self, username: str, password: str):
        user = self.users_crud.get_user(username)
        if not user:
            raise GeneralException(f"Invalid username or password")
        if not verify_password(password, user.hashed_password):
            raise GeneralException(f"Invalid username or password")
        return user
