import uuid
from datetime import datetime

from app.db import Base
from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(BigInteger, default=uuid.uuid4, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
