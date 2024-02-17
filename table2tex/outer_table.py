from dataclasses import dataclass
from typing import Optional

from jinja2 import Template
from pydantic import BaseModel

from table2tex.inner_table import TabularEnvironment


class TableConfig(BaseModel):
    caption: Optional[str] = None
    label: Optional[str] = None
    centering: Optional[bool] = None
    position: str = "htbp"


@dataclass()
class TableEnvironment:
    cfg: TableConfig
    inner_table_env: TabularEnvironment
    template: Template

    def __str__(self):
        return self.template.render(**self.__dict__)
