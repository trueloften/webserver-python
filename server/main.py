import logging

from server.core.config import cfg
from server.core.config.settings import LoggingSettings
from server.core.database import Database
from server.api.api import APIApplication


def main():
    logger = setup_logger(cfg["logging"])
    logger.info("Starting server...")

    logger.info("Initializing database...")
    database = Database(settings=cfg["database"])
    database.initialize()

    logger.info("Initializing API...")
    api = APIApplication(
        database=database,
        settings=cfg["api"]
    )
    api.initialize()

    # Shutdown
    database.shutdown()


def setup_logger(settings: LoggingSettings) -> logging.Logger:
    logging.basicConfig(
        level=settings["level"].upper(),
        format=settings["format"],
        datefmt=settings["date_format"],
    )

    logging.getLogger("httpx").setLevel("INFO")
    logging.getLogger("httpcore").setLevel("INFO")

    return logging.getLogger(__name__)


if __name__ == "__main__":
    main()
