import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QHBoxLayout, QPushButton, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer, QEventLoop
from PyQt6.QtGui import QIcon, QPixmap
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from gui.dark_mode_manager import dark_or_light
import json,ctypes

class InputBox(QWidget):
    mode = 'normal'
    def set_mode(self, mode_value):
        self.mode = mode_value
        self.update_placeholder_text()

    def update_placeholder_text(self):
        if self.mode == 'normal':
            self.input_field.setPlaceholderText("给Neko下达任务吧~(回车发送,输入空内容或按左侧按键取消)")
        elif self.mode == 'chat':
            self.input_field.setPlaceholderText("发送信息(回车发送,输入空内容或按左侧按键取消)")

    def __init__(self, parent=None):
        super().__init__(parent)
        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)
        
        self.anti_grab = config["anti_grab"]
        if self.anti_grab == True :
            SetWindowDisplayAffinity = ctypes.windll.user32.SetWindowDisplayAffinity
            SetWindowDisplayAffinity.restype = ctypes.c_bool
            SetWindowDisplayAffinity(int(self.winId()) , 0x00000011)
        self.mode = 'normal'
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._result = None

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(30)
        self.input_field = QLineEdit(self)
        self.update_placeholder_text()
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 240);
                border-radius: 20px;
                padding: 10px;
                font-size: 16px;
                color: black;
                border: none;
            }
        """)
        self.input_field.returnPressed.connect(self.on_return_pressed)

        self.cancel_button = QPushButton(self)

        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 240);
                border-radius: 20px; 
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 255); 
            }
        """)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)

        self.main_layout.addWidget(self.input_field)
        self.main_layout.addWidget(self.cancel_button)
        self.setLayout(self.main_layout)

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(400)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.initial_pos_set = False

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(400)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.exit_animation = QPropertyAnimation(self, b"geometry")
        self.exit_animation.setDuration(400)
        self.exit_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.exit_animation.finished.connect(self._finish_exit)

        self.send_button_opacity_effect = QGraphicsOpacityEffect(self.cancel_button)
        self.cancel_button.setGraphicsEffect(self.send_button_opacity_effect)
        self.send_button_opacity_animation = QPropertyAnimation(self.send_button_opacity_effect, b"opacity")
        self.send_button_opacity_animation.setDuration(400)
        self.send_button_opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.send_button_exit_animation = QPropertyAnimation(self.cancel_button, b"geometry")
        self.send_button_exit_animation.setDuration(400)
        self.send_button_exit_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def showEvent(self, event):
        if not self.initial_pos_set:
            screen = QApplication.primaryScreen()
            screen_rect = screen.geometry()
            width = int(screen_rect.width() * 0.7)
            height = int(screen_rect.height() * 0.2)
            x = (screen_rect.width() - width) // 2
            start_y = screen_rect.height()
            end_y = screen_rect.height() - height - 20 

            self.setGeometry(x, start_y, width, height)
            self.animation.setStartValue(QRect(x, start_y, width, height))
            self.animation.setEndValue(QRect(x, end_y, width, height))
            self.animation.start()
            self.initial_pos_set = True
            self.input_field.setFocus() 
            btn_width = self.input_field.height()
            self.cancel_button.setFixedSize(btn_width , btn_width)
            self.cancel_button.setStyleSheet(self.cancel_button.styleSheet() + f"""
                QPushButton {{
                    border-radius: {btn_width // 2}px;
                }}
            """)
            self.cancel_button.setIconSize(self.cancel_button.size())

        self._update_style_based_on_background()
        super().showEvent(event)

    def _update_style_based_on_background(self):
        dark_mode = dark_or_light(self.x() + self.width() // 2 , self.y() + self.height() // 2)
        if dark_mode == "Dark" :
            text_color = "black"
            bg_color_input = "rgba(255, 255, 255, 240)"
            bg_color_button = "rgba(255, 255, 255, 240)"
            hover_color_button = "rgba(255, 255, 255, 255)"
            self.cancel_button.setIcon(QIcon(QPixmap("gui/img/close_light.png")))
            self.cancel_button.setIconSize(self.cancel_button.size())
        else:
            text_color = "white"
            bg_color_input = "rgba(0, 0, 0, 180)"
            bg_color_button = "rgba(0, 0, 0, 180)"
            hover_color_button = "rgba(0, 0, 0, 220)"
            self.cancel_button.setIcon(QIcon(QPixmap("gui/img/close_dark.png")))
            self.cancel_button.setIconSize(self.cancel_button.size())

            self.input_field.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {bg_color_input};
                    border-radius: 20px;
                    padding: 10px;
                    font-size: 16px;
                    color: {text_color};
                    border: none;
                }}
            """)
            
            btn_width = self.input_field.height()
            self.cancel_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color_button};
                    border-radius: {btn_width // 2}px; 
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {hover_color_button}; 
                }}
            """)
    def on_return_pressed(self):
        self._result = self.input_field.text()
        self._start_exit_animation()

    def on_cancel_clicked(self):
        self.input_field.clear()
        self._start_exit_animation()

    def _start_exit_animation(self):
        start_rect = self.geometry()
        end_rect = QRect(start_rect.x() + start_rect.width() // 2, -200, 0, 0)
        self.exit_animation.setStartValue(start_rect)
        self.exit_animation.setEndValue(end_rect)
        self.exit_animation.start()

        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.start()

        btn_start_rect = self.cancel_button.geometry()
        btn_end_rect = QRect(btn_start_rect.x() + btn_start_rect.width() //2 , 0 , 0, 0)
        self.send_button_exit_animation.setStartValue(btn_start_rect)
        self.send_button_exit_animation.setEndValue(btn_end_rect)
        self.send_button_exit_animation.start()

        self.send_button_opacity_animation.setStartValue(1.0)
        self.send_button_opacity_animation.setEndValue(0.0)
        self.send_button_opacity_animation.start()

    def _finish_exit(self):
        self.hide()
        if hasattr(self, '_event_loop'):
            self._event_loop.exit()

    def get_content(self):
        self._result = None
        self.show()
        self._event_loop = QEventLoop()
        self._event_loop.exec()
        if self._result == "":
            return None
        return self._result
