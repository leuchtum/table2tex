import sys
from pathlib import Path

import click
import pandas as pd
from jinja2 import Environment, PackageLoader, StrictUndefined
from pydantic import BaseModel, Field

from table2tex import __version__
from table2tex.data import CellConfig, ColConfig, DataEnv, RowConfig
from table2tex.io import read
from table2tex.positioning import PositioningConfig, PositioningTableEnv
from table2tex.superior import SuperiorEnv
from table2tex.table import TableConfig, TableTabularEnv

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
    table: PositioningConfig = Field(default_factory=lambda: PositioningConfig())
    tabular: TableConfig = Field(default_factory=lambda: TableConfig())


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

    data_env = DataEnv(
        cell_cfgs=cfg.cell,
        row_cfgs=cfg.row,
        col_cfgs=cfg.col,
        data=data,
    )

    table_template = templates.get_template("table_tabular.txt")
    table_env = TableTabularEnv(cfg.tabular, data_env, table_template)

    pos_template = templates.get_template("positioning_table.txt")
    pos_env = PositioningTableEnv(cfg.table, table_env, pos_template)

    superior_template = templates.get_template("superior.txt")
    superior_env = SuperiorEnv(cfg, pos_env, superior_template)

    parsed = str(superior_env)
    print(parsed)


if __name__ == "__main__":
    if sys.argv[1:] == ["DEBUG"]:
        path = Path("data.xlsx")
        cfg_from_file, data = read(path)
        main((), path, cfg_from_file, data)
    else:
        cli()
