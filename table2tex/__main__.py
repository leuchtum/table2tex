from pathlib import Path
from typing import Iterable

import click
import pandas as pd
from jinja2 import Environment, PackageLoader
from pydantic import BaseModel, Field

from table2tex.data import CellConfig, ColConfig, DataEnvironment, RowConfig
from table2tex.inner_table import TabularConfig, TabularEnvironment
from table2tex.io import read
from table2tex.outer_table import TableConfig, TableEnvironment

path = Path("data.xlsx")


class GlobalConfig(BaseModel):
    row: dict[int, RowConfig] = Field(default_factory=dict)
    col: dict[int, ColConfig] = Field(default_factory=dict)
    cell: dict[tuple[int, int], CellConfig] = Field(default_factory=dict)
    table: TableConfig = Field(default_factory=lambda: TableConfig())
    tabular: TabularConfig = Field(default_factory=lambda: TabularConfig())


def check_coherence(cfg: GlobalConfig, data: pd.DataFrame) -> None:
    if len(cfg.tabular.columnlayout.replace("|", "")) != data.shape[1]:
        raise ValueError("Column layout does not match data shape")


@click.command()
@click.option("--config", type=click.Path(exists=True, path_type=Path), multiple=True)
@click.argument("path", type=click.Path(exists=True, path_type=Path), nargs=1)
def main(config: tuple[Path, ...], path: Path) -> None:
    if config:
        raise NotImplementedError("Config files not yet supported")

    cfg_from_file, data = read(path)

    cfg = GlobalConfig.model_validate(cfg_from_file)

    check_coherence(cfg, data)

    templates = Environment(
        loader=PackageLoader("table2tex"),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    data_env = DataEnvironment(
        cell_cfgs=cfg.cell,
        row_cfgs=cfg.row,
        col_cfgs=cfg.col,
        data=data,
    )

    tab_template = templates.get_template("TabularEnvironment.txt")
    tab_env = TabularEnvironment(cfg.tabular, data_env, tab_template)

    table_template = templates.get_template("TableEnvironment.txt")
    table_env = TableEnvironment(cfg.table, tab_env, table_template)

    parsed = str(table_env)
    print(parsed)


if __name__ == "__main__":
    main()
