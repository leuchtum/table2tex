from dataclasses import dataclass
from typing import Protocol

from jinja2 import Template


class _Cfg(Protocol):
    columnlayout: str


class _Env(Protocol):
    def __str__(self) -> str:
        ...


@dataclass()
class TableTabularEnv:
    cfg: _Cfg
    data_env: _Env
    template: Template

    def __str__(self) -> str:
        return self.template.render(**self.__dict__)
