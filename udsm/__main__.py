import sys
from pathlib import Path
from typing import Any, Literal

try:
    from . import model  # type: ignore
    from .config import get_config_value, init_config, set_config_value
    from .ui.create_ui import Ui_Create
    from .ui.window_ui import Ui_MainWindow
except ImportError:
    import model
    from config import get_config_value, set_config_value, init_config
    from ui.create_ui import Ui_Create
    from ui.window_ui import Ui_MainWindow

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (QApplication, QDialog, QListWidgetItem,
                             QMainWindow, QMessageBox, QWidget)


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


class MainWindow(QMainWindow, Ui_MainWindow):  # type: ignore[misc]
    def __init__(self) -> None:
        super().__init__(None)
        self.saves_to_items_ut: dict[str, QListWidgetItem] = {}
        self.saves_to_items_dr: dict[str, QListWidgetItem] = {}
        self.setupUi(self)
        self.updateUi()
        self.connectSignalsSlots()

    def updateUi(self) -> None:
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
        self.addUndertaleToSaves.clicked.connect(self.add_undertale_to_saves)
        self.addDeltaruneToSaves.clicked.connect(self.add_deltarune_to_saves)
        self.undertaleSavesList.itemChanged.connect(
            self.undertale_item_renamed
        )
        self.deltaruneSavesList.itemChanged.connect(
            self.deltarune_item_renamed
        )
        self.launchUTSteam.clicked.connect(model.launch_steam_ut)
        self.launchDRSteam.clicked.connect(model.launch_steam_dr)
        self.launchUTFile.clicked.connect(
            lambda: model.launch_file(get_config_value("undertale_file_path"))
        )
        self.launchDRFile.clicked.connect(
            lambda: model.launch_file(get_config_value("deltarune_file_path"))
        )

    def undertale_item_renamed(self, item: QListWidgetItem) -> None:
        prev_name = reverse_lookup(self.saves_to_items_ut, item)
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
            model.rename_undertale_save(prev_name, new_name)
        self.updateUi()

    def deltarune_item_renamed(self, item: QListWidgetItem) -> None:
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
            model.rename_deltarune_save(prev_name, new_name)
        self.updateUi()

    def add_undertale_to_saves(self) -> None:
        self.create_save(get_config_value("undertale_save_path"), "undertale")

    def add_deltarune_to_saves(self) -> None:
        self.create_save(get_config_value("deltarune_save_path"), "deltarune")

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
        game: Literal["undertale", "deltarune"] | None = None,
    ) -> None:
        create = CreateDialog(self, game)
        if create.exec() == QDialog.DialogCode.Accepted:
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
        undertale_save_path = Path(get_config_value("undertale_save_path"))
        model.copy_undertale_save(selected, undertale_save_path)

    def apply_deltarune(self) -> None:
        try:
            selected = self.deltaruneSavesList.selectedItems()[0].text()
        except IndexError:
            return
        deltarune_save_path = Path(get_config_value("deltarune_save_path"))
        model.copy_deltarune_save(selected, deltarune_save_path)

    def delete_undertale(self) -> None:
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


class CreateDialog(QDialog, Ui_Create):  # type: ignore[misc]
    def __init__(
        self, parent: QWidget | None = None,
        game: Literal["undertale", "deltarune"] | None = None,
    ) -> None:
        super().__init__(parent)
        self.game = game
        self.setupUi(self)
        self.updateUi()
        self.connectSignalsSlots()

    def updateUi(self) -> None:
        if self.game == "undertale":
            self.undertaleRadio.setChecked(True)
        elif self.game == "deltarune":
            self.deltaruneRadio.setChecked(True)

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


def reverse_lookup(d: dict[Any, Any], value: Any) -> Any:
    for k, v in d.items():
        if v == value:
            return k
    return None


def main() -> None:
    init_config()
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
