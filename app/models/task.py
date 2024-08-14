import uuid
from datetime import datetime

from app.models.base import Base
from sqlalchemy import Integer, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
