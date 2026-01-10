import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from PyQt6.QtWidgets import QApplication
from gui.neko_chat_window import NekoChatWindow

app = QApplication(sys.argv)
window = NekoChatWindow()
window.show()

sys.exit(app.exec())