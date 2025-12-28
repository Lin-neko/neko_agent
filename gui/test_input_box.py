import sys
from PyQt6.QtWidgets import QApplication
from neko_input_box import InputBox

if __name__ == "__main__":
    app = QApplication(sys.argv)
    input_box = InputBox()
    input_box.set_mode("normal")
    content = input_box.get_content()
    chat_box = InputBox()
    chat_box.set_mode("chat")
    chat_content = chat_box.get_content()
    print(f"User entered: {content} chat:{chat_content}")
