"""Contains the DB modules"""
import uuid
from src.database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Task(Base):
    __tablename__ = "tasks"

    id = Column(
        primary_key=True, index=True, default=uuid.uuid4
    )
    task = Column(String, index=True)
    description = Column(String, index=True)
    is_complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="tasks")
