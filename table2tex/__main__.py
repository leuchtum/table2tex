import sys
from itertools import product
from pathlib import Path
from typing import Optional

import click
import pandas as pd
from jinja2 import Environment as JinjaEnv
from jinja2 import PackageLoader, StrictUndefined
from pydantic import Field

from table2tex import __version__
from table2tex.data import CellConfig, ColConfig, DataEnv, RowConfig
from table2tex.io import read
from table2tex.model import StrictModel
from table2tex.positioning import PositioningConfig, PositioningTableEnv
from table2tex.superior import SuperiorEnv
from table2tex.table import TableConfig, TableTabularEnv


class GlobalConfig(StrictModel):
    # Set automatically
    version: str = __version__
    # Non user defined
    source_file: Path
    # User defined
    columnlayout: str
    position: str = "htbp"
    row: dict[int, RowConfig] = Field(default_factory=dict)
    col: dict[int, ColConfig] = Field(default_factory=dict)
    cell: dict[int, dict[int, CellConfig]] = Field(default_factory=dict)
    caption: Optional[str] = None
    label: Optional[str] = None
    centering: Optional[bool] = None
    show_info: bool = True

    def produce_table_cfg(self) -> TableConfig:
        return TableConfig(columnlayout=self.columnlayout)

    def produce_positioning_cfg(self) -> PositioningConfig:
        return PositioningConfig(
            caption=self.caption,
            label=self.label,
            centering=self.centering,
            position=self.position,
        )

    def produce_row_cfgs(self) -> dict[int, RowConfig]:
        return self.row

    def produce_col_cfgs(self) -> dict[int, ColConfig]:
        return self.col

    def produce_cell_cfgs(self) -> dict[tuple[int, int], CellConfig]:
        return {
            (i, j): cell for i, inner in self.cell.items() for j, cell in inner.items()
        }


def check_coherence(cfg: GlobalConfig, data: pd.DataFrame) -> None:
    # Check if the number of rows in the config matches the data
    if len(cfg.columnlayout.replace("|", "")) != data.shape[1]:
        raise ValueError("Column layout does not match data shape")

    # Check if rows specified in the config are in the data
    if set(cfg.row.keys()) - set(range(data.shape[0])):
        raise ValueError("Rows specified in config not in data")

    # Check if columns specified in the config are in the data
    if set(cfg.col.keys()) - set(range(data.shape[1])):
        raise ValueError("Columns specified in config not in data")

    # Check if cells specified in the config are in the data
    possible = product(range(data.shape[0]), range(data.shape[1]))
    if set(cfg.produce_cell_cfgs().keys()) - set(possible):
        raise ValueError("Cells specified in config not in data")


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
    # Combine configs
    cfg_dict = cfg_from_file
    # TODO...

    # Create GlobalConfig
    cfg = GlobalConfig.model_validate(
        {
            **cfg_dict,
            "source_file": source_file,
        }
    )

    print(cfg.cell)
    # Check data and config coherence
    check_coherence(cfg, data)

    templates = JinjaEnv(
        loader=PackageLoader("table2tex"),
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
    )

    data_env = DataEnv(
        cell_cfgs=cfg.produce_cell_cfgs(),
        row_cfgs=cfg.produce_row_cfgs(),
        col_cfgs=cfg.produce_col_cfgs(),
        data=data,
    )

    table_tpl = templates.get_template("table_tabular.txt")
    table_env = TableTabularEnv(cfg.produce_table_cfg(), data_env, table_tpl)

    pos_tpl = templates.get_template("positioning_table.txt")
    pos_env = PositioningTableEnv(cfg.produce_positioning_cfg(), table_env, pos_tpl)

    superior_tpl = templates.get_template("superior.txt")
    superior_env = SuperiorEnv(cfg, pos_env, superior_tpl)

    parsed = str(superior_env)
    print(parsed)


if __name__ == "__main__":
    if sys.argv[1:] == ["DEBUG"]:
        path = Path("data.xlsx")
        cfg_from_file, data = read(path)
        main((), path, cfg_from_file, data)
    else:
        cli()
