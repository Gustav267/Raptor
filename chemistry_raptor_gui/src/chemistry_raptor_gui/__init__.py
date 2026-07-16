"""The Captura Main Module

This module contains the main entry point for the Captura application.

Captura is a templating program, that allows you to fill out LaTeX templates
from a predefined template and generate different kinds of LaTeX documents.
Due to its modular design, it is easily extensible with new templates."""

import logging
import sys

from PyQt6.QtWidgets import QApplication

from chemistry_raptor_gui.ui.MainWindow import MainWindow

# Uncomment this line on KDE to have a nicer layout/theme.
# os.environ["QT_QPA_PLATFORMTHEME"] = "kde"

__version__: str = "0.1.0"
"""The current version of the RAPTOR application."""

production: bool = False
"""Indicates whether the application is running in production mode or development mode."""

environment: str = "linux"
"""The current environment in which the application is running.

This can be `linux`, `windows`, or `macos`."""


def main():
    app = QApplication(sys.argv)
    # app.setStyle("Windows")
    # app.setStyle("Breeze")

    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
        level="DEBUG",
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting Potentiometrie GUI version v%s" % __version__)

    main_window = MainWindow(__version__)
    main_window.show()

    try:
        app.exec()
    except Exception as e:
        logger.critical("An unexpected error occurred", exc_info=e)
