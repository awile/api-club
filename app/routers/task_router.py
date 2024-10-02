from typing import Annotated

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.sql.expression import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.models import Task

task_router = APIRouter(
    prefix="/task",
    tags=["task"],
    responses={404: {"description": "Not found"}},
)

DBSession = Annotated[AsyncSession, Depends(get_db_session)]


@task_router.get("/")
async def list_tasks(session: DBSession, page: int = 1, page_size: int = 10):
    results = await session.execute(
        select(Task).limit(page_size).offset((page - 1) * page_size)
    )
    tasks = [
        {"id": task.id, "name": task.name, "created_at": task.created_at}
        for task in results.scalars().all()
    ]
    return {"tasks": tasks}


class TaskCreateDTO(BaseModel):
    name: str


@task_router.post("/")
async def create_task(task_create: TaskCreateDTO, session: DBSession):
    task = Task(**task_create.dict())
    session.add(task)
    await session.commit()
    return {"id": task.id, "name": task.name, "created_at": task.created_at}


@task_router.get("/{task_id}")
async def get_task(task_id: int, session: DBSession):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"id": task.id, "name": task.name, "created_at": task.created_at}


class TaskUpdateDTO(BaseModel):
    name: str


@task_router.put("/{task_id}")
async def update_task(task_id: int, task_update: TaskUpdateDTO, session: DBSession):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.name = task_update.name
    await session.commit()
    return {"id": task.id, "name": task.name, "created_at": task.created_at}


@task_router.delete("/{task_id}")
async def delete_task(task_id: int, session: DBSession):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await session.delete(task)
    await session.commit()
    return {"id": task.id, "name": task.name, "created_at": task.created_at}
