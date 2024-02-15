from pathlib import Path

import pandas as pd


def _read_csv(path: Path) -> tuple[dict[str, str], pd.DataFrame]:
    return {}, pd.read_csv(path, header=None, dtype=str)


def _parse_cfg_sheet(cfg_sheet: pd.DataFrame) -> dict[str, str]:
    if cfg_sheet.shape[1] != 2:
        raise ValueError("Invalid configuration sheet")
    cfg_sheet = cfg_sheet.set_index(0, drop=True)
    cfg = cfg_sheet[1].to_dict()
    return cfg


def _read_xlsx(path: Path) -> tuple[dict[str, str], pd.DataFrame]:
    sheets = pd.read_excel(path, header=None, sheet_name=None, dtype=str)
    cfg_sheet = sheets.pop("TABLE2TEX", None)

    if len(sheets) > 1:
        raise ValueError("Multiple sheets not supported")

    data = list(sheets.values())[0]
    cfg = {} if cfg_sheet is None else _parse_cfg_sheet(cfg_sheet)
    return cfg, data


def read(path: Path) -> tuple[dict[str, str], pd.DataFrame]:
    match path.suffix:
        case ".csv":
            return _read_csv(path)
        case ".xlsx":
            return _read_xlsx(path)
        case _:
            raise ValueError("Unsupported file type")
