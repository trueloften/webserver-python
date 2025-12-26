import os
import json

from dataclasses import dataclass
from typing import Any, Optional, TypeVar

from server.core.config.settings import DatabaseSettings

T = TypeVar("T")

def _maybe_migrate_txt_to_json(directory: str, target_name: str) -> None:
    """
    One-time migration helper:
    - if `tasks.txt` exists (old name) and `tasks.json` (new name) does not,
      copy the content as-is (we already stored JSON inside .txt previously).
    """
    legacy = os.path.join(directory, "tasks.txt")
    target = os.path.join(directory, target_name)
    if os.path.exists(target):
        return
    if not os.path.exists(legacy):
        return
    try:
        with open(legacy, "r", encoding="utf-8") as src:
            raw = src.read()
        # validate it is JSON-ish; if not, fall back to empty list
        try:
            json.loads(raw or "[]")
        except json.JSONDecodeError:
            raw = "[]"
        with open(target, "w", encoding="utf-8") as dst:
            dst.write(raw if raw.strip() else "[]")
    except OSError:
        # best-effort migration; ignore if filesystem disallows
        return


@dataclass(slots=True)
class Database:
    settings: DatabaseSettings
    _path: Optional[str] = None

    def initialize(self) -> None:
        directory = self.settings["directory"]
        storage_name = self.settings["storage_name"]
        os.makedirs(directory, exist_ok=True)
        _maybe_migrate_txt_to_json(directory, storage_name)
        self._path = os.path.join(directory, storage_name)
        if not os.path.exists(self._path):
            with open(self._path, "w", encoding="utf-8") as f:
                f.write("[]")

    def shutdown(self) -> None:
        return None

    @property
    def path(self) -> str:
        if not self._path:
            raise RuntimeError("Database is not initialized")
        return self._path

    def read(self) -> str:
        with open(self.path, "r", encoding="utf-8") as f:
            return f.read()

    def write(self, data: str) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(data)

    def read_json(self, default: T) -> T:
        raw = self.read().strip()
        if not raw:
            return default
        
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return default

    def write_json(self, value: Any) -> None:
        self.write(json.dumps(value, ensure_ascii=False))
