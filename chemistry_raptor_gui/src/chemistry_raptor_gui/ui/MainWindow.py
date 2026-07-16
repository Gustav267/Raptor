"""Holds the main window of the application."""

import logging
import sys

import requests
from PyQt6.QtCore import QUrl, QCoreApplication
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QApplication
from requests import HTTPError

from chemistry_raptor_gui.ui.MainScrollArea import MainScrollArea
from chemistry_raptor_gui.ui.Menubar import Menubar
from chemistry_raptor_gui.ui.Potentiometrie import PotentiometrieWindow

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, current_version: str) -> None:
        """The Main Window of the application.

        This is the main window of the application. It holds the homepage or the wizard and the menubar.
        """
        super().__init__()

        self.setWindowTitle("Potentiometrie GUI")
        self.setMinimumSize(600, 400)
        self.resize(800, 600)
        self.showMaximized()

        self.potentiometrie = PotentiometrieWindow(self)
        self.scroll_area = MainScrollArea(self.potentiometrie)
        self.setCentralWidget(self.scroll_area)

        self.setMenuBar(
            Menubar(
                clear_data=lambda: self.potentiometrie.data_input.reset_data(None),
                import_data=self.potentiometrie.context_menu_bar.import_button,
                add_data_row=lambda: self.potentiometrie.data_input.add_row(),
                generate_plot=self.potentiometrie.generate_plot,
                parent=self,
            )
        )

        check_update(self, current_version)


def check_update(parent: QMainWindow, current_version: str):
    update_check_url = "https://api.github.com/repos/Gustav267/Raptor/releases/latest"

    try:
        result = requests.get(update_check_url)

        if result.status_code != 200:
            logger.error(
                f"Could not perform update check. Http response: {result.status_code}"
            )
            return
        data = result.json()
        if "tag_name" not in data:
            logger.error("Could not perform update check. No tag was found")
            return
        if data["tag_name"] == "v" + current_version:
            return

        logger.info(f"Update available: v{data['tag_name']}")

        button = QMessageBox.question(
            parent,
            "Update verfügbar",
            f"""Ein Update auf Version {data["tag_name"]} ist verfügbar.
Möchten Sie die Webseite öffnen, um das Update herunterzuladen?""",
        )

        if button == QMessageBox.StandardButton.Yes:
            QDesktopServices.openUrl(
                QUrl("https://github.com/Gustav267/Raptor/releases/latest")
            )
            QCoreApplication.quit()
            sys.exit(0)

    except HTTPError as e:
        logger.exception(
            f"Could not perform update check. Http response: {e.response}",
            exc_info=True,
        )
