import ctypes
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import sys
 
SetWindowDisplayAffinity = ctypes.windll.user32.SetWindowDisplayAffinity
SetWindowDisplayAffinity.restype = ctypes.c_bool
 
#文档https://learn.microsoft.com/zh-cn/windows/win32/api/winuser/nf-winuser-setwindowdisplayaffinity

WDA_NONE = 0x00000000 #可以截屏
WDA_MONITOR = 0x00000001 #截屏黑屏
WDA_EXCLUDEFROMCAPTURE = 0x00000011 #截屏隐身
 
class SecureWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("喵喵喵")
        self.setGeometry(100, 100, 600, 400)
 
        label = QLabel("123\n123\n123", self)
        label.setFont(QFont("Microsoft YaHei", 20))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(label)
 
    def showEvent(self, event):
        super().showEvent(event)
 
        hwnd = int(self.winId()) 
        SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE) #设在这里哦❤
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SecureWindow()
    window.show()
    sys.exit(app.exec())