from app.dtos.task_dtos import TaskDTO
from app.models.task import Task


class TaskSerializer:

    @staticmethod
    def serialize(task: Task) -> TaskDTO:
        return TaskDTO(id=task.id, name=task.name, created_at=task.created_at)
