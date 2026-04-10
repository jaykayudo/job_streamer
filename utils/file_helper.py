from __future__ import annotations

import json
import os
from typing import Any

from conf.settings import SETTINGS


def save_json_to_files_dir(filename: str, data: Any) -> str:
    """
    Serialise *data* to JSON and write it to SETTINGS.FILES_DIR/<filename>.

    Args:
        filename: File name (no directory prefix, e.g. "job_123_application.json").
        data: Any JSON-serialisable object.

    Returns:
        The absolute path of the written file.
    """
    os.makedirs(SETTINGS.FILES_DIR, exist_ok=True)
    file_path = os.path.join(SETTINGS.FILES_DIR, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    return file_path