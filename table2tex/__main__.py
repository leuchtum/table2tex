from itertools import product
from pathlib import Path
from typing import Any

import click
import pandas as pd
from jinja2 import Environment as JinjaEnv
from jinja2 import PackageLoader, StrictUndefined

from table2tex.configs import GlobalConfig
from table2tex.data import DataEnv
from table2tex.helper import nested_update
from table2tex.io import read_config, read_data
from table2tex.positioning import PositioningTableEnv
from table2tex.superior import SuperiorEnv
from table2tex.table import TableTabularEnv


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
@click.option(
    "-c",
    "--config",
    "cfg_files",
    type=click.Path(exists=True, path_type=Path),
    multiple=True,
)
@click.argument(
    "source_files",
    type=click.Path(exists=True, path_type=Path),
    nargs=-1,
)
def cli(cfg_files: list[Path], source_files: list[Path]) -> None:
    multi_main(cfg_files, source_files)


def multi_main(cfg_files: list[Path], source_files: list[Path]) -> None:
    cfg_c = [read_config(path) for path in cfg_files]
    for source_file in source_files:
        cfg_s, data = read_data(source_file)
        main([*cfg_c, cfg_s], [*cfg_files, source_file], data)


def main(
    cfgs: list[dict[str, str]],
    sources: list[Path],
    data: pd.DataFrame,
) -> None:
    # Merge all the configurations
    buf: dict[Any, Any] = {"sources": sources}
    for cfg in cfgs:
        buf = nested_update(buf, cfg)
    config = GlobalConfig.model_validate(buf)

    # Check data and config coherence
    check_coherence(config, data)

    templates = JinjaEnv(
        loader=PackageLoader("table2tex"),
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
    )

    data_env = DataEnv(
        cell_cfgs=config.produce_cell_cfgs(),
        row_cfgs=config.produce_row_cfgs(),
        col_cfgs=config.produce_col_cfgs(),
        data=data,
    )

    table_tpl = templates.get_template("table_tabular.txt")
    table_env = TableTabularEnv(config.produce_table_cfg(), data_env, table_tpl)

    pos_tpl = templates.get_template("positioning_table.txt")
    pos_env = PositioningTableEnv(config.produce_positioning_cfg(), table_env, pos_tpl)

    superior_tpl = templates.get_template("superior.txt")
    superior_env = SuperiorEnv(config, pos_env, superior_tpl)

    parsed = str(superior_env)
    print(parsed)


if __name__ == "__main__":
    cli()
