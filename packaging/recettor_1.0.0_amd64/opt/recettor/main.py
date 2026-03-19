import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from database.db_manager import initialize_db
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 15))
    app.setApplicationName("Recettor")

    # Initialize database
    initialize_db()

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
