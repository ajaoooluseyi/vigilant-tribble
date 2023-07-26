"""Contains the DB modules"""
import uuid
from sqlalchemy.dialects import postgresql
from src.database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Task(Base):
    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement="auto",
    )
    task = Column(String, index=True)
    description = Column(String, index=True)
    is_complete = Column(Boolean, default=False)
    owner_id = Column(postgresql.UUID(as_uuid=True), ForeignKey("users.id"))

    owner = relationship("User")
