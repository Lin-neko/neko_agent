from PyQt6.QtWidgets import QTextEdit, QApplication , QPushButton, QLabel
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPixmap
import sys

class NekoPMS(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_geometry = QRect(int(QApplication.primaryScreen().geometry().width() * 0.9 - QApplication.primaryScreen().geometry().width() * 0.15 // 2),
                                       int(QApplication.primaryScreen().geometry().height() * 0.15),
                                       int(QApplication.primaryScreen().geometry().width() * 0.15),
                                       int(QApplication.primaryScreen().geometry().height() * 0.2))
        self.setGeometry(self.original_geometry)
        self.setReadOnly(True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #282c34; /* 深灰色背景 */
                color: #abb2bf; /* 浅灰色文本 */
                font-family: "Cascadia Code", "Consolas", "Monaco", "Courier New", monospace;
                font-size: 10pt;
                border: 1px solid #3e4452; /* 边框 */
                border-radius: 5px; /* 轻微圆角 */
                padding: 5px; /* 内边距 */
            }
            QScrollBar:vertical {
                border: none;
                background: #282c34;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #4b5263;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.approve_btn = QPushButton('允许', self)
        self.approve_btn.setGeometry(int(self.width() * 0.06),
                                     int(self.height() * 0.75),
                                     int(self.width() * 0.42),
                                     int(self.height() * 0.2))
        self.approve_btn.setStyleSheet("""
            QPushButton {
                background-color: #abb2bf;
                color: #3e4452;
                font-family: "Cascadia Code", "Consolas", "Monaco", "Courier New", monospace;
                border: 1px solid #4b5263;
                border-radius: 10px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #787d86;
            }
            QPushButton:pressed {
                background-color: #282c34;
            }
        """)
        self.reject_btn = QPushButton('拒绝', self)
        self.reject_btn.setGeometry(int(self.width() * 0.53),
                                     int(self.height() * 0.75),
                                     int(self.width() * 0.42),
                                     int(self.height() * 0.2))
        self.reject_btn.setStyleSheet("""
            QPushButton {
                background-color: #3e4452;
                color: #abb2bf;
                font-family: "Cascadia Code", "Consolas", "Monaco", "Courier New", monospace;
                border: 1px solid #4b5263;
                border-radius: 10px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #4b5263;
            }
            QPushButton:pressed {
                background-color: #282c34;
            }
        """)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setGeometry(0,int(self.approve_btn.height() - 10), int(self.width()), int(self.height() * 0.7))
        self.label.setStyleSheet("""
            QLabel {
                color: #abb2bf;
                font-family: "Cascadia Code", "Consolas", "Monaco", "Courier New", monospace;
                font-size: 10pt;
            }
        """)
        self.cmd_icon = QLabel(self)
        self.cmd_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cmd_icon.setGeometry(int(self.width() * 0.38),int(self.height()*0.1), int(self.width()*0.25), int(self.height() * 0.2))
        self.cmd_icon.setPixmap(QPixmap('gui\\img\\cmd_exec.png'))
        self.cmd_icon.setScaledContents(True)
        self.cmd_icon.hide()

        self.file_icon = QLabel(self)
        self.file_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_icon.setGeometry(int(self.width() * 0.38),int(self.height()*0.1), int(self.width()*0.25), int(self.height() * 0.2))
        self.file_icon.setPixmap(QPixmap('gui\\img\\file.png'))
        self.file_icon.setScaledContents(True)
        self.file_icon.hide()

        self.file_edit_icon = QLabel(self)
        self.file_edit_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_edit_icon.setGeometry(int(self.width() * 0.38),int(self.height()*0.1), int(self.width()*0.25), int(self.height() * 0.2))
        self.file_edit_icon.setPixmap(QPixmap('gui\\img\\file_edit.png'))
        self.file_edit_icon.setScaledContents(True)
        self.file_edit_icon.hide()

        self.popen_icon = QLabel(self)
        self.popen_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.popen_icon.setGeometry(int(self.width() * 0.38),int(self.height()*0.1), int(self.width()*0.25), int(self.height() * 0.2))
        self.popen_icon.setPixmap(QPixmap('gui\\img\\popen.png'))
        self.popen_icon.setScaledContents(True)
        self.popen_icon.hide()
    def cmd_exec_check(self, cmd):
        self.cmd_icon.show()
        self.label.setText(f"Neko尝试运行命令\n{cmd}\n是否允许?")
    
    def popen_check(self, cmd):
        self.popen_icon.show()
        self.label.setText(f'Neko尝试在后台运行命令\n{cmd}\n是否允许?')

    def file_read_check(self, file_path):
        self.file_icon.show()
        self.label.setText(f"Neko尝试读取文件\n{file_path}\n是否允许")
    
    def file_write_check(self, file_path):
        self.file_edit_icon.show()
        self.label.setText(f"Neko尝试写入文件\n{file_path}\n是否允许")
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    dummy_window = NekoPMS()
    dummy_window.show()
    dummy_window.file_read_check("123")
    
    sys.exit(app.exec())
