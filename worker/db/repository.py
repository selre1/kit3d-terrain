from __future__ import annotations

from worker.db.connection import get_connection


def _ensure_updated(rowcount: int, job_id: str, action: str) -> None:
    if rowcount == 0:
        raise RuntimeError(f"terrain_job not found for {action}: {job_id}")


def terrain_task_running(job_id: str, dem_id: str, task_id: str | None = None) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE terrain_job
                SET status = 'RUNNING',
                    task_id = %s,
                    err = NULL,
                    started_at = NOW(),
                    ended_at = NULL
                WHERE job_id = %s
                  AND dem_id = %s
                """,
                (task_id, job_id, dem_id),
            )
            _ensure_updated(cur.rowcount, job_id, "RUNNING")


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
            _ensure_updated(cur.rowcount, job_id, "ZIPPING")


def terrain_task_done(job_id: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE terrain_job
                SET status = 'DONE',
                    err = NULL,
                    ended_at = NOW()
                WHERE job_id = %s
                """,
                (job_id,),
            )
            _ensure_updated(cur.rowcount, job_id, "DONE")


def terrain_task_failed(job_id: str, err: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE terrain_job
                SET status = 'FAILED',
                    err = %s,
                    ended_at = NOW()
                WHERE job_id = %s
                """,
                (err[:4000], job_id),
            )
            _ensure_updated(cur.rowcount, job_id, "FAILED")


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
