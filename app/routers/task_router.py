from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.services.task_service import get_task_service, TaskService
from app.dtos.task_dtos import (
    TaskDTO,
    TaskCreateDTO,
    TaskListResponseDTO,
    TaskListParametersDTO,
)


task_router = APIRouter(
    prefix="/task",
    tags=["task"],
    responses={404: {"description": "Not found"}},
)

TaskServiceDependency = Annotated[TaskService, Depends(get_task_service)]


@task_router.get("/", response_model=TaskListResponseDTO)
async def list_tasks(
    service: TaskServiceDependency, page: int = 1, page_size: int = 10
) -> TaskListResponseDTO:
    parameters = TaskListParametersDTO(page=page, per_page=page_size)
    tasks = await service.list_tasks(parameters)
    return TaskListResponseDTO(parameters=parameters, tasks=tasks)


@task_router.get("/{task_id}", response_model=TaskDTO)
async def get_task(task_id: int, service: TaskServiceDependency) -> TaskDTO:
    try:
        task = await service.get_task(task_id)
        if task is None:
            raise ValueError()
        return task
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")


@task_router.post("/", response_model=TaskDTO)
async def create_task(
    task_create: TaskCreateDTO, service: TaskServiceDependency
) -> TaskDTO:
    return await service.create_task(task_create)
