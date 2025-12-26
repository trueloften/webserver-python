from dataclasses import dataclass

from .entities import TaskEntity
from .models import TaskCreate
from .repositories import TasksRepository

from .exceptions import TaskValidationError


@dataclass(slots=True)
class TaskService:
    repo: TasksRepository

    def list_tasks(self) -> list[TaskEntity]:
        return self.repo.load()

    def create_task(self, payload: TaskCreate) -> TaskEntity:
        title = payload.get("title")
        priority = payload.get("priority")

        if not isinstance(title, str) or not title.strip():
            raise TaskValidationError("Field 'title' is required")
        
        if priority not in ("low", "normal", "high"):
            raise TaskValidationError("Field 'priority' must be one of: low, normal, high")

        tasks = self.repo.load()
        task: TaskEntity = {
            "id": self.repo.next_id(tasks),
            "title": title.strip(),
            "priority": priority,  # type: ignore[typeddict-item]
            "isDone": False,
        }
        tasks.append(task)
        self.repo.save(tasks)
        return task

    def complete_task(self, task_id: int) -> None:
        tasks = self.repo.load()
        tasks = self.repo.mark_complete(tasks, task_id=int(task_id))
        self.repo.save(tasks)
