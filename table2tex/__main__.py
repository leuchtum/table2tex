from pathlib import Path

import pandas as pd
from jinja2 import Environment, PackageLoader

from table2tex.data import DataEnvironment
from table2tex.inner_table import TabularEnvironment
from table2tex.io import read
from table2tex.outer_table import TableEnvironment
from table2tex.setting import Setting

path = Path("data.xlsx")


def check_coherence(setting: Setting, data: pd.DataFrame) -> None:
    if len(setting.columnlayout.replace("|", "")) != data.shape[1]:
        raise ValueError("Column layout does not match number of columns")


def main() -> None:
    env = Environment(
        loader=PackageLoader("table2tex"),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    cfg_from_file, data = read(path)

    setting = Setting.model_validate(cfg_from_file)

    check_coherence(setting, data)

    data_env = DataEnvironment(setting, data)

    tab_template = env.get_template("TabularEnvironment.txt")
    tab_env = TabularEnvironment(setting, data_env, tab_template)

    table_template = env.get_template("TableEnvironment.txt")
    table_env = TableEnvironment(setting, tab_env, table_template)

    print(table_env)


if __name__ == "__main__":
    main()
