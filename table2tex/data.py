from dataclasses import dataclass, field
from itertools import product
from typing import Mapping, Optional, Protocol

import numpy as np
import numpy.typing as npt
import pandas as pd
from pydantic import BaseModel


class CellConfig(BaseModel):
    textbf: Optional[bool] = None


class RowConfig(BaseModel):
    hline_above: Optional[bool] = None
    hline_below: Optional[bool] = None
    toprule_above: Optional[bool] = None
    toprule_below: Optional[bool] = None
    midrule_above: Optional[bool] = None
    midrule_below: Optional[bool] = None
    bottomrule_above: Optional[bool] = None
    bottomrule_below: Optional[bool] = None
    textbf: Optional[bool] = None


class ColConfig(BaseModel):
    textbf: Optional[bool] = None


class _HasTextBfAttr(Protocol):
    textbf: Optional[bool] = None


def _build_textbf_mask(
    shape: tuple[int, int],
    cell_cfgs: Mapping[tuple[int, int], _HasTextBfAttr],
    row_cfgs: Mapping[int, _HasTextBfAttr],
    col_cfgs: Mapping[int, _HasTextBfAttr],
) -> npt.NDArray[np.bool_]:
    mask = np.zeros(shape=shape, dtype=bool)
    for i, j in product(range(shape[0]), range(shape[1])):
        cell_cfg = cell_cfgs.get((i, j), CellConfig())
        row_cfg = row_cfgs.get(i, RowConfig())
        col_cfg = col_cfgs.get(j, ColConfig())

        val = False

        if col_cfg.textbf is not None:
            val = col_cfg.textbf
        if row_cfg.textbf is not None:
            val = row_cfg.textbf
        if cell_cfg.textbf is not None:
            val = cell_cfg.textbf

        mask[i, j] = val
    return mask


class _HasHLineAttr(Protocol):
    hline_above: Optional[bool] = None
    hline_below: Optional[bool] = None


def _build_hline_mask(
    shape: tuple[int, int],
    row_cfgs: Mapping[int, _HasHLineAttr],
) -> tuple[npt.NDArray[np.bool_], npt.NDArray[np.bool_]]:
    before_mask = np.zeros(shape[0], dtype=bool)
    after_mask = np.zeros(shape[0], dtype=bool)
    for i in range(shape[0]):
        row_cfg = row_cfgs.get(i, RowConfig())
        before_mask[i] = row_cfg.hline_above
        after_mask[i] = row_cfg.hline_below
    return before_mask, after_mask


@dataclass(kw_only=True)
class DataEnv:
    cell_cfgs: dict[tuple[int, int], CellConfig] = field(default_factory=dict)
    row_cfgs: dict[int, RowConfig] = field(default_factory=dict)
    col_cfgs: dict[int, ColConfig] = field(default_factory=dict)
    data: pd.DataFrame
    _row_prefixes: pd.Series = field(init=False)
    _row_suffixes: pd.Series = field(init=False)
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
        return merged.sum(axis=1).sum()

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
