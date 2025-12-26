from typing import TypedDict

from .models import TaskPriority


class TaskEntity(TypedDict):
    title: str
    priority: TaskPriority
    isDone: bool
    id: int


