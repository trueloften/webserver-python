from server.core.webserver import Router
from server.modules.tasks.routes import router as tasks_router

router = Router(prefix="")


@router.get("/health")
def health():
    return {"status": "ok"}


router.include_router(tasks_router)
