import json
from datetime import datetime
from pathlib import Path
from platform import system
from typing import Any

try:
    from .paths import (BACKUP_PATH, CONFIG_DIR, CONFIG_PATH,
                        DELTARUNE_SAVES_PATH, LOGGER_PATH,
                        UNDERTALE_SAVES_PATH)
except ImportError:
    from paths import (BACKUP_PATH, CONFIG_DIR, CONFIG_PATH,
                       DELTARUNE_SAVES_PATH, LOGGER_PATH, UNDERTALE_SAVES_PATH)


def get_default_undertale_save_path() -> str:
    match system():
        case "Linux":
            return str(Path.home() / ".config" / "UNDERTALE")
        case "Windows":
            return str(Path.home() / "AppData" / "Local" / "UNDERTALE")
        case "Darwin":
            return str(
                Path.home() / "Library" / "Application Support" /
                "com.tobyfox.undertale"
            )
        case _:
            return ""


def get_default_deltarune_save_path() -> str:
    match system():
        case "Linux":
            return ""
        case "Windows":
            return str(Path.home() / "AppData" / "Local" / "DELTARUNE")
        case "Darwin":
            return str(
                Path.home() / "Library" / "Application Support" /
                "com.tobyfox.deltarune"
            )
        case _:
            return ""


DEFAULT_CONFIG: dict[str, str | int | float | bool | list[str]] = {
    "undertale_file_path": "",
    "deltarune_file_path": "",
    "undertale_save_path": get_default_undertale_save_path(),
    "deltarune_save_path": get_default_deltarune_save_path(),
    "deltarune_saves": [],
    "undertale_saves": [],
}


def config_exists() -> bool:
    return CONFIG_PATH.exists()


def create_app_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def trunc_log() -> None:
    with open(LOGGER_PATH, "w") as fp:
        fp.write("")


def init_config() -> None:
    create_app_dir()
    trunc_log()
    UNDERTALE_SAVES_PATH.mkdir(parents=True, exist_ok=True)
    DELTARUNE_SAVES_PATH.mkdir(parents=True, exist_ok=True)
    BACKUP_PATH.mkdir(parents=True, exist_ok=True)

    if not config_exists():
        with open(CONFIG_PATH, "w", encoding="utf-8") as fp:
            json.dump(DEFAULT_CONFIG, fp)


def _get_config() -> dict[str, Any]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as fp:
        text = fp.read()
    try:
        conf: dict[str, Any] = json.loads(text)
    except json.JSONDecodeError as e:
        log(f"Failed to decode configuration file: {e}", "ERROR")
        log("Creating new config")
        conf = DEFAULT_CONFIG
    for key in conf.copy():
        if key not in DEFAULT_CONFIG:
            del conf[key]
    for key in DEFAULT_CONFIG:
        if key not in conf:
            conf[key] = DEFAULT_CONFIG[key]
    return conf


def _overwrite_config(config: dict[str, Any]) -> None:
    try:
        text = json.dumps(config)
    except Exception as e:
        log(f"Failed to dump configuration: {e}", "ERROR")
        return
    with open(CONFIG_PATH, "w", encoding="utf-8") as fp:
        fp.write(text)


def get_config_value(key: str) -> Any:
    try:
        val = _get_config()[key]
    except KeyError:
        val = DEFAULT_CONFIG[key]
    return val


def set_config_value(
    key: str, value: str | int | float | bool | list[str]
) -> None:
    config = _get_config()
    config[key] = value
    _overwrite_config(config)


def log(msg: str, level: str = "INFO") -> None:
    time = datetime.now().isoformat()
    with open(LOGGER_PATH, "a", encoding="utf-8") as fp:
        fp.write(f"[{time}] [{level}] {msg}\n")
