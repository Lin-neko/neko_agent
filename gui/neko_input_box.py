import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QHBoxLayout, QPushButton, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer, QEventLoop
from PyQt6.QtGui import QIcon, QPixmap

class InputBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._result = None 
        self._app = QApplication.instance() if QApplication.instance() else QApplication(sys.argv)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(30)

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("请输入内容...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 20px;
                padding: 10px;
                font-size: 16px;
                color: black;
                border: none;
            }
        """)
        self.input_field.returnPressed.connect(self.on_return_pressed)

        self.send_button = QPushButton(self)
        send_icon_path = "gui/img/send.png"
        send_pixmap = QPixmap(send_icon_path)
        send_icon = QIcon(send_pixmap)
        self.send_button.setIcon(send_icon)
        self.send_button.setIconSize(self.send_button.size())

        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 20px; 
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 225); 
            }
        """)
        self.send_button.clicked.connect(self.on_return_pressed)

        self.main_layout.addWidget(self.input_field)
        self.main_layout.addWidget(self.send_button)
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

        self.send_button_opacity_effect = QGraphicsOpacityEffect(self.send_button)
        self.send_button.setGraphicsEffect(self.send_button_opacity_effect)
        self.send_button_opacity_animation = QPropertyAnimation(self.send_button_opacity_effect, b"opacity")
        self.send_button_opacity_animation.setDuration(400)
        self.send_button_opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.send_button_exit_animation = QPropertyAnimation(self.send_button, b"geometry")
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
            self.send_button.setFixedSize(btn_width , btn_width)
            self.send_button.setStyleSheet(self.send_button.styleSheet() + f"""
                QPushButton {{
                    border-radius: {btn_width // 2}px;
                }}
            """)
            self.send_button.setIconSize(self.send_button.size())

        super().showEvent(event)

    def on_return_pressed(self):
        self._result = self.input_field.text()
        self._start_exit_animation()
        self.input_field.clear()

    def _start_exit_animation(self):
        start_rect = self.geometry()
        end_rect = QRect(start_rect.x() + start_rect.width() // 2, 0, 0, 0)
        self.exit_animation.setStartValue(start_rect)
        self.exit_animation.setEndValue(end_rect)
        self.exit_animation.start()

        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.start()

        btn_start_rect = self.send_button.geometry()
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
        return self._result
