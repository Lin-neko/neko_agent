import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from neko_log_window import NekoLogWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    log_window = NekoLogWindow()
    log_window.show()
    
    # 使用QTimer实现非阻塞的定时添加日志
    counter = [0]  # 使用列表作为可变对象
    max_count = 10
    
    def add_log_message():
        if counter[0] < max_count:
            counter[0] += 1
            log_window.append_log(f"测试信息 {counter[0]}: 这是第{counter[0]}条日志信息")
            if counter[0] < max_count:
                # 设置下一个定时器
                QTimer.singleShot(100, add_log_message)  # 100毫秒 = 0.1秒
            else:
                print("已完成10条日志信息的添加")
        else:
            print("已完成10条日志信息的添加")
    
    # 启动第一个定时器
    QTimer.singleShot(100, add_log_message)
    
    app.exec()
