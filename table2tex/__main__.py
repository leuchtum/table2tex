import sys
from itertools import product
from pathlib import Path

import click
import pandas as pd
from jinja2 import Environment as JinjaEnv
from jinja2 import PackageLoader, StrictUndefined

from table2tex.configs import GlobalConfig
from table2tex.data import DataEnv
from table2tex.io import read
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
    "--config-file",
    "config_files",
    type=click.Path(exists=True, path_type=Path),
    multiple=True,
)
@click.argument(
    "source_file",
    type=click.Path(exists=True, path_type=Path),
    nargs=1,
)
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
