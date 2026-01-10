from PyQt6.QtWidgets import QWidget, QApplication, QPushButton, QTextEdit, QVBoxLayout
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QDateTime, QPropertyAnimation
from PyQt6.QtGui import QIcon, QPixmap, QRegion, QTextBlockFormat, QTextCursor, QTextCharFormat, QFont,QTextImageFormat
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gui.dark_mode_manager import dark_or_light
import json
import re


class TransparentWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(QRect(100,100,100,100))
        self.setStyleSheet("background: transparent;")

class NekoChatWindow(QWidget):
    closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(200)  # 动画持续时间200毫秒

        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)
        self.user_name = config["chat_settings"]["chat_user_name"]
        self.agent_name = config["chat_settings"]["chat_agent_name"]

        screen_geometry = QApplication.primaryScreen().geometry()
        self.original_geometry = QRect(
            int(screen_geometry.width() * 0.15),
            int(screen_geometry.height() * 0.1),
            int(screen_geometry.width() * 0.75), 
            int(screen_geometry.height() * 0.7)
        )
        self.setGeometry(self.original_geometry)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.chat_display.setObjectName("chatDisplay")

        layout = QVBoxLayout(self)
        layout.addWidget(self.chat_display)
        layout.setContentsMargins(10, 45, 10, 10)
        self.setLayout(layout)

        self.setObjectName("NekoChatWindow")
        self.setStyleSheet("""
            QWidget#NekoChatWindow {
                background-color: #282c34;
                border-radius: 10px;
            }
            QTextEdit#chatDisplay {
                background-color: #282c34;
                color: #abb2bf;
                font-family: "Cascadia Code", "Consolas", "Monaco", "Courier New", monospace;
                font-size: 10pt;
                border: 1px solid #3e4452; 
                border-radius: 10px; 
                padding: 10px; 
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
        self.setRoundedCorners()


        self.minimize_button = QPushButton("", self)
        self.minimize_button.setObjectName("minimizeButton")
        self.minimize_button.setGeometry(10, 10, 30, 30)
        self.minimize_button.setStyleSheet(f"""
            QPushButton#minimizeButton {{
                background-color: transparent;
                border-radius: 15px;
                border: none;
            }}
        """)
        self.minimize_button.clicked.connect(self.minimize_window)

        self.log_history = [] # 用于存储对话历史，每个元素是一个字典 {'sender': 'user'/'agent', 'message': 'content'}

        self._update_style_based_on_background()

        self.message_queue = []
        self.user_message_read_position = 0
        self.agent_message_read_position = 0

        self.timer = self.startTimer(1000)  # 每隔1秒读取一次文件

    def timerEvent(self, event):
        if event.timerId() == self.timer:
            self._read_and_append_messages()

    def _read_and_append_messages(self):
        self._read_user_messages()
        self._read_agent_messages()

    def _read_user_messages(self):
        try:
            with open(".\\cache\\user_message.txt", "r", encoding="utf-8") as f:
                content = f.read()
                new_messages = content[self.user_message_read_position:]
                if new_messages:
                    messages = re.split(r'\[message_end\]', new_messages)
                    for message in messages:
                        if message.strip():
                            self._append_message(message, 'user')
                    self.user_message_read_position = len(content)
        except FileNotFoundError:
            pass

    def _read_agent_messages(self):
        try:
            with open(".\\cache\\agent_message.txt", "r", encoding="utf-8") as f:
                content = f.read()
                new_messages = content[self.agent_message_read_position:]
                if new_messages:
                    messages = re.split(r'\[message_end\]', new_messages)
                    for message in messages:
                        if message.strip():
                            self._append_message(message, 'agent')
                    self.agent_message_read_position = len(content)
        except FileNotFoundError:
            pass

    def _append_message(self, message, sender):
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        if sender == 'user':
            avatar_path = os.path.join("gui", "img", "user_avatar.png")
            alignment = Qt.AlignmentFlag.AlignRight
            name = self.user_name
        else:
            avatar_path = os.path.join("gui", "img", "agent_avatar.JPG")
            alignment = Qt.AlignmentFlag.AlignLeft
            name = self.agent_name

        self.log_history.append({
            'sender': sender,
            'message': message,
            'timestamp': timestamp
        })

        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        block_format = QTextBlockFormat()
        block_format.setAlignment(alignment)
        block_format.setTopMargin(10)
        block_format.setBottomMargin(10)

        cursor.setBlockFormat(block_format)

        if sender == 'user':
            lines = message.split('\n')
            for i, line in enumerate(lines):
                cursor.insertText(f" {line} ")
                if i < len(lines) - 1:
                    cursor.insertText("\n")  # 为多行消息添加换行

            cursor.insertText(f"[{timestamp}]:{name} ")

            if os.path.exists(avatar_path):
                avatar_format = QTextImageFormat()
                avatar_format.setWidth(20)
                avatar_format.setHeight(20)
                avatar_format.setName(avatar_path)
                cursor.insertImage(avatar_format)
        else:
            if os.path.exists(avatar_path):
                avatar_format = QTextImageFormat()
                avatar_format.setWidth(20)
                avatar_format.setHeight(20)
                avatar_format.setName(avatar_path)
                cursor.insertImage(avatar_format)

            cursor.insertText(f" {name} [{timestamp}]: ")
            cursor.insertMarkdown(message)

        cursor.insertText("\n")

        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def get_history(self):
        return self.log_history

    def _update_style_based_on_background(self):
        """根据屏幕背景亮度更新样式表"""
        x = self.x() + self.width() // 2
        y = self.y() + self.height() // 2
        dark_mode = dark_or_light(x, y)

        if dark_mode == "Light":
            # 浅色主题
            text_color = "#000000"
            bg_color = "#ffffff"
            border_color = "#cccccc"
            scrollbar_bg = "#f0f0f0"
            scrollbar_handle = "#c0c0c0"
            # 设置最小化按钮图标
            self.minimize_button.setIcon(QIcon(QPixmap("gui/img/minimize_light.png")))
        else:
            # 深色主题
            text_color = "#abb2bf"
            bg_color = "#282c34"
            border_color = "#3e4452"
            scrollbar_bg = "#282c34"
            scrollbar_handle = "#4b5263"
            # 设置最小化按钮图标
            self.minimize_button.setIcon(QIcon(QPixmap("gui/img/minimize_dark.png")))

        self.setStyleSheet(f"""
            QWidget#NekoChatWindow {{
                background-color: {bg_color};
                border-radius: 10px;
            }}
            QTextEdit#chatDisplay {{
                background-color: {bg_color};
                color: {text_color};
                font-family: "Cascadia Code", "Consolas", "Monaco", "Courier New", monospace;
                font-size: 10pt;
                border: 1px solid {border_color};
                border-radius: 10px;
                padding: 10px;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {scrollbar_bg};
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {scrollbar_handle};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

    def set_opacity(self, opacity):
        self.setWindowOpacity(opacity)

    def setRoundedCorners(self):
        radius = 10
        path = QRegion(0, 0, self.width(), self.height(), QRegion.RegionType.Rectangle)
        rounded = QRegion(0, 0, self.width(), self.height(), QRegion.RegionType.Ellipse)
        corner = QRegion(0, 0, radius * 2, radius * 2, QRegion.RegionType.Ellipse)
        
        top_left = corner
        top_right = corner.translated(self.width() - radius * 2, 0)
        bottom_left = corner.translated(0, self.height() - radius * 2)
        bottom_right = corner.translated(self.width() - radius * 2, self.height() - radius * 2)
        
        rounded_region = top_left.united(top_right).united(bottom_left).united(bottom_right)
        rectangular_region = QRegion(0, radius, self.width(), self.height() - radius * 2)
        rounded_region = rounded_region.united(rectangular_region)
        rectangular_region = QRegion(radius, 0, self.width() - radius * 2, self.height())
        rounded_region = rounded_region.united(rectangular_region)
        
        self.setMask(rounded_region)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setRoundedCorners()

    def close_window(self):
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.hide)
        self.animation.start()
        self.closed.emit()

    def minimize_window(self):
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.hide)
        self.animation.start()
        self.show_minimized_button()

    def show_minimized_button(self):
        if not hasattr(self, 'minimized_button'):
            self.tmp_window = TransparentWindow(self.parentWidget())
            self.minimized_button = QPushButton("Chat", self.tmp_window)
            self.minimized_button.setObjectName("minimizedButton")
            # 将按钮放置在屏幕左下角
            screen_geometry = QApplication.primaryScreen().geometry()
            self.minimized_button.setGeometry(0, 0, 50, 50)
            self.tmp_window.setGeometry(10, screen_geometry.height() - 60, 50, 50)
            self.tmp_window.show()
            self.minimized_button.setStyleSheet(f"""
                QPushButton#minimizedButton {{
                    background-color: #6c757d;
                    color: white;
                    border-radius: 5px;
                    border: none;
                }}
            """)
            self.minimized_button.clicked.connect(self.restore_window)
        self.minimized_button.show()

    def restore_window(self):
        self.minimized_button.hide()
        self.show()

    def showEvent(self, event):
        self.setWindowOpacity(0.0)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        try:
            self.animation.finished.disconnect()  # 移除之前的连接
        except TypeError:
            pass
        super().showEvent(event)
        self._update_style_based_on_background()
        self.animation.start()

    def clear_log(self):
        self.chat_display.clear()
        self.log_history.clear()
