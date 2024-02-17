from dataclasses import dataclass
from typing import Optional

from jinja2 import Template

from table2tex.table import TableTabularEnv


@dataclass()
class PositioningConfig:
    position: str
    caption: Optional[str] = None
    label: Optional[str] = None
    centering: Optional[bool] = None


@dataclass()
class PositioningTableEnv:
    cfg: PositioningConfig
    table_env: TableTabularEnv
    template: Template

    def __str__(self) -> str:
        return self.template.render(**self.__dict__)
