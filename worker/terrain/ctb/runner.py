from __future__ import annotations

import shlex
import subprocess

from worker.config.settings import settings
from worker.terrain.ctb.models import CtbError, CtbResult


def _run(command: list[str], timeout_sec: int) -> CtbResult:
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired as exc:
        raise CtbError(f"CTB timeout after {timeout_sec}s") from exc

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    command_text = shlex.join(command)

    if proc.returncode != 0:
        detail = (stderr or stdout or "").strip()
        raise CtbError(f"CTB failed (exit={proc.returncode}): {detail[:4000]}")

    return CtbResult(command=command_text, stdout=stdout, stderr=stderr)


def _build_ctb_command(input_file: str, output_dir: str) -> list[str]:
    command = (
        f'ctb-tile -f Mesh -C -N -o "{output_dir}" "{input_file}" '
        f'&& ctb-tile -f Mesh -C -N -l -o "{output_dir}" "{input_file}"'
    )
    return ["sh", "-lc", command]


def run_ctb(input_file: str, output_dir: str) -> CtbResult:
    command = _build_ctb_command(input_file, output_dir)
    return _run(command, settings.ctb_timeout_sec)
