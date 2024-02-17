from dataclasses import dataclass, field
from itertools import product
from typing import Mapping, Optional, Protocol

import numpy as np
import numpy.typing as npt
import pandas as pd


class _CellCfg(Protocol):
    textbf: Optional[bool]


class _RowCfg(Protocol):
    hline_above: Optional[bool]
    hline_below: Optional[bool]
    toprule_above: Optional[bool]
    toprule_below: Optional[bool]
    midrule_above: Optional[bool]
    midrule_below: Optional[bool]
    bottomrule_above: Optional[bool]
    bottomrule_below: Optional[bool]
    textbf: Optional[bool]


class _ColCfg(Protocol):
    textbf: Optional[bool]


class _HasTextBfAttr(Protocol):
    textbf: Optional[bool]


def _build_textbf_mask(
    shape: tuple[int, int],
    cell_cfgs: Mapping[tuple[int, int], _HasTextBfAttr],
    row_cfgs: Mapping[int, _HasTextBfAttr],
    col_cfgs: Mapping[int, _HasTextBfAttr],
) -> npt.NDArray[np.bool_]:
    mask = np.zeros(shape=shape, dtype=bool)
    N, M = shape
    for i, j in product(range(-N, N), range(-M, M)):
        cell_cfg = cell_cfgs.get((i, j))
        row_cfg = row_cfgs.get(i)
        col_cfg = col_cfgs.get(j)

        val = None

        if col_cfg is not None and col_cfg.textbf is not None:
            val = col_cfg.textbf
        if row_cfg is not None and row_cfg.textbf is not None:
            val = row_cfg.textbf
        if cell_cfg is not None and cell_cfg.textbf is not None:
            val = cell_cfg.textbf

        if val is not None:
            mask[i, j] = val

    return mask


class _HasHLineAttr(Protocol):
    hline_above: Optional[bool] = None
    hline_below: Optional[bool] = None


def _build_hline_mask(
    shape: tuple[int, int],
    row_cfgs: Mapping[int, _HasHLineAttr],
) -> tuple[npt.NDArray[np.bool_], npt.NDArray[np.bool_]]:
    N = shape[0]
    before_mask = np.zeros(N, dtype=bool)
    after_mask = np.zeros(N, dtype=bool)
    for i in range(-N, N):
        row_cfg = row_cfgs.get(i)
        if row_cfg is None:
            continue
        before_mask[i] = row_cfg.hline_above
        after_mask[i] = row_cfg.hline_below
    return before_mask, after_mask


@dataclass(kw_only=True)
class DataEnv:
    cell_cfgs: Mapping[tuple[int, int], _CellCfg] = field(default_factory=dict)
    row_cfgs: Mapping[int, _RowCfg] = field(default_factory=dict)
    col_cfgs: Mapping[int, _ColCfg] = field(default_factory=dict)
    data: pd.DataFrame
    _row_prefixes: "pd.Series[str]" = field(init=False)
    _row_suffixes: "pd.Series[str]" = field(init=False)
    _data: pd.DataFrame = field(init=False)

    def _apply_textbf(self) -> None:
        mask = _build_textbf_mask(
            self._data.shape,
            self.cell_cfgs,
            self.row_cfgs,
            self.col_cfgs,
        )
        self._data[mask] = self._data.map(lambda s: f"\\textbf{{{s}}}")

    def _apply_hline(self) -> None:
        before_mask, after_mask = _build_hline_mask(self._data.shape, self.row_cfgs)
        self._row_prefixes[before_mask] += "\\hline\n"
        self._row_suffixes[after_mask] += " \\hline"

    def _finalize(self) -> None:
        self._row_suffixes[0 : self._data.shape[0] - 1] += "\n"

    def _merge(self) -> str:
        and_symbol = pd.Series(["&"] * self._data.shape[0])
        to_be_concat = []
        for i, col in enumerate(self._data.columns):
            to_be_concat.append(self._data[col])
            if i != self._data.shape[1] - 1:
                to_be_concat.append(and_symbol)

        merged = pd.concat(
            [self._row_prefixes, *to_be_concat, self._row_suffixes], axis=1
        )
        return merged.sum(axis=1).sum()  # type: ignore

    def _reset(self) -> None:
        self._row_prefixes = pd.Series([""] * self.data.shape[0])
        self._row_suffixes = pd.Series(["\\\\"] * self.data.shape[0])
        self._data = self.data.copy()

    def __str__(self) -> str:
        self._reset()
        self._apply_textbf()
        self._apply_hline()
        self._finalize()
        return self._merge()
