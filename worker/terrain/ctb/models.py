from __future__ import annotations

from dataclasses import dataclass


class CtbError(RuntimeError):
    pass


@dataclass
class CtbResult:
    command: str
    stdout: str
    stderr: str
