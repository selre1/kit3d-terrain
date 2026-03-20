from __future__ import annotations

import os

from worker.config.settings import settings


def write_task_log(job_id: str, content: str) -> str:
    os.makedirs(settings.log_root, exist_ok=True)
    log_path = os.path.join(settings.log_root, f"{job_id}.log")
    with open(log_path, "w", encoding="utf-8") as file:
        file.write(content)
    return log_path
