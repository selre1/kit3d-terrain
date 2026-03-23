from __future__ import annotations

import os
from dataclasses import dataclass

from worker.config.settings import settings


@dataclass(frozen=True)
class TerrainPathSet:
    assets_root: str
    terrain_dir: str
    terrain_zip: str


def build_terrain_paths(job_id: str) -> TerrainPathSet:
    assets_root = settings.assets_dir
    terrain_dir = os.path.join(assets_root, "dem", "terrain", job_id)
    terrain_zip = os.path.join(assets_root, "dem", "zip", f"{job_id}.zip")
    return TerrainPathSet(
        assets_root=assets_root,
        terrain_dir=terrain_dir,
        terrain_zip=terrain_zip,
    )


def to_relative_path(path: str, base_dir: str) -> str:
    return os.path.relpath(path, base_dir).replace("\\", "/")


def to_asset_url(relative_path: str) -> str:
    return f"/assets/{relative_path.lstrip('/')}"
