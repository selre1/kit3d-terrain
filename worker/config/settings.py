from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/1")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/2")
    celery_queue: str = os.getenv("CELERY_QUEUE", "terrain_jobs")
    celery_prefetch: int = int(os.getenv("CELERY_PREFETCH", "1"))
    celery_broker_heartbeat: int = int(os.getenv("CELERY_BROKER_HEARTBEAT", "0"))

    ctb_timeout_sec: int = int(os.getenv("CTB_TIMEOUT_SEC", "7200"))

    assets_dir: str = os.getenv("ASSETS_DIR")
    log_root: str = os.getenv("LOG_ROOT")

    db_host: str = os.getenv("DB_HOST")
    db_name: str = os.getenv("DB_NAME")
    db_user: str = os.getenv("DB_USER")
    db_password: str = os.getenv("DB_PASSWORD")


settings = Settings()
