import sys
from PyQt6.QtWidgets import QApplication
from gui.neko_input_box import InputBox

if __name__ == "__main__":
    app = QApplication(sys.argv)
    input_box = InputBox()
    content = input_box.get_content()
    print(f"User entered: {content}")
    sys.exit(0)
