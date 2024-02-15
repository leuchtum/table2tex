from pathlib import Path

from jinja2 import Environment, PackageLoader

from table2tex.data import DataEnvironment
from table2tex.inner_table import TabularEnvironment
from table2tex.io import read
from table2tex.outer_table import TableEnvironment
from table2tex.setting import (
    DataEnvironmentConfig,
    TableEnvironmentConfig,
    TabularEnvironmentConfig,
)

path = Path("data.xlsx")


if __name__ == "__main__":
    loader = PackageLoader("table2tex")
    env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

    data_cfg = DataEnvironmentConfig()
    tab_cfg = TabularEnvironmentConfig()
    table_cfg = TableEnvironmentConfig()

    cfg_from_file, data = read(path)

    data_env = DataEnvironment(data_cfg, data)
    tab_env = TabularEnvironment(
        tab_cfg, data_env, env.get_template("TabularEnvironment.txt")
    )
    table_env = TableEnvironment(
        table_cfg, tab_env, env.get_template("TableEnvironment.txt")
    )

    # print(data)
    print(table_env)
