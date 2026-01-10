import sys
from PyQt6.QtWidgets import QApplication
from neko_chat_window import NekoChatWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NekoChatWindow()
    window.show()

    sys.exit(app.exec())
