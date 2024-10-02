from typing import Annotated, Optional

from fastapi import Depends
from app.repositories.task_repo import TaskRepository, get_task_repo
from app.serializers.task_serializer import TaskSerializer
from app.dtos.task_dtos import TaskDTO, TaskCreateDTO, TaskListParametersDTO
from app.models.task import TaskCreate


class TaskService:
    def __init__(self, repo: TaskRepository, serializer: TaskSerializer):
        self.repo = repo
        self.serializer = serializer

    async def get_task(self, task_id: int) -> Optional[TaskDTO]:
        task = await self.repo.get(task_id)
        if task is None:
            return None
        return self.serializer.serialize(task)

    async def create_task(self, task_create_dto: TaskCreateDTO):
        task_create = TaskCreate(name=task_create_dto.name)
        task = await self.repo.create(task_create)
        return self.serializer.serialize(task)

    async def list_tasks(self, parameters: TaskListParametersDTO):
        tasks = await self.repo.list(parameters.page, parameters.per_page)
        return [self.serializer.serialize(task) for task in tasks]


def get_task_service(
    task_repo: Annotated[TaskRepository, Depends(get_task_repo)],
    task_serializer: Annotated[TaskSerializer, Depends(TaskSerializer)],
):
    return TaskService(task_repo, task_serializer)
