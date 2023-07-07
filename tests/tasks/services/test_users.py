from src.service import ServiceResult
from src.users.exceptions import UserNotFoundException
from src.tasks.models import User
from src.tasks.schemas import UserCreate
from src.tasks.services.users import UserService

from src.config import setup_logger

logger = setup_logger()

prefix = "userTesting"


def test_create_user(user_service: UserService, test_password):
    user: ServiceResult = user_service.create_user(
        UserCreate(
            username=prefix + "1@regnify.com",  # type: ignore
            password=test_password,
        )
    )

    logger.info(user.data)

    assert isinstance(user.data, User)
    assert user.data.username == prefix + "1@regnify.com"


def test_get_user(user_service: UserService):
    # * get user with a valid username
    user = user_service.get_user(prefix + "2@regnify.com")
    assert user.success
    assert isinstance(user.data, User)
    assert user.exception == None

    # * get user with an invalid username
    result: ServiceResult = user_service.get_user("invalid-user@regnify.com")
    assert not result.success
    assert result.data == None
    assert isinstance(result.exception, UserNotFoundException)


def test_get_user_by_id(user_service: UserService):
    # * get user with a valid username
    user = user_service.get_user(prefix + "2@regnify.com")

    user_with_id = user_service.get_user_by_id(user.data.id)
    assert user_with_id.success
    assert isinstance(user_with_id.data, User)
    assert user_with_id.exception == None

    none_result = user_service.get_user_by_id(user_id=5)
    assert not none_result.success
    assert none_result.data == None
    assert isinstance(none_result.exception, UserNotFoundException)
