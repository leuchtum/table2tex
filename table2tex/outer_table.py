from dataclasses import dataclass
from typing import Protocol

from jinja2 import Template

from table2tex.inner_table import TabularEnvironment


class _Config(Protocol):
    position: str | None = None
    caption: str | None = None
    centering: bool = True


@dataclass()
class TableEnvironment:
    cfg: _Config
    inner_table_env: TabularEnvironment
    template: Template

    def __str__(self):
        return self.template.render(**self.__dict__)
