import sys
from PyQt6.QtWidgets import QApplication, QPushButton, QWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer, QSize
from PyQt6.QtGui import QPainter, QColor

class CancelButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(int(screen_geometry.width() * 0.5 -screen_geometry.width() * 0.15 // 2), 
                         int(screen_geometry.height() * 0.85),
                         int(screen_geometry.width() * 0.15),
                         int(screen_geometry.height() * 0.045))
        self.setText("  终止") # 添加两个空格为图标留出空间
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 保存原始尺寸用于动画
        self.original_width = int(screen_geometry.width() * 0.1)
        self.original_height = int(screen_geometry.height() * 0.045)
        
        self.setStyleSheet("""
            QPushButton {
                border-radius: 12px;
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6c5ce7, stop: 1 #a29bfe);
                color: white;
                font-size: 18px;
                font-weight: 500;
                border: none;
                padding: 10px 20px 10px 40px; /* 增加左侧内边距为图标留出空间 */
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #8e7dff, stop: 1 #c0baff);
            }
            QPushButton:pressed {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #5a4acb, stop: 1 #8e7dff);
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
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 设置图标颜色 (与文本颜色一致)
        painter.setBrush(QColor("white"))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # 计算图标位置和大小
        icon_size = self.height() * 0.4 # 图标大小为按钮高度的40%
        icon_x = self.width() * 0.1 # 距离左侧10%
        icon_y = (self.height() - icon_size) / 2 # 垂直居中
        
        # 绘制圆角矩形 (停止图标)
        painter.drawRoundedRect(int(icon_x), int(icon_y), int(icon_size), int(icon_size), 3, 3)
        
        painter.end()
        
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
