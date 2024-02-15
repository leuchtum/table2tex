from dataclasses import field

from pydantic import BaseModel


class DataEnvironmentConfig(BaseModel):
    add_hline: bool = False
    add_toprule: bool = False
    add_bottomrule: bool = False
    add_midrule_after_rows: list[int] = field(default_factory=list)
    bf_rows: list[int] = field(default_factory=list)
    bf_cols: list[int] = field(default_factory=list)
    highlight_rows: list[int] = field(default_factory=list)
    highlight_colour: str = "gray!25"


class TableEnvironmentConfig(BaseModel):
    position: str | None = None
    caption: str | None = None
    centering: bool = True


class TabularEnvironmentConfig(BaseModel):
    collayout: str = ""
