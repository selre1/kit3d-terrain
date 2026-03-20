from __future__ import annotations

import os
import zipfile


def zip_directory(source_dir: str, zip_path: str) -> None:
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for root, _, files in os.walk(source_dir):
            for file_name in files:
                abs_path = os.path.join(root, file_name)
                rel_path = os.path.relpath(abs_path, source_dir).replace("\\", "/")
                archive.write(abs_path, rel_path)
