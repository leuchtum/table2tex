from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def _parse_indices(indices: str) -> list[str]:
    return indices.split(" ")


IndexList = Annotated[list[int], BeforeValidator(_parse_indices)]


class Setting(BaseModel):
    model_config = ConfigDict(extra="forbid")
    add_hline: bool = False
    add_toprule: bool = False
    add_bottomrule: bool = False
    add_midrule_after_rows: IndexList = Field(default_factory=list)
    bf_rows: IndexList = Field(default_factory=list)
    bf_cols: IndexList = Field(default_factory=list)
    highlight_rows: IndexList = Field(default_factory=list)
    highlight_color: str = "CCCCCC"
    position: str | None = None
    caption: str | None = None
    centering: bool = True
    columnlayout: str = ""
