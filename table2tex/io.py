from pathlib import Path

import pandas as pd
import tomllib


def _read_csv(path: Path) -> tuple[dict[str, str], pd.DataFrame]:
    return {}, pd.read_csv(path, header=None, dtype=str)


def _parse_cfg_sheet(cfg_sheet: pd.DataFrame) -> dict[str, str]:
    if cfg_sheet.shape[1] != 2:
        raise ValueError("Invalid configuration sheet")
    cfg_string = "\n".join(["=".join(row) for _, row in cfg_sheet.iterrows()])
    cfg = tomllib.loads(cfg_string)
    return cfg


def _read_xlsx(path: Path) -> tuple[dict[str, str], pd.DataFrame]:
    sheets = pd.read_excel(path, header=None, sheet_name=None, dtype=str)
    cfg_sheet = sheets.pop("TABLE2TEX", None)

    if len(sheets) > 1:
        raise ValueError("Multiple sheets not supported")

    data = list(sheets.values())[0]
    data = data.fillna("")
    cfg = {} if cfg_sheet is None else _parse_cfg_sheet(cfg_sheet)
    cfg["source_file"] = str(path)
    return cfg, data


def read(path: Path) -> tuple[dict[str, str], pd.DataFrame]:
    match path.suffix:
        case ".csv":
            return _read_csv(path)
        case ".xlsx":
            return _read_xlsx(path)
        case _:
            raise ValueError("Unsupported file type")
