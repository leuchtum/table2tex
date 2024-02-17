from dataclasses import dataclass
from typing import Optional, Protocol

from jinja2 import Template


class _Cfg(Protocol):
    position: str
    caption: Optional[str]
    label: Optional[str]
    centering: Optional[bool]


class _Env(Protocol):
    def __str__(self) -> str:
        ...


@dataclass()
class PositioningTableEnv:
    cfg: _Cfg
    table_env: _Env
    template: Template

    def __str__(self) -> str:
        return self.template.render(**self.__dict__)
