#!/usr/bin/env python3
# Main application entry point

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

from ui.main_window import MainWindow
from utils.logger import setup_logger

def main():
    """Main application entry point"""
    # Setup logger
    logger = setup_logger()
    logger.info("Starting EEPROM Programmer application")

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("EEPROM Programmer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("EEPROM Tools")
    
    # Set application style
    with open("ui/styles/dark_theme.qss", "r") as f:
        app.setStyleSheet(f.read())
    
    # Create settings
    settings = QSettings("EEPROM Tools", "EEPROM Programmer")
    
    # Create and show main window
    window = MainWindow(settings, logger)
    window.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()