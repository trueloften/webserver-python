from server.core.webserver import App

from server.api.v1.dependencies import get_database
from server.modules.tasks.repositories import TasksRepository
from server.modules.tasks.service import TaskService


def get_tasks_repository(app: App) -> TasksRepository:
    return TasksRepository(database=get_database(app))


def get_task_service(app: App) -> TaskService:
    return TaskService(repo=get_tasks_repository(app))


