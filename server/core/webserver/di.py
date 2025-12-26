import inspect
from typing import Any, Callable, Optional

from .app import App
from .depends import Depends
from .exceptions import HTTPException
from .request import Request


class _Empty:
    pass


def call_with_injection(
    fn: Callable[..., Any],
    *,
    request: Request,
    app: App,
    dependency_cache: Optional[dict[Callable[..., Any], Any]] = None,
) -> Any:
    cache = dependency_cache if dependency_cache is not None else {}
    sig = inspect.signature(fn)
    kwargs: dict[str, Any] = {}

    for name, param in sig.parameters.items():
        if param.annotation is Request:
            kwargs[name] = request
            continue
        if param.annotation is App:
            kwargs[name] = app
            continue

        if name in request.path_params:
            kwargs[name] = request.path_params[name]
            continue

        q = request.query_params
        if name in q:
            kwargs[name] = q[name]
            continue

        if isinstance(param.default, Depends):
            kwargs[name] = _resolve_dep(param.default, request=request, app=app, cache=cache)
            continue

        if request.method.upper() == "POST" and name in ("body", "data", "payload"):
            try:
                kwargs[name] = request.json()
                continue
            except Exception as e:
                raise HTTPException(400, f"Invalid JSON body: {e}") from e

        if param.default is not inspect._empty:
            kwargs[name] = param.default
            continue

        raise HTTPException(500, f"Cannot resolve parameter '{name}' for {getattr(fn, '__name__', fn)}")

    return fn(**kwargs)


def _resolve_dep(dep: Depends, *, request: Request, app: App, cache: dict[Callable[..., Any], Any]) -> Any:
    fn = dep.dependency
    if dep.use_cache and fn in cache:
        return cache[fn]

    value = call_with_injection(fn, request=request, app=app, dependency_cache=cache)
    if dep.use_cache:
        cache[fn] = value
    return value


