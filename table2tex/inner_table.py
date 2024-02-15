from dataclasses import dataclass

from jinja2 import Template

from table2tex.data import DataEnvironment
from table2tex.setting import TabularEnvironmentConfig


@dataclass()
class TabularEnvironment:
    cfg: TabularEnvironmentConfig
    data_env: DataEnvironment
    template: Template

    def __str__(self) -> str:
        return self.template.render(**self.__dict__)
