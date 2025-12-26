import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional


@dataclass(slots=True)
class Response:
    status_code: int = 200
    body: bytes = b""
    headers: dict[str, str] = field(default_factory=dict)

    @staticmethod
    def text(text: str, status_code: int = 200, headers: Optional[Mapping[str, str]] = None) -> "Response":
        hdrs = {"content-type": "text/plain; charset=utf-8"}
        if headers:
            hdrs.update({k.lower(): v for k, v in headers.items()})
        
        return Response(status_code=status_code, body=text.encode("utf-8"), headers=hdrs)

    @staticmethod
    def json(data: Any, status_code: int = 200, headers: Optional[Mapping[str, str]] = None) -> "Response":
        hdrs = {"content-type": "application/json; charset=utf-8"}
        if headers:
            hdrs.update({k.lower(): v for k, v in headers.items()})
        
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        return Response(status_code=status_code, body=raw, headers=hdrs)


