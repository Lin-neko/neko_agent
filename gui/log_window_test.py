import sys
from PyQt6.QtWidgets import QApplication
from neko_log_window import NekoLogWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    log_window = NekoLogWindow()
    log_window.show()

    # 测试日志功能
    log_window.append_log("这是一个测试日志信息。")
    log_window.append_log("第二条日志信息。")
    log_window.append_log("第三条日志信息，这条信息比较长，看看会不会自动换行和滚动。")
    for i in range(20):
        log_window.append_log(f"这是第 {i+4} 条日志信息。")
    sys.exit(app.exec())