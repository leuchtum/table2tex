from dataclasses import dataclass

from jinja2 import Template

from table2tex.inner_table import TabularEnvironment
from table2tex.setting import TableEnvironmentConfig


@dataclass()
class TableEnvironment:
    cfg: TableEnvironmentConfig
    inner_table_env: TabularEnvironment
    template: Template

    def __str__(self):
        return self.template.render(**self.__dict__)
