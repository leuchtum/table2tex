import sys
from pathlib import Path

import click
import pandas as pd
from jinja2 import Environment, PackageLoader, StrictUndefined
from pydantic import BaseModel, Field

from table2tex import __version__
from table2tex.data import CellConfig, ColConfig, DataEnvironment, RowConfig
from table2tex.global_table import GlobalEnvironment
from table2tex.inner_table import TabularConfig, TabularEnvironment
from table2tex.io import read
from table2tex.outer_table import TableConfig, TableEnvironment

path = Path("data.xlsx")


class GlobalConfig(BaseModel):
    # Set automatically
    source_file: Path
    version: str = __version__
    # User defined
    show_info: bool = True
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
def cli(config_files: tuple[Path, ...], source_file: Path) -> None:
    if config_files:
        raise NotImplementedError("Config files not yet supported")

    cfg_from_file, data = read(source_file)
    main(config_files, source_file, cfg_from_file, data)


def main(
    config_files: tuple[Path, ...],
    source_file: Path,
    cfg_from_file: dict[str, str],
    data: pd.DataFrame,
) -> None:
    cfg = GlobalConfig.model_validate(cfg_from_file)

    check_coherence(cfg, data)

    templates = Environment(
        loader=PackageLoader("table2tex"),
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
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

    global_template = templates.get_template("GlobalEnvironment.txt")
    global_env = GlobalEnvironment(cfg, table_env, global_template)

    parsed = str(global_env)
    print(parsed)


if __name__ == "__main__":
    if sys.argv[1:] == ["DEBUG"]:
        path = Path("data.xlsx")
        cfg_from_file, data = read(path)
        main((), path, cfg_from_file, data)
    else:
        cli()
