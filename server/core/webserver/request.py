import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional
from urllib.parse import parse_qs


@dataclass(slots=True)
class Request:
    method: str
    path: str
    raw_path: str
    headers: Mapping[str, str]
    query_string: str
    body: bytes
    client: Optional[tuple[str, int]] = None
    path_params: dict[str, str] = field(default_factory=dict)
    app: Any = None

    @property
    def query_params(self) -> dict[str, str]:
        parsed = parse_qs(self.query_string, keep_blank_values=True)
        return {k: (v[0] if v else "") for k, v in parsed.items()}

    def json(self) -> Any:
        if not self.body:
            return None

        return json.loads(self.body.decode("utf-8"))


