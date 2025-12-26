from typing import Any
from dataclasses import dataclass, field

from .router import Router

from server.core.config.settings import APISettings


@dataclass(slots=True)
class App:
    database: Any
    settings: APISettings
    state: dict[str, Any] = field(default_factory=dict)
    router: Router = field(default_factory=Router)

    def include_router(self, router: Router, *, prefix: str = "") -> None:
        self.router.include_router(router, prefix=prefix)

    def get(self, path: str):
        return self.router.get(path)

    def post(self, path: str):
        return self.router.post(path)

    def put(self, path: str):
        return self.router.put(path)


