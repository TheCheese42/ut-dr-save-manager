import platform
import shutil
import webbrowser
from datetime import datetime
from pathlib import Path
from subprocess import getoutput
from threading import Thread

try:
    from .paths import BACKUP_PATH, DELTARUNE_SAVES_PATH, UNDERTALE_SAVES_PATH
except ImportError:
    from paths import BACKUP_PATH, DELTARUNE_SAVES_PATH, UNDERTALE_SAVES_PATH


def get_undertale_saves() -> list[str]:
    return list(map(str, map(
        lambda x: x.stem,
        sorted(UNDERTALE_SAVES_PATH.iterdir(), key=lambda x: x.name)
    )))


def get_deltarune_saves() -> list[str]:
    return list(map(str, map(
        lambda x: x.stem,
        sorted(DELTARUNE_SAVES_PATH.iterdir(), key=lambda x: x.name)
    )))


def copy_undertale_save(name: str, save_path: Path | str) -> None:
    try:
        shutil.move(save_path, BACKUP_PATH / datetime.now().strftime(
            "UNDERTALE_%Y-%m-%d_%H-%M-%S") / name)
    except FileExistsError:
        pass
    shutil.copytree(UNDERTALE_SAVES_PATH / name, save_path)


def copy_deltarune_save(name: str, save_path: Path | str) -> None:
    try:
        shutil.move(save_path, BACKUP_PATH / datetime.now().strftime(
            "DELTARUNE_%Y-%m-%d_%H-%M-%S") / name)
    except FileExistsError:
        pass
    shutil.copytree(UNDERTALE_SAVES_PATH / name, save_path)


def create_undertale_save(name: str, path: Path | str) -> None:
    try:
        shutil.copytree(path, UNDERTALE_SAVES_PATH / name)
    except FileExistsError:
        pass


def create_deltarune_save(name: str, path: Path | str) -> None:
    try:
        shutil.copytree(path, DELTARUNE_SAVES_PATH / name)
    except FileExistsError:
        pass


def delete_undertale_save(name: str) -> None:
    try:
        shutil.rmtree(UNDERTALE_SAVES_PATH / name)
    except FileNotFoundError:
        pass


def delete_deltarune_save(name: str) -> None:
    try:
        shutil.rmtree(DELTARUNE_SAVES_PATH / name)
    except FileNotFoundError:
        pass


def _open_file_threaded(path: str | Path) -> None:
    try:
        # Webbrowser module can well be used to open regular file as well.
        # The system will use the default application, for the file type,
        # not necessarily the webbrowser.
        webbrowser.WindowsDefault().open(str(path))  # type: ignore[attr-defined]  # noqa
    except Exception:
        system = platform.system()
        if system == "Windows":
            getoutput(f"start {path}")
        else:
            getoutput(f"open {path}")


def open_file(path: str | Path) -> None:
    thread = Thread(target=_open_file_threaded, args=(path,))
    thread.start()


def open_backup_folder() -> None:
    open_file(BACKUP_PATH)
