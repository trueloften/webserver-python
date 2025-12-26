from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass(frozen=True, slots=True)
class Depends:
    dependency: Callable[..., Any]
    use_cache: bool = True
    name: Optional[str] = None


