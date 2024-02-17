from itertools import product
from typing import Callable, Mapping, Protocol

import numpy as np
import numpy.typing as npt


def _2d_mask(N: int, M: int, cond: Callable[[int, int], int]) -> npt.NDArray[np.int_]:
    mask = -np.ones(shape=(N, M), dtype=int)
    for i, j in product(range(-N, N), range(-M, M)):
        mask[i, j] = max(cond(i, j), mask[i, j])
    return mask


def _1d_mask(K: int, cond: Callable[[int], int]) -> npt.NDArray[np.int_]:
    mask = -np.ones(K, dtype=int)
    for k in range(-K, K):
        mask[k] = max(cond(k), mask[k])
    return mask


class _HasTextBfAttr(Protocol):
    textbf: int


def build_textbf_mask(
    shape: tuple[int, int],
    cell_cfgs: Mapping[tuple[int, int], _HasTextBfAttr],
    row_cfgs: Mapping[int, _HasTextBfAttr],
    col_cfgs: Mapping[int, _HasTextBfAttr],
) -> npt.NDArray[np.bool_]:
    def cell_cond(i: int, j: int) -> int:
        cfg = cell_cfgs.get((i, j))
        if cfg is None:
            return -1
        return cfg.textbf

    def col_cond(j: int) -> int:
        cfg = col_cfgs.get(j)
        if cfg is None:
            return -1
        return cfg.textbf

    def row_cond(i: int) -> int:
        cfg = row_cfgs.get(i)
        if cfg is None:
            return -1
        return cfg.textbf

    N, M = shape
    row_mask = _1d_mask(N, row_cond)
    row_mask = np.vstack([row_mask] * M).T
    col_mask = _1d_mask(M, col_cond)
    col_mask = np.vstack([col_mask] * N)
    cell_mask = _2d_mask(N, M, cell_cond)

    mask = -np.ones(shape=shape, dtype=int)
    mask[row_mask >= 0] = row_mask[row_mask >= 0]
    mask[col_mask >= 0] = col_mask[col_mask >= 0]
    mask[cell_mask >= 0] = cell_mask[cell_mask >= 0]
    return mask


class _HasHLineAttr(Protocol):
    hline_above: int
    hline_below: int


def build_hline_mask(
    shape: tuple[int, int],
    cfgs: Mapping[int, _HasHLineAttr],
) -> tuple[npt.NDArray[np.int_], npt.NDArray[np.int_]]:
    def before_cond(i: int) -> int:
        cfg = cfgs.get(i)
        if cfg is None:
            return -1
        return cfg.hline_above

    def after_cond(i: int) -> int:
        cfg = cfgs.get(i)
        if cfg is None:
            return -1
        return cfg.hline_below

    N = shape[0]
    before_mask = _1d_mask(N, before_cond)
    after_mask = _1d_mask(N, after_cond)
    return before_mask, after_mask
