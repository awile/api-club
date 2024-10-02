from typing import Annotated, Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.models.task import Task, TaskCreate


class TaskRepository:
    model = Task

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> Optional[Task]:
        return await self.session.get(self.model, id)

    async def create(self, task_create: TaskCreate) -> Task:
        task = Task(**task_create.dict())
        self.session.add(task)
        await self.session.commit()
        return task

    async def list(self, page: int, per_page: int):
        return await self.session.execute(
            self.model.__table__.select().limit(per_page).offset((page - 1) * per_page)
        )


def get_task_repo(
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> TaskRepository:
    return TaskRepository(session=session)
