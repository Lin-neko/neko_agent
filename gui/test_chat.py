import sys
from PyQt6.QtWidgets import QApplication
from neko_input_box import InputBox
from neko_chat_window import NekoChatWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    input_box = InputBox()
    input_box.set_mode("chat")
    chatapp = QApplication(sys.argv)
    window = NekoChatWindow()
    window.show()
    input_box.show()
    window.append_user_msg("你好，这是一个用户发送的测试消息。")
    window.append_agent_msg("你好！这是一个代理回复的测试消息。")
    window.append_user_msg(f"123")
    window.append_agent_msg(f"`md`")
    
    print("聊天历史：", window.get_history())
    sys.exit(app.exec())
