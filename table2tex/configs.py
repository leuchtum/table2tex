from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, ConfigDict


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
