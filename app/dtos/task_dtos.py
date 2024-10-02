from typing import List
from datetime import datetime

from pydantic import BaseModel, field_serializer


class TaskDTO(BaseModel):
    id: int
    name: str
    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(value, serialization_info):
        return value.strftime("%Y-%m-%d")


class TaskCreateDTO(BaseModel):
    name: str


class TaskListParametersDTO(BaseModel):
    page: int = 1
    per_page: int = 10


class TaskListResponseDTO(BaseModel):
    parameters: TaskListParametersDTO
    tasks: List[TaskDTO] = []
