from dataclasses import dataclass

from jinja2 import Template

from table2tex.data import DataEnv


@dataclass()
class TableConfig:
    columnlayout: str


@dataclass()
class TableTabularEnv:
    cfg: TableConfig
    data_env: DataEnv
    template: Template

    def __str__(self) -> str:
        return self.template.render(**self.__dict__)
