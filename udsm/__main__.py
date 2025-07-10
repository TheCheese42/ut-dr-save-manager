import sys
from functools import partial
from pathlib import Path
from platform import system
from typing import Any, Literal

import pyqt_utils

if True:  # Makes flake8 shut up
    pyqt_utils.init_app("ut-dr-save-manager", __file__)

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QDragEnterEvent, QDropEvent, QIcon, QKeyEvent
from PyQt6.QtWidgets import (QApplication, QDialog, QFileDialog,
                             QListWidgetItem, QMainWindow, QMenu, QMessageBox,
                             QWidget)
from pyqt_utils import licenses
from pyqt_utils.config import (get_config_value, init_config, log,
                               set_config_value)
from pyqt_utils.styles import find_styles
from pyqt_utils.utils import open_url
from pyqt_utils.version import version_string

from . import model
from .paths import (BACKUP_PATH, DELTARUNE_SAVES_PATH, ICONS_PATH,
                    PREMADE_PATH, UNDERTALE_SAVES_PATH)

try:
    from .ui.about_ui import Ui_About
    from .ui.create_ui import Ui_Create
    from .ui.playlist_runner_ui import Ui_PlaylistRunner
    from .ui.playlists_ui import Ui_Playlists
    from .ui.window_ui import Ui_MainWindow
except ImportError:
    log(
        "Failed to load UI. Did you forget to run the compile-ui script?",
        "ERROR",
    )
    sys.exit(1)

try:
    from .styles.Breeze import breeze_pyqt6 as _  # noqa
except ImportError:
    log(
        "Failed to load breeze styles. Did you forget to run the "
        "compile-styles script?"
        "WARNING",
    )

type Game = Literal["undertale", "deltarune"]


def get_default_undertale_save_path() -> str:
    match system():
        case "Linux":
            return str((
                Path.home() / ".config" / "UNDERTALE"
            ).absolute().resolve())
        case "Windows":
            return str((
                Path.home() / "AppData" / "Local" / "UNDERTALE"
            ).absolute().resolve())
        case "Darwin":
            return str(
                (
                    Path.home() / "Library" / "Application Support" /
                    "com.tobyfox.undertale"
                ).absolute().resolve()
            )
        case _:
            return ""


def get_default_deltarune_save_path() -> str:
    match system():
        case "Linux":
            return ""
        case "Windows":
            return str((
                Path.home() / "AppData" / "Local" / "DELTARUNE"
            ).absolute().resolve())
        case "Darwin":
            return str(
                (
                    Path.home() / "Library" / "Application Support" /
                    "com.tobyfox.deltarune"
                ).absolute().resolve()
            )
        case _:
            return ""


def get_default_undertale_proc_name() -> str:
    match system():
        case "Linux":
            return "runner"
        case "Windows":
            return "UNDERTALE.exe"
        case _:
            return ""


def get_default_deltarune_proc_name() -> str:
    match system():
        case "Linux":
            return "DELTARUNE.exe"
        case "Windows":
            return "DELTARUNE.exe"
        case _:
            return ""


DEFAULT_CONFIG: dict[str, bool | str | list[str] | dict[str, list[str]]] = {
    "first_startup": True,
    "theme": "",
    "undertale_file_path": "",
    "deltarune_file_path": "",
    "undertale_save_path": get_default_undertale_save_path(),
    "deltarune_save_path": get_default_deltarune_save_path(),
    "deltarune_saves": [],
    "undertale_saves": [],
    "playlists": {},
    "undertale_proc_name": get_default_undertale_proc_name(),
    "deltarune_proc_name": get_default_deltarune_proc_name(),
}


def show_question(parent: QWidget, title: str, desc: str) -> int:
    messagebox = QMessageBox(parent)
    messagebox.setIcon(QMessageBox.Icon.Question)
    messagebox.setWindowTitle(title)
    messagebox.setText(desc)
    messagebox.setStandardButtons(
        QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes
    )
    messagebox.setDefaultButton(QMessageBox.StandardButton.Yes)
    return messagebox.exec()


def show_error(parent: QWidget, title: str, desc: str) -> int:
    messagebox = QMessageBox(parent)
    messagebox.setIcon(QMessageBox.Icon.Critical)
    messagebox.setWindowTitle(title)
    messagebox.setText(desc)
    messagebox.setStandardButtons(QMessageBox.StandardButton.Ok)
    messagebox.setDefaultButton(QMessageBox.StandardButton.Ok)
    return messagebox.exec()


def show_info(parent: QWidget, title: str, desc: str) -> int:
    messagebox = QMessageBox(parent)
    messagebox.setIcon(QMessageBox.Icon.Information)
    messagebox.setWindowTitle(title)
    messagebox.setText(desc)
    messagebox.setStandardButtons(QMessageBox.StandardButton.Ok)
    messagebox.setDefaultButton(QMessageBox.StandardButton.Ok)
    return messagebox.exec()


class MainWindow(QMainWindow, Ui_MainWindow):  # type: ignore[misc]
    def __init__(self) -> None:
        super().__init__(None)
        self.saves_to_items_ut: dict[str, QListWidgetItem] = {}
        self.saves_to_items_dr: dict[str, QListWidgetItem] = {}
        self.setupUi(self)
        self.updateUi()
        self.connectSignalsSlots()
        self.resize(0, 0)
        QTimer.singleShot(
            0, lambda: self.resize(self.width(), self.height() + 50)
        )
        if get_config_value("first_startup"):
            set_config_value("first_startup", False)
            self.import_all_premade_saves()

    def updateUi(self) -> None:
        self.setWindowIcon(QIcon(str(ICONS_PATH / "icon.png")))
        self.undertaleSavePath.setText(get_config_value("undertale_save_path"))
        self.deltaruneSavePath.setText(get_config_value("deltarune_save_path"))
        self.undertaleFilePath.setText(get_config_value("undertale_file_path"))
        self.deltaruneFilePath.setText(get_config_value("deltarune_file_path"))
        self.undertaleSavesList.clear()
        self.saves_to_items_ut.clear()
        self.saves_to_items_dr.clear()
        self.deltaruneSavesList.clear()
        for save in model.get_undertale_saves():
            item = QListWidgetItem(save)
            self.saves_to_items_ut[save] = item
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.undertaleSavesList.addItem(item)
        for save in model.get_deltarune_saves():
            item = QListWidgetItem(save)
            self.saves_to_items_dr[save] = item
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.deltaruneSavesList.addItem(item)
        self.menuImportPremadeSave.clear()
        ia: QAction = self.menuImportPremadeSave.addAction("Import all")  # type: ignore[assignment]  # noqa
        ia.triggered.connect(partial(self.import_all_premade_saves, None))
        for game in PREMADE_PATH.iterdir():
            game_menu: QMenu = self.menuImportPremadeSave.addMenu(game.name)  # type: ignore[assignment]  # noqa
            ia: QAction = game_menu.addAction("Import all")  # type: ignore[assignment]  # noqa
            ia.triggered.connect(
                partial(self.import_all_premade_saves, game.name)
            )
            for category in game.iterdir():
                if not category.is_dir():
                    continue
                cat_menu: QMenu = game_menu.addMenu(category.name)  # type: ignore[assignment]  # noqa
                ia: QAction = cat_menu.addAction("Import all")  # type: ignore[assignment]  # noqa
                ia.triggered.connect(
                    partial(self.import_all_premade_saves, category.name)
                )
                for save in category.iterdir():
                    if not save.is_dir():
                        continue
                    action: QAction = cat_menu.addAction(save.name)  # type: ignore[assignment]  # noqa
                    action.triggered.connect(
                        partial(
                            self.create_save,
                            save,
                            (
                                "undertale" if game.name.lower() == "undertale"
                                else "deltarune"
                            ),
                            save.name,
                        )
                    )

        # Themes
        self.menuTheme.clear()
        self.all_theme_actions: list[QAction] = []
        action: QAction = self.menuTheme.addAction("Default")  # type: ignore[assignment]  # noqa
        self.all_theme_actions.append(action)
        action.setCheckable(True)
        action.triggered.connect(partial(self.set_style, "", ""))
        configured_theme = get_config_value("theme")
        if not configured_theme:
            self.set_style("", "")
        for group, styles in find_styles().items():
            menu: QMenu = self.menuTheme.addMenu(group)  # type: ignore[assignment]  # noqa
            for style in styles:
                action: QAction = menu.addAction(style.name)  # type: ignore[assignment]  # noqa
                self.all_theme_actions.append(action)
                action.setCheckable(True)
                action.triggered.connect(
                    partial(self.set_style, style.name, style.stylesheet)
                )
                if style.name == configured_theme:
                    self.set_style(style.name, style.stylesheet)

    def import_all_premade_saves(self, from_dir: str | None = None) -> None:
        for game in PREMADE_PATH.iterdir():
            if not game.is_dir():
                continue
            for category in game.iterdir():
                if not category.is_dir():
                    continue
                for save in category.iterdir():
                    if not save.is_dir():
                        continue
                    if (
                        from_dir is None
                        or from_dir == game.name
                        or from_dir == category.name
                    ):
                        self.create_save(
                            save,
                            (
                                "undertale" if game.name.lower() == "undertale"
                                else "deltarune"
                            ),
                            save.name,
                        )

    def set_style(self, name: str, stylesheet: str) -> None:
        self.setStyleSheet(stylesheet)
        set_config_value("theme", name)
        for action in self.all_theme_actions:
            if action.text() == name:
                action.setChecked(True)
            else:
                action.setChecked(False)
        if not name:
            self.all_theme_actions[0].setChecked(True)

    def connectSignalsSlots(self) -> None:
        self.undertaleSavePath.textChanged.connect(
            lambda: set_config_value(
                "undertale_save_path", self.undertaleSavePath.text()
            )
        )
        self.deltaruneSavePath.textChanged.connect(
            lambda: set_config_value(
                "deltarune_save_path", self.deltaruneSavePath.text()
            )
        )
        self.undertaleFilePath.textChanged.connect(
            lambda: set_config_value(
                "undertale_file_path", self.undertaleFilePath.text()
            )
        )
        self.deltaruneFilePath.textChanged.connect(
            lambda: set_config_value(
                "deltarune_file_path", self.deltaruneFilePath.text()
            )
        )
        self.openBackup.clicked.connect(model.open_backup_folder)
        self.applyUndertale.clicked.connect(self.apply_undertale)
        self.applyDeltarune.clicked.connect(self.apply_deltarune)
        self.deleteUndertale.clicked.connect(self.delete_undertale)
        self.deleteDeltarune.clicked.connect(self.delete_deltarune)
        self.addUndertaleToSaves.clicked.connect(
            partial(self.add_to_saves, "undertale")
        )
        self.addDeltaruneToSaves.clicked.connect(
            partial(self.add_to_saves, "deltarune")
        )
        self.undertaleSavesList.itemChanged.connect(
            partial(self.item_renamed, "undertale")
        )
        self.undertaleSavesList.selectionChanged = (
            lambda selected, deselected:
            self.deltaruneSavesList.clearSelection()
            if self.undertaleSavesList.selectedItems() else None
        )
        self.deltaruneSavesList.itemChanged.connect(
            partial(self.item_renamed, "deltarune")
        )
        self.deltaruneSavesList.selectionChanged = (
            lambda selected, deselected:
            self.undertaleSavesList.clearSelection()
            if self.deltaruneSavesList.selectedItems() else None
        )
        self.launchUTSteam.clicked.connect(model.launch_steam_ut)
        self.launchDRSteam.clicked.connect(model.launch_steam_dr)
        self.launchUTFile.clicked.connect(
            partial(self.launch_file, "undertale")
        )
        self.launchDRFile.clicked.connect(
            partial(self.launch_file, "deltarune")
        )
        self.actionTimeMachine.triggered.connect(
            lambda: open_url(
                "https://crumblingstatue.github.io/FloweysTimeMachine/"
            )
        )
        self.actionSpamtonEditor.triggered.connect(
            lambda: open_url("https://saveeditor.spamton.com/")
        )
        self.actionOpen_Playlists.triggered.connect(self.open_playlists)
        self.actionView_Licenses.triggered.connect(self.open_licenses)
        self.actionAbout.triggered.connect(self.open_about)
        self.actionImportUTSave.triggered.connect(
            partial(self.import_save, "undertale")
        )
        self.actionImportDRSave.triggered.connect(
            partial(self.import_save, "deltarune")
        )

    def import_save(self, game: Game) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select SAVE Folder")
        if folder:
            self.create_save(folder, game)

    def open_playlists(self) -> None:
        dialog = PlaylistsDialog(self, get_config_value("playlists"))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            set_config_value("playlists", dialog.playlists_d)

    def open_about(self) -> None:
        dialog = About(self)
        dialog.exec()

    def open_licenses(self) -> None:
        dialog = licenses.LicenseViewer(self)
        dialog.licenses.append(licenses.License(
            "???", "Glory to the dog.", "https://toby.fangamer.com/"
        ))
        dialog.setup_licenses()
        dialog.exec()

    def launch_file(self, game: Game) -> None:
        path = get_config_value(f"{game}_file_path")
        game_display = game if game != "undertale" else game.upper()
        if not path:
            show_error(
                self, f"No {game_display} file path set",
                f"Please configure the {game_display} file path first."
            )
            return
        model.launch_file(path)

    def item_renamed(self, game: Game, item: QListWidgetItem) -> None:
        if game == "undertale":
            prev_name = reverse_lookup(self.saves_to_items_ut, item)
        else:
            prev_name = reverse_lookup(self.saves_to_items_dr, item)
        if prev_name is None:
            return
        new_name = item.text().strip()
        if not new_name or new_name.lower() in (
            *map(str.lower, model.get_undertale_saves()),
            *map(str.lower, model.get_deltarune_saves()),
        ):
            item.setText(prev_name)
        else:
            item.setText(new_name)
            if game == "undertale":
                model.rename_undertale_save(prev_name, new_name)
            else:
                model.rename_deltarune_save(prev_name, new_name)
        self.updateUi()

    def add_to_saves(self, game: Game) -> None:
        path = get_config_value(f"{game}_save_path")
        game_display = game if game != "undertale" else game.upper()
        if not path:
            show_error(
                self,
                f"No {game_display} save path set",
                f"Please configure the {game_display} save path first.",
            )
            return
        self.create_save(path, game)

    def dragEnterEvent(self, a0: QDragEnterEvent | None) -> None:
        if a0 is None:
            return
        if (mimeData := a0.mimeData()) is None:
            a0.ignore()
            return
        if mimeData.hasUrls():
            a0.accept()
        else:
            a0.ignore()

    def dropEvent(self, a0: QDropEvent | None) -> None:
        if a0 is None:
            return
        if (mimeData := a0.mimeData()) is None:
            return
        lines: list[str] = []
        for url in mimeData.urls():
            lines.append(url.toLocalFile())
        if len(lines) != 1:
            show_error(self, "Error", "Please drop only one folder at a time.")
            return
        self.create_save(lines[0])

    def create_save(
        self, path: str | Path,
        game: Game | None = None,
        name: str | None = None,
    ) -> None:
        create = CreateDialog(self, game)
        if game and name:
            if game == "undertale":
                model.create_undertale_save(name, path)
            else:
                model.create_deltarune_save(name, path)
            self.updateUi()
        elif create.exec() == QDialog.DialogCode.Accepted:
            name = create.nameEdit.text()
            if create.undertaleRadio.isChecked():
                model.create_undertale_save(name, path)
            else:
                model.create_deltarune_save(name, path)
            self.updateUi()

    def apply_undertale(self) -> None:
        try:
            selected = self.undertaleSavesList.selectedItems()[0].text()
        except IndexError:
            return
        undertale_save_path = Path(
            cv := get_config_value("undertale_save_path")
        )
        if not cv:
            show_error(
                self, "No UNDERTALE SAVE path set",
                "Please configure the UNDERTALE SAVE path first."
            )
            return
        if not undertale_save_path.name.lower().endswith("undertale"):
            show_error(
                self, "You IDIOT!",
                "Your UNDERTALE SAVE path does not end with 'undertale'. Are "
                "you sure picked the right path?",
            )
            return
        model.copy_undertale_save(selected, undertale_save_path)
        show_info(
            self, "SAVE Applied",
            f"Your UNDERTALE SAVE '{selected}' was applied.\n\n"
            "This overwrote your previous SAVE file. If this was an accident, "
            "you can recover your SAVE by clicking on 'Open Backup Folder'.",
        )

    def apply_deltarune(self) -> None:
        try:
            selected = self.deltaruneSavesList.selectedItems()[0].text()
        except IndexError:
            return
        deltarune_save_path = Path(
            cv := get_config_value("deltarune_save_path")
        )
        if not cv:
            show_error(
                self, "No deltarune SAVE path set",
                "Please configure the deltarune SAVE path first."
            )
            return
        if not deltarune_save_path.name.lower().endswith("deltarune"):
            show_error(
                self, "You IDIOT!",
                "Your deltarune SAVE path does not end with 'deltarune'. Are "
                "you sure picked the right path?",
            )
            return
        model.copy_deltarune_save(selected, deltarune_save_path)
        show_info(
            self, "SAVE Applied",
            f"Your deltarune SAVE '{selected}' was applied.\n\n"
            "This overwrote your previous SAVE file. If this was an accident, "
            "you can recover your SAVE by clicking on 'Open Backup Folder'.",
        )

    def delete_undertale(self) -> None:
        # Nooooooooo
        try:
            selected = self.undertaleSavesList.selectedItems()[0].text()
        except IndexError:
            return
        if show_question(
            self, "TRULY ERASE IT?",
            f"Do you really want to delete the UNDERTALE SAVE '{selected}'?",
        ) == QMessageBox.StandardButton.Yes:
            model.delete_undertale_save(selected)
            self.updateUi()

    def delete_deltarune(self) -> None:
        # Nooooooooo
        try:
            selected = self.deltaruneSavesList.selectedItems()[0].text()
        except IndexError:
            return
        if show_question(
            self, "TRULY ERASE IT?",
            f"Do you really want to delete the deltarune SAVE '{selected}'?",
        ) == QMessageBox.StandardButton.Yes:
            model.delete_deltarune_save(selected)
            self.updateUi()


class PlaylistsDialog(QDialog, Ui_Playlists):  # type: ignore[misc]
    def __init__(
        self,
        parent: QWidget | None = None,
        playlists: dict[str, list[str]] = {},
    ) -> None:
        super().__init__(parent)
        self.playlists_d = playlists
        self.playlists_to_items: dict[str, QListWidgetItem] = {}
        self.selected_playlist: str | None = None
        self.setupUi(self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.updateUi()
        self.connectSignalsSlots()

    def updateUi(self) -> None:
        self.setWindowIcon(QIcon(str(ICONS_PATH / "icon.png")))
        self.utProcName.setText(get_config_value("undertale_proc_name"))
        self.drProcName.setText(get_config_value("deltarune_proc_name"))
        list_items = [
            self.playlists.item(i).text()  # type: ignore[union-attr]
            for i in range(self.playlists.count())
        ]
        if list(self.playlists_d.keys()) != list_items:
            self.playlists_to_items.clear()
            self.playlists.clear()
            for playlist in self.playlists_d.keys():
                item = QListWidgetItem(playlist)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                self.playlists.addItem(item)
                self.playlists_to_items[playlist] = item
        self.undertaleCombo.blockSignals(True)
        self.deltaruneCombo.blockSignals(True)
        self.undertaleCombo.clear()
        self.deltaruneCombo.clear()
        for save in [""] + model.get_undertale_saves():
            self.undertaleCombo.addItem(save)
        for save in [""] + model.get_deltarune_saves():
            self.deltaruneCombo.addItem(save)
        self.undertaleCombo.setCurrentIndex(0)
        self.deltaruneCombo.setCurrentIndex(0)
        self.undertaleCombo.blockSignals(False)
        self.deltaruneCombo.blockSignals(False)
        if not self.selected_playlist:
            self.savesList.clear()
            self.savesList.setDisabled(True)
            self.undertaleCombo.setDisabled(True)
            self.deltaruneCombo.setDisabled(True)
        else:
            self.savesList.clear()
            self.savesList.setDisabled(False)
            self.undertaleCombo.setDisabled(False)
            self.deltaruneCombo.setDisabled(False)
            for save in self.playlists_d.get(self.selected_playlist, []):
                self.savesList.addItem(save)

    def connectSignalsSlots(self) -> None:
        self.playlists.itemChanged.connect(self.playlist_renamed)
        self.createPlaylist.clicked.connect(self.create_playlist)
        self.delPlaylist.clicked.connect(self.delete_playlist)
        self.playlists.itemSelectionChanged.connect(
            self.playlist_selection_changed
        )
        self.delSave.clicked.connect(self.remove_save)
        self.moveUp.clicked.connect(self.move_save_up)
        self.moveDown.clicked.connect(self.move_save_down)
        self.undertaleCombo.currentTextChanged.connect(self.add_save)
        self.deltaruneCombo.currentTextChanged.connect(self.add_save)
        self.playSteam.clicked.connect(partial(self.play_playlist, True))
        self.playFile.clicked.connect(partial(self.play_playlist, False))
        self.utProcName.textChanged.connect(
            lambda: set_config_value(
                "undertale_proc_name", self.utProcName.text()
            )
        )
        self.drProcName.textChanged.connect(
            lambda: set_config_value(
                "deltarune_proc_name", self.drProcName.text()
            )
        )

    def play_playlist(self, steam: bool) -> None:
        if not self.selected_playlist:
            return
        if not self.playlists_d.get(self.selected_playlist):
            show_error(
                self, "No SAVES in playlist",
                f"The playlist '{self.selected_playlist}' is empty."
            )
            return
        if not (ut_save_path := get_config_value("undertale_save_path")):
            show_error(
                self, "No UNDERTALE SAVE path set",
                "Please configure the UNDERTALE SAVE path first."
            )
            return
        if not (dr_save_path := get_config_value("deltarune_save_path")):
            show_error(
                self, "No deltarune SAVE path set",
                "Please configure the deltarune SAVE path first."
            )
            return
        ut_fp = ""
        dr_fp = ""
        if not steam and (
            not (ut_fp := get_config_value("undertale_file_path"))
            or not (dr_fp := get_config_value("deltarune_file_path"))
        ):
            show_error(
                self, "No UNDERTALE or deltarune file path set",
                "Please configure the UNDERTALE and deltarune file paths "
                "first."
            )
            return
        if not (ut_proc_name := get_config_value("undertale_proc_name")):
            show_error(
                self, "No UNDERTALE process name set",
                "Please configure the UNDERTALE process name first."
            )
            return
        if not (dr_proc_name := get_config_value("deltarune_proc_name")):
            show_error(
                self, "No deltarune process name set",
                "Please configure the deltarune process name first."
            )
            return
        dialog = PlaylistRunnerDialog(
            self.selected_playlist,
            self.playlists_d[self.selected_playlist].copy(),
            ut_proc_name,
            dr_proc_name,
            ut_save_path,
            dr_save_path,
            steam,
            ut_fp,
            dr_fp,
            self,
        )
        dialog.exec()

    def add_save(self, save: str) -> None:
        if not save:
            return  # Nothing selected
        if not self.selected_playlist:
            return
        self.playlists_d[self.selected_playlist].append(save)
        self.updateUi()

    def remove_save(self) -> None:
        try:
            selected = self.savesList.selectedIndexes()[0].row()
        except IndexError:
            return
        if not self.selected_playlist:
            return
        self.playlists_d[self.selected_playlist].pop(selected)
        self.updateUi()

    def move_save_up(self) -> None:
        try:
            selected = self.savesList.selectedItems()[0]
        except IndexError:
            return
        if not self.selected_playlist:
            return
        index = self.savesList.row(selected)
        if index > 0:
            self.playlists_d[self.selected_playlist].insert(
                index - 1, selected.text()
            )
            self.playlists_d[self.selected_playlist].pop(index + 1)
            self.updateUi()

    def move_save_down(self) -> None:
        try:
            selected = self.savesList.selectedItems()[0]
        except IndexError:
            return
        if not self.selected_playlist:
            return
        index = self.savesList.row(selected)
        if index < len(self.playlists_d[self.selected_playlist]) - 1:
            self.playlists_d[self.selected_playlist].insert(
                index + 2, selected.text()
            )
            self.playlists_d[self.selected_playlist].pop(index)
            self.updateUi()

    def playlist_renamed(self, item: QListWidgetItem) -> None:
        prev_name = reverse_lookup(self.playlists_to_items, item)
        if prev_name is None:
            return
        new_name = item.text().strip()
        if not new_name or new_name.lower() in (
            *map(str.lower, model.get_undertale_saves()),
            *map(str.lower, model.get_deltarune_saves()),
        ):
            item.setText(prev_name)
        else:
            item.setText(new_name)
            if prev_name in self.playlists_d:
                self.playlists_d[new_name] = self.playlists_d.pop(prev_name)
        self.updateUi()

    def create_playlist(self) -> None:
        self.playlists_d["New Playlist"] = []
        self.updateUi()

    def delete_playlist(self) -> None:
        try:
            selected = self.playlists.selectedItems()[0].text()
        except IndexError:
            return
        if show_question(
            self, "TRULY ERASE IT?",
            f"Do you really want to delete the playlist '{selected}'?",
        ) == QMessageBox.StandardButton.Yes:
            if selected in self.playlists_d:
                del self.playlists_d[selected]
                self.updateUi()

    def playlist_selection_changed(self) -> None:
        try:
            self.selected_playlist = self.playlists.selectedItems()[0].text()
        except IndexError:
            self.selected_playlist = None
        self.updateUi()


class PlaylistRunnerDialog(QDialog, Ui_PlaylistRunner):  # type: ignore[misc]
    def __init__(
        self,
        playlist_name: str,
        playlist: list[str],
        ut_proc_name: str,
        dr_proc_name: str,
        ut_save_path: Path | str,
        dr_save_path: Path | str,
        steam: bool,
        ut_file_path: Path | str = "",
        dr_file_path: Path | str = "",
        parent: QWidget | None = None,
    ) -> None:
        if not steam and (not ut_file_path or not dr_file_path):
            raise ValueError(
                "If steam is False, ut_file_path and dr_file_path must be set."
            )
        super().__init__(parent)
        self.playlist_name = playlist_name
        self.playlist = playlist
        self.ut_proc_name = ut_proc_name
        self.dr_proc_name = dr_proc_name
        self.ut_save_path = ut_save_path
        self.dr_save_path = dr_save_path
        self.steam = steam
        self.ut_file_path = ut_file_path
        self.dr_file_path = dr_file_path
        self.current_save: str = ""
        self.play_cooldown: float = 0.0
        self.setupUi(self)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_play)
        self.timer.setInterval(100)
        self.timer.start()
        self.update_play()
        self.updateUi()
        self.connectSignalsSlots()

    def updateUi(self) -> None:
        self.setWindowIcon(QIcon(str(ICONS_PATH / "icon.png")))
        self.displayPlaylist.setText(self.playlist_name)
        self.displayCurSave.setText(self.current_save)
        self.displayNextSave.setText(self.playlist[0] if self.playlist else "")
        self.displayRemaining.setText(str(len(self.playlist)))

    def connectSignalsSlots(self) -> None:
        self.cancelBtn.clicked.connect(self.close)

    def update_play(self) -> None:
        self.play_cooldown -= self.timer.interval() / 1000.0
        if (
            model.program_running(self.ut_proc_name)
            or model.program_running(self.dr_proc_name)
            or self.play_cooldown > 0.0
        ):
            return
        if not self.playlist:
            self.close()
            return
        save = self.current_save = self.playlist.pop(0)
        self.updateUi()
        if save in model.get_undertale_saves():
            model.copy_undertale_save(save, self.ut_save_path)
            if self.steam:
                model.launch_steam_ut()
            else:
                model.launch_file(self.ut_file_path)
            self.play_cooldown = 10.0
        elif save in model.get_deltarune_saves():
            model.copy_deltarune_save(save, self.dr_save_path)
            if self.steam:
                model.launch_steam_dr()
            else:
                model.launch_file(self.dr_file_path)
            self.play_cooldown = 10.0

    def keyPressEvent(self, a0: QKeyEvent | None) -> None:
        if a0 and a0.key() == Qt.Key.Key_Escape:
            a0.ignore()
        else:
            super().keyPressEvent(a0)


class CreateDialog(QDialog, Ui_Create):  # type: ignore[misc]
    def __init__(
        self, parent: QWidget | None = None,
        game: Game | None = None,
    ) -> None:
        super().__init__(parent)
        self.game = game
        self.setupUi(self)
        self.updateUi()
        self.connectSignalsSlots()

    def updateUi(self) -> None:
        self.setWindowIcon(QIcon(str(ICONS_PATH / "icon.png")))
        if self.game == "undertale":
            self.undertaleRadio.setChecked(True)
        elif self.game == "deltarune":
            self.deltaruneRadio.setChecked(True)
        if self.game:
            self.undertaleRadio.setEnabled(False)
            self.deltaruneRadio.setEnabled(False)

    def connectSignalsSlots(self) -> None:
        self.buttonBox.accepted.connect(self.accept_requested)

    def accept_requested(self) -> None:
        can_accept = True
        if not any(
            (self.undertaleRadio.isChecked(), self.deltaruneRadio.isChecked())
        ):
            show_error(
                self, "Don't you care enough to assign your SAVE to a game?",
                "Please select the game this SAVE is for.",
            )
            return
        name = self.nameEdit.text().strip()
        if not name or name.lower() in (
            *map(str.lower, model.get_undertale_saves()),
            *map(str.lower, model.get_deltarune_saves()),
        ):
            show_error(
                self, "Don't you care enough to give your SAVE a unique name?",
                "Please give your SAVE a unique name.",
            )
            return
        if can_accept:
            self.accept()


class About(QDialog, Ui_About):  # type: ignore[misc]
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()

    def setupUi(self, *args: Any, **kwargs: Any) -> None:
        super().setupUi(*args, **kwargs)
        self.setWindowIcon(QIcon(str(ICONS_PATH / "icon.png")))
        self.versionDisplay.setText(version_string)

    def connectSignalsSlots(self) -> None:
        self.openGithubBtn.clicked.connect(
            partial(
                open_url,
                "https://github.com/TheCheese42/ut-dr-save-manager"
            )
        )


def reverse_lookup(d: dict[Any, Any], value: Any) -> Any:
    for k, v in d.items():
        if v == value:
            return k
    return None


def main() -> None:
    init_config(DEFAULT_CONFIG)
    UNDERTALE_SAVES_PATH.mkdir(parents=True, exist_ok=True)
    DELTARUNE_SAVES_PATH.mkdir(parents=True, exist_ok=True)
    BACKUP_PATH.mkdir(parents=True, exist_ok=True)

    app = QApplication(sys.argv)
    app.setApplicationName("ut-dr-save-manager")
    app.setApplicationDisplayName("SaveManager For UNDERTALE/deltarune")
    font = app.font()
    font.setFamily("Liberation Sans")
    app.setFont(font)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
