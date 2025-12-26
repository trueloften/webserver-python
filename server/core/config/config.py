import os
import json

from typing import TypedDict

from .settings import (
    APISettings,
    LoggingSettings,
    DatabaseSettings
)


class Config(TypedDict):
    api: APISettings
    logging: LoggingSettings
    database: DatabaseSettings


def _load_config() -> Config:
    if not (config_path := os.getenv("CONFIG_PATH")):
        raise FileNotFoundError("CONFIG_PATH variable must be specified!")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError("The configuration file does not exist.")

    config_raw: str = None    
    with open(config_path, "r") as config_file:
        config_raw = config_file.read()
    
    config_parsed = json.loads(config_raw)

    return Config(
        api=config_parsed["api"],
        logging=config_parsed["logging"],
        database=config_parsed["database"]
    )

# Singleton
cfg = _load_config()
