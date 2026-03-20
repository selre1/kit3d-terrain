from __future__ import annotations

from datetime import datetime

from worker.db.connection import get_connection


def terrain_task_running(job_id: str, dem_id: str, started_at: datetime, task_id: str | None = None) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO terrain_job (job_id, dem_id, status, task_id, err, started_at, ended_at)
                VALUES (%s, %s, 'RUNNING', %s, NULL, %s, NULL)
                ON CONFLICT (job_id) DO UPDATE
                SET dem_id = EXCLUDED.dem_id,
                    status = 'RUNNING',
                    task_id = EXCLUDED.task_id,
                    err = NULL,
                    started_at = EXCLUDED.started_at,
                    ended_at = NULL
                """,
                (job_id, dem_id, task_id, started_at),
            )


def terrain_task_zipping(job_id: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE terrain_job
                SET status = 'ZIPPING'
                WHERE job_id = %s
                """,
                (job_id,),
            )


def terrain_task_done(job_id: str, ended_at: datetime) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE terrain_job
                SET status = 'DONE',
                    err = NULL,
                    ended_at = %s
                WHERE job_id = %s
                """,
                (ended_at, job_id),
            )


def terrain_task_failed(job_id: str, err: str, ended_at: datetime) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE terrain_job
                SET status = 'FAILED',
                    err = %s,
                    ended_at = %s
                WHERE job_id = %s
                """,
                (err[:4000], ended_at, job_id),
            )


def terrain_result_upsert(
    job_id: str,
    terrain_dir_path: str,
    terrain_zip_path: str,
    terrain_uri: str,
    zip_uri: str,
) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO terrain_result (
                    job_id,
                    terrain_dir_path,
                    terrain_zip_path,
                    terrain_uri,
                    zip_uri
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (job_id) DO UPDATE
                SET terrain_dir_path = EXCLUDED.terrain_dir_path,
                    terrain_zip_path = EXCLUDED.terrain_zip_path,
                    terrain_uri = EXCLUDED.terrain_uri,
                    zip_uri = EXCLUDED.zip_uri
                """,
                (job_id, terrain_dir_path, terrain_zip_path, terrain_uri, zip_uri),
            )
