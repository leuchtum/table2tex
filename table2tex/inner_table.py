from dataclasses import dataclass

from jinja2 import Template
from pydantic import BaseModel

from table2tex.data import DataEnvironment


class TabularEnvironmentConfig(BaseModel):
    collayout: str


@dataclass()
class TabularEnvironment:
    cfg: TabularEnvironmentConfig
    data_env: DataEnvironment
    template: Template

    def __str__(self) -> str:
        return self.template.render(**self.__dict__)
