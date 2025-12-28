from neko_settings_window import NekoSettingsWindow
import sys
from PyQt6.QtWidgets import QApplication
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NekoSettingsWindow()
    window.get_settings()

        
    sys.exit(app.exec())