from dataclasses import dataclass
from typing import Iterable

from server.core.database import Database

from .entities import TaskEntity
from .exceptions import TaskNotFound


@dataclass(slots=True)
class TasksRepository:
    database: Database

    def load(self) -> list[TaskEntity]:
        data = self.database.read_json(default=[])
        if not isinstance(data, list):
            return []

        out: list[TaskEntity] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            
            if {"title", "priority", "isDone", "id"} <= set(item.keys()):
                out.append(item)
        
        return out

    def save(self, tasks: Iterable[TaskEntity]) -> None:
        self.database.write_json(list(tasks))

    def next_id(self, tasks: list[TaskEntity]) -> int:
        if not tasks:
            return 1
        return max(int(t["id"]) for t in tasks) + 1

    def mark_complete(self, tasks: list[TaskEntity], task_id: int) -> list[TaskEntity]:
        found = False
        for t in tasks:
            if int(t["id"]) == int(task_id):
                t["isDone"] = True
                found = True
                break
        
        if not found:
            raise TaskNotFound(task_id)
        
        return tasks


