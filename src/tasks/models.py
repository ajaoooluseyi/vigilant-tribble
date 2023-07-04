"""Contains the DB modules"""

from .dependencies import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from src.scopes import UserScope


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    tasks = relationship("Task", back_populates="owner")

    @staticmethod
    def full_scopes() -> list[str]:
        return [
            UserScope.CREATE.value,
            UserScope.READ.value,
            UserScope.UPDATE.value,
            UserScope.DELETE.value,
        ]

    def __repr__(self):
        return self.username


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String, index=True)
    description = Column(String, index=True)
    is_complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="tasks")
