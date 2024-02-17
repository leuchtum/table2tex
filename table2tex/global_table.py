from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from jinja2 import Template

from table2tex.outer_table import TableEnvironment


class _CfgWithNeededAttr(Protocol):
    show_info: bool
    version: str
    source_file: Path


@dataclass()
class GlobalEnvironment:
    cfg: _CfgWithNeededAttr
    outer_table_env: TableEnvironment
    template: Template

    @property
    def source_file_mtime(self) -> str:
        as_float = self.cfg.source_file.stat().st_mtime
        as_utc = datetime.fromtimestamp(as_float, tz=timezone.utc)
        as_local = as_utc.astimezone()
        return as_local.isoformat()

    def __str__(self) -> str:
        as_float = self.cfg.source_file.stat().st_mtime
        as_utc = datetime.fromtimestamp(as_float, tz=timezone.utc)
        as_local = as_utc.astimezone()
        as_string = as_local.isoformat()

        return self.template.render(
            {
                **self.__dict__,
                "source_file": self.cfg.source_file.resolve(),
                "source_file_mtime": as_string,
            }
        )
