from dataclasses import dataclass
from typing import Protocol

import pandas as pd


class _Config(Protocol):
    add_hline: bool
    add_toprule: bool
    add_bottomrule: bool
    add_midrule_after_rows: list[int]
    bf_rows: list[int]
    bf_cols: list[int]
    highlight_rows: list[int]
    highlight_color: str


@dataclass()
class DataEnvironment:
    cfg: _Config
    data: pd.DataFrame

    def _parse_cell(self, row_idx: int, col_idx: int, value: str) -> str:
        if row_idx in self.cfg.bf_rows or col_idx in self.cfg.bf_cols:
            value = "\\textbf{" + value + "}"
        return value

    def _parse_row_prefix(self, row_idx: int) -> str:
        buf = []
        if self.cfg.add_hline and row_idx == 0:
            buf.append("\\hline\n")
        if self.cfg.add_toprule and row_idx == 0:
            buf.append("\\toprule\n")
        if row_idx in self.cfg.highlight_rows:
            buf.append("\\rowcolor[HTML]{" + self.cfg.highlight_color + "}\n")
        return "".join(buf)

    def _parse_row_suffix(self, row_idx: int) -> str:
        buf = []
        if self.cfg.add_hline:
            buf.append(" \\hline")
        if row_idx in self.cfg.add_midrule_after_rows:
            buf.append(" \\midrule")
        if self.cfg.add_bottomrule and row_idx == self.data.shape[0] - 1:
            buf.append("\n\\bottomrule")
        return "".join(buf)

    def _parse_row(self, row_idx: int, row: pd.Series) -> str:
        parsed = "&".join(
            [self._parse_cell(row_idx, col_idx, cell) for col_idx, cell in row.items()]
        )
        parsed += "\\\\"
        prefix = self._parse_row_prefix(row_idx)
        suffix = self._parse_row_suffix(row_idx)
        return f"{prefix}{parsed}{suffix}"

    def _parse_rows(self) -> list[str]:
        parsed = [
            self._parse_row(row_idx, row) for row_idx, row in self.data.iterrows()
        ]
        return parsed

    def __str__(self) -> str:
        return "\n".join(self._parse_rows())
