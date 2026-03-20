# kit3d-terrain

Terrain worker for KIT3D.

## Structure
- `worker/config`: settings and logger config
- `worker/db`: DB connection and repositories
- `worker/terrain`: CTB execution logic
- `worker/task`: Celery task orchestration
- `worker/utils`: shared utility functions

## Task
- Name: `terrain.convert_dem`
- Queue: `terrain_jobs`
- Payload: `job_id`, `dem_id`, `file_path`

## Path rule
- `ASSETS_DIR=/data/assets`
- Terrain output: `/data/assets/dem/terrain/{job_id}`
- Terrain zip: `/data/assets/dem/terrain/{job_id}.zip`
- Logs: `{LOG_ROOT}/{job_id}.log`

## Run
```bash
docker compose up -d --build kit3d-terrain
```
