from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

import pandas as pd
from jinja2 import Template


class _Cfg(Protocol):
    show_info: bool
    version: str
    sources: list[Path]


class _Env(Protocol):
    def __str__(self) -> str:
        ...


@dataclass()
class SuperiorEnv:
    cfg: _Cfg
    pos_env: _Env
    template: Template

    def __str__(self) -> str:
        def path_to_string(path: Path) -> str:
            return path.resolve().as_posix()

        def path_to_mtime_string(path: Path) -> str:
            as_float = path.stat().st_mtime
            as_utc = datetime.fromtimestamp(as_float, tz=timezone.utc)
            as_local = as_utc.astimezone()
            return as_local.isoformat()

        sources = [path_to_string(path) for path in self.cfg.sources]
        mtimes = [path_to_mtime_string(path) for path in self.cfg.sources]
        source_table = pd.DataFrame(
            {
                "%": ["%" for _ in sources],
                "SOURCE": sources,
                "MODIFICATION TIME": mtimes,
            },
        ).to_string(index=False)
        return self.template.render(
            {
                **self.__dict__,
                "source_table": source_table,
            }
        )
