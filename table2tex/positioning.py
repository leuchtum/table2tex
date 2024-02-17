from dataclasses import dataclass
from typing import Optional

from jinja2 import Template
from pydantic import BaseModel

from table2tex.table import TableTabularEnv


class PositioningConfig(BaseModel):
    caption: Optional[str] = None
    label: Optional[str] = None
    centering: Optional[bool] = None
    position: str = "htbp"


@dataclass()
class PositioningTableEnv:
    cfg: PositioningConfig
    table_env: TableTabularEnv
    template: Template

    def __str__(self):
        return self.template.render(**self.__dict__)
