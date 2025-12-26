from server.core.webserver import Depends, HTTPException, Router

from .exceptions import TaskNotFound, TaskValidationError
from .service import TaskService
from .dependencies import get_task_service

router = Router(prefix="")


@router.get("/get")
def get_tasks(service: TaskService = Depends(get_task_service)):
    return service.list_tasks()


@router.post("/create")
def create_task(payload: dict, service: TaskService = Depends(get_task_service)):
    if not isinstance(payload, dict):
        raise HTTPException(400, "JSON body must be an object")
    
    try:
        created = service.create_task(payload)  # type: ignore[arg-type]
        return created
    
    except TaskValidationError as e:
        raise HTTPException(400, e.detail) from e


@router.put("/{id}/complete")
def complete_task(id: str, service: TaskService = Depends(get_task_service)):
    try:
        task_id = int(id)
    except ValueError as e:
        raise HTTPException(400, "Task id must be an integer") from e

    try:
        service.complete_task(task_id)
        return None

    except TaskNotFound as e:
        raise HTTPException(404, "Not Found") from e
