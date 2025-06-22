from pathlib import Path

from PyQt6.QtCore import QStandardPaths

if "__compiled__" in globals():
    # With nuitka, __file__ will show the file in a subfolder that doesn't
    # exist.
    # With nuitka: udsm.dist/udsm/paths.py
    # Actual: udsm.dist/paths.py
    # That's why we go back another folder using .parent twice.
    ROOT_PATH = Path(__file__).parent.parent
else:
    ROOT_PATH = Path(__file__).parent  # type: ignore[assignment]

VERSION_PATH = ROOT_PATH / "version.txt"
LICENSES_PATH = ROOT_PATH / "licenses"
LICENSE_PATH = LICENSES_PATH / "LICENSE.html"
WINDOWS_LICENSE_PATH = LICENSES_PATH / "OPEN_SOURCE_LICENSES_WINDOWS.html"
LINUX_LICENSE_PATH = LICENSES_PATH / "OPEN_SOURCE_LICENSES_LINUX.html"

CONFIG_DIR = Path(
    QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppDataLocation
    )
) / "ut-dr-save-manager"

CONFIG_PATH = CONFIG_DIR / "config.json"
LOGGER_PATH = CONFIG_DIR / "latest.log"
UNDERTALE_SAVES_PATH = CONFIG_DIR / "undertale_saves"
DELTARUNE_SAVES_PATH = CONFIG_DIR / "deltarune_saves"
BACKUP_PATH = CONFIG_DIR / "backups"
