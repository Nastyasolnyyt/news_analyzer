from pathlib import Path
from typing import Optional


def find_project_root_by_src(current_path: Optional[Path] = None) -> Path:
    if current_path is None:
        current_path = Path(__file__).resolve()

    for parent in [current_path] + list(current_path.parents):
        if (parent / "src").exists() and (parent / "src").is_dir():
            return parent

    return current_path.parents[-1]
