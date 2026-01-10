import keyboard
import threading
import os
import time
from gui.msgbox import show_message

def emergency_keyboard_listener():
    def on_f1_f2_combo():
        print("检测到 F1 + F2 组合键，紧急退出...")
        show_message("Neko已停止","Neko与python已被终止")
        os.system("taskkill /f /im python.exe")

    keyboard.add_hotkey('f1+f2', on_f1_f2_combo)
    keyboard.wait()


if __name__ == '__main__':
    listener_thread = threading.Thread(target=emergency_keyboard_listener, daemon=True)
    listener_thread.start()
    while True:
        time.sleep(1)
