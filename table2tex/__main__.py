import pandas as pd
from jinja2 import Environment, PackageLoader

from table2tex.data import DataEnvironment, DataEnvironmentConfig
from table2tex.inner_table import TabularEnvironment, TabularEnvironmentConfig
from table2tex.outer_table import TableEnvironment, TableEnvironmentConfig

loader = PackageLoader("table2tex")
env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)


df = pd.DataFrame(
    {
        0: [
            "Abbreviations",
            "LP",
            "MILP",
            "SP",
            "PTDF",
        ],
        1: [
            "Description",
            "Linear program",
            "Mixed integer linear program",
            "Support point",
            "Power Transfer Distribution Factor",
        ],
    }
)

if __name__ == "__main__":
    data_cfg = DataEnvironmentConfig(add_hline=True)
    tab_cfg = TabularEnvironmentConfig(collayout="ll")
    table_cfg = TableEnvironmentConfig(position="htb", caption="Test caption")
    data_env = DataEnvironment(data_cfg, df)
    tab_env = TabularEnvironment(
        tab_cfg, data_env, env.get_template("TabularEnvironment.txt")
    )
    table_env = TableEnvironment(
        table_cfg, tab_env, env.get_template("TableEnvironment.txt")
    )

    # print(data)
    print(table_env)
