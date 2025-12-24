import sys
import traceback

def main():
    try:
        from PyQt6.QtWidgets import QApplication, QWidget
        from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
        from PyQt6.QtGui import QPainter, QColor, QBrush, QScreen, QGuiApplication
    except Exception as e:
        print(f"pyqt6未安装或其他错误: {e}", file=sys.stderr)
        return 1

    class MoveIndicator(QWidget):
        def __init__(self, x1, y1, x2, y2, radius=8, duration=1000, target_opacity=0.6):
            flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
            super().__init__(None, flags)
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.radius = int(radius)
            diameter = self.radius * 2
            self.resize(diameter, diameter)

            self.start_pos = QPoint(int(x1) - self.radius, int(y1) - self.radius)
            self.end_pos = QPoint(int(x2) - self.radius, int(y2) - self.radius)
            self.move(self.start_pos)

            self.duration = int(duration)
            self.target_opacity = float(target_opacity)
            self.setWindowOpacity(0.0)

            # 动画路径
            self.pos_animation = QPropertyAnimation(self, b"pos")
            self.pos_animation.setDuration(self.duration)
            self.pos_animation.setStartValue(self.start_pos)
            self.pos_animation.setEndValue(self.end_pos)
            self.pos_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

            # 淡入动画
            self.fade_in = QPropertyAnimation(self, b"windowOpacity")
            self.fade_in.setDuration(200) # 淡入时间
            self.fade_in.setStartValue(0.0)
            self.fade_in.setEndValue(self.target_opacity)
            self.fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)

            # 淡出动画
            self.fade_out = QPropertyAnimation(self, b"windowOpacity")
            self.fade_out.setDuration(200) # 淡出时间
            self.fade_out.setStartValue(self.target_opacity)
            self.fade_out.setEndValue(0.0)
            self.fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.fade_out.finished.connect(self.close)
            self.fade_out.finished.connect(QApplication.instance().quit)

            # 启动动画序列
            self.fade_in.finished.connect(self.pos_animation.start)
            self.pos_animation.finished.connect(self.fade_out.start)
            QTimer.singleShot(0, self.fade_in.start)

        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # 获取当前位置的屏幕像素颜色
            current_x = self.pos().x() + self.radius
            current_y = self.pos().y() + self.radius

            screen = QGuiApplication.primaryScreen()
            if screen:
                pixmap = screen.grabWindow(0, current_x, current_y, 1, 1)
                if not pixmap.isNull():
                    image = pixmap.toImage()
                    if not image.isNull():
                        pixel_color = QColor(image.pixel(0, 0))
                        luminance = (0.299 * pixel_color.red() +
                                     0.587 * pixel_color.green() +
                                     0.114 * pixel_color.blue()) / 255
                        if luminance > 0.5:
                            dot_color = QColor(0, 0, 0, 255)
                        else:
                            dot_color = QColor(255, 255, 255, 255)
                    else:
                        dot_color = QColor(255, 255, 255, 255)
                else:
                    dot_color = QColor(255, 255, 255, 255)
            else:
                dot_color = QColor(255, 255, 255, 255)

            brush = QBrush(dot_color)
            painter.setBrush(brush)
            painter.setPen(Qt.PenStyle.NoPen)
            diameter = self.radius * 2
            painter.drawEllipse(0, 0, diameter, diameter)

    try:
        app = QApplication(sys.argv)
        if len(sys.argv) < 5:
            print("[neko_move_indicator] Usage: neko_move_indicator.py X1 Y1 X2 Y2 [duration_ms] [radius_px] [target_opacity]", file=sys.stderr)
            return 1
        x1 = float(sys.argv[1])
        y1 = float(sys.argv[2])
        x2 = float(sys.argv[3])
        y2 = float(sys.argv[4])
        duration = int(sys.argv[5]) if len(sys.argv) > 5 else 1000
        radius = int(sys.argv[6]) if len(sys.argv) > 6 else 8
        target_opacity = float(sys.argv[7]) if len(sys.argv) > 7 else 0.6

        w = MoveIndicator(x1, y1, x2, y2, radius=radius, duration=duration, target_opacity=target_opacity)
        w.show()
        app.exec()
        return 0
    except Exception:
        traceback.print_exc(file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
