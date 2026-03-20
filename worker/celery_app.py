from __future__ import annotations

from celery import Celery

from worker.config.settings import settings


celery_app = Celery(
    "terrain",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["worker.task.terrain_task"],
)

celery_app.conf.update(
    task_default_queue=settings.celery_queue,
    task_routes={"terrain.convert_dem": {"queue": settings.celery_queue}},
    worker_prefetch_multiplier=settings.celery_prefetch,
    broker_heartbeat=settings.celery_broker_heartbeat,
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
)
