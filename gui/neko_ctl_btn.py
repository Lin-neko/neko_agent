import sys
from PyQt6.QtWidgets import QApplication, QPushButton, QWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer, QSize

class CancelButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(int(screen_geometry.width() * 0.45), 
                         int(screen_geometry.height() * 0.85),
                         int(screen_geometry.width() * 0.15),
                         int(screen_geometry.height() * 0.045))
        self.setText("终止")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 保存原始尺寸用于动画
        self.original_width = int(screen_geometry.width() * 0.1)
        self.original_height = int(screen_geometry.height() * 0.045)
        
        self.setStyleSheet("""
            QPushButton {
                border-radius: 17%;
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #ff5252, stop: 1 #b33939);
                color: white;
                font-size: 18px;
                font-weight: 500;
                border: none;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #ff6b6b, stop: 1 #ff5252);
            }
        """)
        
        self._opacity = 0.0
        self.fade_in_timer = QTimer(self)
        self.fade_in_timer.timeout.connect(self._update_opacity)
        self.fade_in_animation_step = 0
        
        self.click_animation = QPropertyAnimation(self, b"geometry")
        self.click_animation.setDuration(200)
        self.click_animation.setEasingCurve(QEasingCurve.Type.OutBack)
        self.clicked.connect(self.on_clicked)
        
        self.setWindowOpacity(0.0)

    def _update_opacity(self):
        self.fade_in_animation_step += 1
        self._opacity = self.fade_in_animation_step / 25.0  
        self.setWindowOpacity(self._opacity)
        if self._opacity >= 1.0:
            self.fade_in_timer.stop()

    def fade_in(self):
        self.show()
        self.fade_in_animation_step = 0
        self.fade_in_timer.start(10)

    def show_and_fade_in(self):
        QTimer.singleShot(100, self.fade_in)
        
    def on_clicked(self):
        self.click_animation.setStartValue(self.geometry())
        self.click_animation.setEndValue(QRect(int(self.x() + self.width() * 0.05) ,int(self.y() + self.height() * 0.05) ,int(self.width() * 0.9), int(self.height() * 0.9)))
        self.click_animation.finished.connect(self.restore_size)
        self.click_animation.start()
        
    def restore_size(self):
        self.click_animation.setDirection(QPropertyAnimation.Direction.Backward)
        self.click_animation.finished.disconnect()
        self.click_animation.finished.connect(self.reset_click_animation)
        self.click_animation.start()
        
    def reset_click_animation(self):
        self.click_animation.finished.disconnect()
        self.click_animation.setDirection(QPropertyAnimation.Direction.Forward)
        
    def initial_size(self):
        return QSize(self.original_width, self.original_height)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        
    @property
    def opacity(self):
        return self._opacity
        
    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.setWindowOpacity(value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    button = CancelButton()
    button.show_and_fade_in()
    sys.exit(app.exec())