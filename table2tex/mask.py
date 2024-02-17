from itertools import product
from typing import Mapping, Optional, Protocol

import numpy as np
import numpy.typing as npt


class _HasTextBfAttr(Protocol):
    textbf: Optional[bool]


def build_textbf_mask(
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


def build_hline_mask(
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
