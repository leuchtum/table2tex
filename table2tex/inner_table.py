from dataclasses import dataclass
from typing import Protocol

from jinja2 import Template

from table2tex.data import DataEnvironment


class _Config(Protocol):
    collayout: str = ""


@dataclass()
class TabularEnvironment:
    cfg: _Config
    data_env: DataEnvironment
    template: Template

    def __str__(self) -> str:
        return self.template.render(**self.__dict__)
