"""Pydantic Models"""
from pydantic import BaseModel, constr
from src.schemas import ParentPydanticModel


class TaskBase(BaseModel):
    task: constr(min_length=3)  # type: ignore
    description: str = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskComplete(BaseModel):
    is_complete: bool


class TaskSchema(BaseModel):
    id: int
    task: str
    description: str = None
    is_complete: bool
    owner_id: int

    class Config:
        orm_mode = True


class TaskOut(TaskSchema):
    pass


class ManyTaskOut(ParentPydanticModel):
    tasks: list[TaskSchema]

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class UserSchema(BaseModel):
    email: str
    id: int
    is_active: bool
    tasks: list[TaskSchema]

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str = None
