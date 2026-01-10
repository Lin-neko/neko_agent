import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from gui.neko_settings_window import NekoSettingsWindow
from PyQt6.QtWidgets import QApplication
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NekoSettingsWindow()
    window.get_settings()

        
    sys.exit(app.exec())