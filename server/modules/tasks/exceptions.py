class TaskError(Exception):
    pass


class TaskNotFound(TaskError):
    def __init__(self, task_id: int):
        super().__init__(f"Task with id={task_id} not found")
        self.task_id = task_id


class TaskValidationError(TaskError):
    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


