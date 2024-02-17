from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from table2tex import __version__


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=False)


class CellConfig(StrictModel):
    textbf: Optional[bool] = None


class ColConfig(StrictModel):
    textbf: Optional[bool] = None


class RowConfig(StrictModel):
    hline_above: Optional[bool] = None
    hline_below: Optional[bool] = None
    toprule_above: Optional[bool] = None
    toprule_below: Optional[bool] = None
    midrule_above: Optional[bool] = None
    midrule_below: Optional[bool] = None
    bottomrule_above: Optional[bool] = None
    bottomrule_below: Optional[bool] = None
    textbf: Optional[bool] = None


@dataclass()
class PositioningConfig:
    position: str
    caption: Optional[str] = None
    label: Optional[str] = None
    centering: Optional[bool] = None


@dataclass()
class TableConfig:
    columnlayout: str


class GlobalConfig(StrictModel):
    # Non user defined
    version: str = __version__
    sources: list[Path] = Field(default_factory=dict)
    # User defined
    columnlayout: str = ""
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
