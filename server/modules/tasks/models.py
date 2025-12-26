from typing import Literal, TypedDict


TaskPriority = Literal["low", "normal", "high"]


class TaskCreate(TypedDict):
    title: str
    priority: TaskPriority


