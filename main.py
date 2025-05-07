import os
import sys
from license_validator import validate_license, register_license
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon
import database
from database import DB_PATH

from ui.main_window import MainWindow

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def main():
    """
    Main entry point for the application.
    Initializes the database and launches the GUI.
    """
    # Initialize the PyQt application FIRST
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # License validation AFTER QApplication is ready
    if not validate_license():
        print("Invalid or expired license. Starting registration process.")
        if not register_license():
            print("License registration failed or cancelled.")
            return

    # Create the database if it doesn't exist
    database.create_database()

    # Load stylesheet
    try:
        qss_path = resource_path("style.qss")
        with open(qss_path, "r") as style_file:
            app.setStyleSheet(style_file.read())
    except Exception as e:
        print(f"Error loading stylesheet: {e}")

    # Create main window
    window = MainWindow()
    window.show()
    print("Retail Master application started")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
