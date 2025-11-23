"""Simple JSON-based preset storage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from src import config


def _preset_dir() -> Path:
    path = Path(config.PRESET_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def preset_path(name: str) -> Path:
    safe_name = name.replace("/", "_").replace("\\", "_")
    return _preset_dir() / f"{safe_name}.json"


def list_presets() -> List[str]:
    return [p.stem for p in _preset_dir().glob("*.json")]


def save_preset(name: str, data: Dict) -> None:
    path = preset_path(name)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_preset(name: str) -> Dict:
    path = preset_path(name)
    if not path.exists():
        raise FileNotFoundError(f"Preset not found: {name}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def delete_preset(name: str) -> None:
    path = preset_path(name)
    if path.exists():
        path.unlink()
