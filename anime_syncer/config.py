import json
from pathlib import Path

_CONFIG_DIR = Path.home() / ".config" / "anime-syncer"
CONFIG_FILE = _CONFIG_DIR / "config.json"
SYNCED_FILE = _CONFIG_DIR / "synced.json"


def _ensure_dir():
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    return json.loads(CONFIG_FILE.read_text())


def save_config(data: dict):
    _ensure_dir()
    CONFIG_FILE.write_text(json.dumps(data, indent=2))


def load_synced() -> dict:
    if not SYNCED_FILE.exists():
        return {}
    return json.loads(SYNCED_FILE.read_text())


def save_synced(data: dict):
    _ensure_dir()
    SYNCED_FILE.write_text(json.dumps(data, indent=2))
