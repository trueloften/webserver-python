import logging

from server.core.webserver import App, WebServer
from server.core.config.settings import APISettings
from server.core.database import Database

from server.api.v1 import router as v1_router


class APIApplication:
    def __init__(self, database: Database, settings: APISettings):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.database = database
        self.settings = settings

        self.app = App(database=database, settings=settings)

        self.app.include_router(v1_router, prefix=settings["root_path"])

        self._server = WebServer(host=settings["host"], port=settings["port"])

    def initialize(self):
        self._logger.info(
            "Starting webserver on %s:%s (root_path=%s)",
            self.settings["host"],
            self.settings["port"],
            self.settings["root_path"],
        )
        self._server.run(self.app)
