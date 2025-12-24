from PyQt6.QtWidgets import QTextEdit, QApplication, QPushButton
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QIcon, QPixmap
import sys

class NekoLogWindow(QTextEdit):
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

        self.is_collapsed = False

        self.log_history = [] # 用于存储日志内容

        self.collapse_button = QPushButton("", self)
        self.collapse_button.setObjectName("collapseButton") # 添加objectName
        self.original_button_geometry = QRect(int(self.width() * 0.8), int(self.height() *0.05 ), 20, 20)
        self.collapse_button.setGeometry(self.original_button_geometry)
        self.collapse_button.setStyleSheet("""
            QPushButton#collapseButton {
                background-color: transparent;
                border-radius: 10px; 
                border: none;
            }
            QPushButton#collapseButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.collapse_button.setIcon(QIcon(QPixmap("gui/img/log_expand.PNG")))
        self.collapse_button.setIconSize(self.collapse_button.size())
        self.collapse_button.clicked.connect(self.toggle_collapse)

    def append_log(self, message):
        self.log_history.append(message) # 将日志添加到历史记录
        if not self.is_collapsed: # 只有在未折叠状态下才显示
            self.append(message)
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def toggle_collapse(self):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300) 
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        if self.is_collapsed:
            # 展开
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(self.original_geometry)
            self.is_collapsed = False
            self.collapse_button.setGeometry(self.original_button_geometry) # 按钮恢复到原始位置
            self.verticalScrollBar().show() # 显示滚动条
            self.collapse_button.setIcon(QIcon(QPixmap("gui/img/log_expand.PNG")))
            self.collapse_button.setIconSize(self.collapse_button.size())
            # 恢复日志窗口的原始样式
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
            # 恢复按钮的原始样式
            self.collapse_button.setStyleSheet("""
                QPushButton#collapseButton {
                    background-color: transparent;
                    border-radius: 10px;
                    border: none;
                }
                QPushButton#collapseButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            self.animation.finished.connect(self.restore_log_content) # 动画结束后恢复日志内容
        else:
            # 折叠
            collapsed_size = 20
            collapsed_geometry = QRect(self.x() + self.collapse_button.x(),
                                       self.y() + self.collapse_button.y(),
                                       collapsed_size, collapsed_size)
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(collapsed_geometry)
            self.is_collapsed = True
            self.document().clear() # 清空内容，使其不可见
            self.verticalScrollBar().hide() # 隐藏滚动条
            # 调整按钮位置，使其在折叠状态下居中
            self.collapse_button.setGeometry(0, 0, collapsed_size, collapsed_size)
            self.collapse_button.setIcon(QIcon(QPixmap("gui/img/log_fold.PNG")))
            self.collapse_button.setIconSize(self.collapse_button.size())
            # 修改日志窗口的样式，使其变为圆形
            self.setStyleSheet(f"""
                QTextEdit {{
                    background-color: #282c34;
                    color: #abb2bf;
                    font-family: "Cascadia Code", "Consolas", "Monaco", "Courier New", monospace;
                    font-size: 10pt;
                    border: 1px solid #3e4452;
                    border-radius: {collapsed_size // 2}px; /* 使窗口变为圆形 */
                    padding: 0px; /* 折叠时移除内边距 */
                }}
                QScrollBar:vertical {{
                    border: none;
                    background: #282c34;
                    width: 10px;
                    margin: 0px 0px 0px 0px;
                }}
                QScrollBar::handle:vertical {{
                    background: #4b5263;
                    min-height: 20px;
                    border-radius: 5px;
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    background: none;
                }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                    background: none;
                }}
                QPushButton#collapseButton {{ /* 使用objectName来选择按钮 */
                    background-color: transparent; /* 按钮背景透明 */
                    border-radius: {collapsed_size // 2}px; /* 按钮变为圆形 */
                    border: none;
                }}
            """)

        self.animation.start()

    def restore_log_content(self):
        self.clear() # 清空当前显示
        for message in self.log_history: # 从历史记录中恢复
            self.append(message)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def clear_log(self):
        self.clear()

