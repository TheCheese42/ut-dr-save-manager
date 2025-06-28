import shutil
from datetime import datetime
from pathlib import Path
from subprocess import getoutput
from threading import Thread

from .paths import BACKUP_PATH, DELTARUNE_SAVES_PATH, UNDERTALE_SAVES_PATH

from pyqt_utils.utils import open_file


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
    except (FileExistsError, FileNotFoundError):
        pass
    shutil.copytree(UNDERTALE_SAVES_PATH / name, save_path)


def copy_deltarune_save(name: str, save_path: Path | str) -> None:
    try:
        shutil.move(save_path, BACKUP_PATH / datetime.now().strftime(
            "DELTARUNE_%Y-%m-%d_%H-%M-%S") / name)
    except (FileExistsError, FileNotFoundError):
        pass
    shutil.copytree(DELTARUNE_SAVES_PATH / name, save_path)


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


def rename_undertale_save(name: str, new_name: str) -> None:
    try:
        shutil.move(
            UNDERTALE_SAVES_PATH / name, UNDERTALE_SAVES_PATH / new_name
        )
    except FileNotFoundError:
        pass
    except FileExistsError:
        pass


def rename_deltarune_save(name: str, new_name: str) -> None:
    try:
        shutil.move(
            DELTARUNE_SAVES_PATH / name, DELTARUNE_SAVES_PATH / new_name
        )
    except FileNotFoundError:
        pass
    except FileExistsError:
        pass


def open_backup_folder() -> None:
    open_file(BACKUP_PATH)


def launch_steam_ut() -> None:
    getoutput("steam steam://rungameid/391540")


def launch_steam_dr() -> None:
    getoutput("steam steam://rungameid/1671210")


def _start_file_threaded(path: str | Path) -> None:
    getoutput(str(path))


def launch_file(path: str | Path) -> None:
    thread = Thread(target=_start_file_threaded, args=(path,))
    thread.start()
