from fastapi import (
    APIRouter,
    Depends,
    Body,
    Security,
)
from fastapi.security import OAuth2PasswordRequestForm

from src.config import setup_logger
from src.pagination import CommonQueryParams
from src.service import handle_result
from src.tasks.services.users import UserService
from src.tasks.dependencies import (
    get_current_active_user,
    access_token_expires,
    revoked_tokens,
    create_access_token,
)
from src.tasks import schemas


router = APIRouter(tags=["Users for Tasks"], prefix="/taskusers")

logger = setup_logger()


@router.get("/", response_model=list[schemas.UserSchema])
def read_users(
    common: CommonQueryParams = Depends(),
    user_service: UserService = Depends(),
):
    result = user_service.get_users(skip=common.skip, limit=common.limit)
    return handle_result(result, list[schemas.UserSchema])  # type: ignore


@router.get(
    "/{user_id}",
    response_model=schemas.UserSchema,
)
def read_user(
    user_id: int,
    user_service: UserService = Depends(),
):
    result = user_service.get_user_by_id(id=user_id)
    return handle_result(result, schemas.UserSchema)  # type: ignore


@router.post(
    "/signup",
    response_model=schemas.UserSchema,
)
def signup(
    payload: schemas.UserCreate = Body(),
    user_service: UserService = Depends(),
):
    result = user_service.create_user(user=payload)

    return result


@router.post("/login", response_model=schemas.Token)
def login(
    payload: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(),
):
    user = user_service.authenticate_user(payload.username, payload.password)

    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(token: str = Security(get_current_active_user)):
    revoked_tokens.add(token)
    return {"Success": "Logged out successfully"}
