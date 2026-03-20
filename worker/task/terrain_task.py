from __future__ import annotations

import os
import traceback
from dataclasses import dataclass
from typing import Any

from worker.celery_app import celery_app
from worker.config.logging import get_logger
from worker.config.settings import settings
from worker.db import (
    terrain_result_upsert,
    terrain_task_done,
    terrain_task_failed,
    terrain_task_running,
    terrain_task_zipping,
)
from worker.terrain.ctb.models import CtbError, CtbResult
from worker.terrain.ctb.runner import run_ctb
from worker.utils.archive import zip_directory
from worker.utils.logs import write_task_log
from worker.utils.paths import build_terrain_paths, to_asset_url, to_relative_path
from worker.utils.time import now_kst, now_kst_text

logger = get_logger("kit3d-terrain")


@dataclass(frozen=True)
class TerrainConvertPayload:
    job_id: str
    dem_id: str
    file_path: str


def _parse_payload(payload: dict[str, Any] | None) -> TerrainConvertPayload:
    body = payload or {}
    job_id = body.get("job_id")
    dem_id = body.get("dem_id")
    file_path = body.get("file_path")

    if not job_id:
        raise ValueError("job_id is required")
    if not dem_id:
        raise ValueError("dem_id is required")
    if not file_path:
        raise ValueError("file_path is required")
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"input file not found: {file_path}")

    return TerrainConvertPayload(
        job_id=str(job_id),
        dem_id=str(dem_id),
        file_path=str(file_path),
    )


def _build_log_text(result: CtbResult) -> str:
    parts: list[str] = ["[COMMAND]", result.command]
    if result.stdout:
        parts.extend(["", "[STDOUT]", result.stdout])
    if result.stderr:
        parts.extend(["", "[STDERR]", result.stderr])
    return "\n".join(parts) + "\n"


def _mark_failed(job_id: str, err: str) -> None:
    try:
        terrain_task_failed(job_id, err, now_kst())
    except Exception:
        logger.exception("Failed to update terrain_job status FAILED job_id=%s", job_id)


@celery_app.task(name="terrain.health")
def health() -> dict:
    return {
        "status": "ok",
        "queue": settings.celery_queue,
        "time": now_kst_text(),
    }


@celery_app.task(name="terrain.convert_dem", bind=True, queue=settings.celery_queue, acks_late=True)
def convert_dem(self, payload) -> dict:
    req = _parse_payload(payload)
    celery_task_id = getattr(getattr(self, "request", None), "id", None)
    paths = build_terrain_paths(req.job_id)

    os.makedirs(paths.terrain_dir, exist_ok=True)

    try:
        terrain_task_running(req.job_id, req.dem_id, now_kst(), celery_task_id)

        ctb_result = run_ctb(req.file_path, paths.terrain_dir)
        log_path = write_task_log(req.job_id, _build_log_text(ctb_result))

        terrain_task_zipping(req.job_id)
        zip_directory(paths.terrain_dir, paths.terrain_zip)

        terrain_dir_path = to_relative_path(paths.terrain_dir, paths.assets_root)
        terrain_zip_path = to_relative_path(paths.terrain_zip, paths.assets_root)
        terrain_uri = to_asset_url(terrain_dir_path)
        zip_uri = to_asset_url(terrain_zip_path)

        terrain_result_upsert(
            req.job_id,
            terrain_dir_path,
            terrain_zip_path,
            terrain_uri,
            zip_uri,
        )
        terrain_task_done(req.job_id, now_kst())

        return {
            "job_id": req.job_id,
            "dem_id": req.dem_id,
            "status": "DONE",
            "terrain_dir_path": terrain_dir_path,
            "terrain_zip_path": terrain_zip_path,
            "terrain_uri": terrain_uri,
            "zip_uri": zip_uri,
            "log_path": log_path,
            "finished_at": now_kst_text(),
        }
    except CtbError as exc:
        logger.exception("Terrain conversion failed job_id=%s", req.job_id)
        log_path = write_task_log(req.job_id, f"[ERROR]\n{exc}\n")
        _mark_failed(req.job_id, str(exc))
        return {
            "job_id": req.job_id,
            "dem_id": req.dem_id,
            "status": "FAILED",
            "error": str(exc),
            "log_path": log_path,
            "finished_at": now_kst_text(),
        }
    except Exception as exc:
        logger.exception("Unexpected terrain failure job_id=%s", req.job_id)
        detail = f"{exc}\n\n{traceback.format_exc()}"
        log_path = write_task_log(req.job_id, f"[ERROR]\n{detail}\n")
        _mark_failed(req.job_id, str(exc))
        return {
            "job_id": req.job_id,
            "dem_id": req.dem_id,
            "status": "FAILED",
            "error": str(exc),
            "log_path": log_path,
            "finished_at": now_kst_text(),
        }
