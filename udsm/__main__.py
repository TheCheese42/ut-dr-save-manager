import sys
from pathlib import Path

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

from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (QApplication, QDialog, QMainWindow, QMessageBox,
                             QWidget)


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
        self.setupUi(self)
        self.updateUi()
        self.connectSignalsSlots()

    def updateUi(self) -> None:
        self.undertaleSavePath.setText(get_config_value("undertale_save_path"))
        self.deltaruneSavePath.setText(get_config_value("deltarune_save_path"))
        self.undertaleFilePath.setText(get_config_value("undertale_file_path"))
        self.deltaruneFilePath.setText(get_config_value("deltarune_file_path"))
        self.undertaleSavesList.clear()
        self.deltaruneSavesList.clear()
        for save in model.get_undertale_saves():
            self.undertaleSavesList.addItem(save)
        for save in model.get_deltarune_saves():
            self.deltaruneSavesList.addItem(save)

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

        create = CreateDialog(self)
        if create.exec() == QDialog.DialogCode.Accepted:
            name = create.nameEdit.text()
            if create.undertaleRadio.isChecked():
                model.create_undertale_save(name, lines[0])
            else:
                model.create_deltarune_save(name, lines[0])
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
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()

    def connectSignalsSlots(self) -> None:
        self.buttonBox.accepted.connect(self.accept_requested)

    def accept_requested(self) -> None:
        if (
            (self.undertaleRadio or self.deltaruneRadio)
            and self.nameEdit.text()
        ):
            self.accept()
        else:
            self.reject()


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
