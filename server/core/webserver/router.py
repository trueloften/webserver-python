import re
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional


def _join_paths(prefix: str, path: str) -> str:
    prefix = prefix or ""
    path = path or ""

    if prefix:
        if not prefix.startswith("/"):
            prefix = "/" + prefix
        
        if prefix != "/" and prefix.endswith("/"):
            prefix = prefix[:-1]

    if path:
        if not path.startswith("/"):
            path = "/" + path
        
        if path != "/" and path.endswith("/"):
            path = path[:-1]

    if not prefix:
        return path or "/"
    
    if not path or path == "/":
        return prefix or "/"
    
    return prefix + path


def _compile_path(path_template: str) -> tuple[re.Pattern[str], list[str]]:
    """
    Supports simple `{param}` segments, e.g. `/tasks/{task_id}`.
    """
    param_names: list[str] = []

    def repl(match: re.Match[str]) -> str:
        name = match.group(1)
        param_names.append(name)
        return rf"(?P<{name}>[^/]+)"

    escaped = re.sub(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", repl, path_template)
    pattern = "^" + escaped + "$"
    return re.compile(pattern), param_names


@dataclass(slots=True)
class Route:
    method: str
    path_template: str
    endpoint: Callable[..., Any]
    name: Optional[str] = None
    _regex: re.Pattern[str] = None
    _param_names: list[str] = None

    def __post_init__(self) -> None:
        self.method = self.method.upper()
        self._regex, self._param_names = _compile_path(self.path_template)

    def match(self, method: str, path: str) -> Optional[dict[str, str]]:
        if self.method != method.upper():
            return None
        m = self._regex.match(path)
        if not m:
            return None
        return dict(m.groupdict())


class Router:
    def __init__(self, *, prefix: str = ""):
        self.prefix = prefix
        self.routes: list[Route] = []

    def add_api_route(self, path: str, endpoint: Callable[..., Any], *, methods: Iterable[str]) -> None:
        for method in methods:
            full = _join_paths(self.prefix, path)
            self.routes.append(Route(method=method, path_template=full, endpoint=endpoint, name=getattr(endpoint, "__name__", None)))

    def get(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.add_api_route(path, fn, methods=["GET"])
            return fn

        return decorator

    def post(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.add_api_route(path, fn, methods=["POST"])
            return fn

        return decorator

    def put(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.add_api_route(path, fn, methods=["PUT"])
            return fn

        return decorator

    def include_router(self, router: "Router", *, prefix: str = "") -> None:
        effective_prefix = _join_paths(self.prefix, prefix) if prefix else (self.prefix or "")
        for r in router.routes:
            child_path = r.path_template
            full_path = _join_paths(effective_prefix, child_path)
            self.routes.append(Route(method=r.method, path_template=full_path, endpoint=r.endpoint, name=r.name))


