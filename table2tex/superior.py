from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from jinja2 import Template


class _Cfg(Protocol):
    show_info: bool
    version: str
    source_file: Path


class _Env(Protocol):
    def __str__(self) -> str:
        ...


@dataclass()
class SuperiorEnv:
    cfg: _Cfg
    pos_env: _Env
    template: Template

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
