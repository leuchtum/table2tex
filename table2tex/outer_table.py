from dataclasses import dataclass

from jinja2 import Template
from pydantic import BaseModel

from table2tex.inner_table import TabularEnvironment


class TableEnvironmentConfig(BaseModel):
    position: str | None = None
    caption: str | None = None
    centering: bool = True


@dataclass()
class TableEnvironment:
    cfg: TableEnvironmentConfig
    inner_table_env: TabularEnvironment
    template: Template

    def __str__(self):
        return self.template.render(**self.__dict__)
