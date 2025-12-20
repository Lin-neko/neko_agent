import sys
import traceback

def main():
    try:
        from PyQt6.QtWidgets import QApplication, QWidget
        from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
        from PyQt6.QtGui import QPainter, QColor, QBrush, QScreen, QGuiApplication
    except Exception as e:
        print(f"pyqy6未安装或其他错误: {e}", file=sys.stderr)
        return 1

    class Indicator(QWidget):
        def __init__(self, x, y, radius=8, duration=400, target_opacity=0.6):
            flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
            super().__init__(None, flags)
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.radius = int(radius)
            diameter = self.radius * 2
            self.resize(diameter, diameter)
            self.x = int(x)
            self.y = int(y)
            self.move(self.x - self.radius, self.y - self.radius)

            self.duration = int(duration)
            self.target_opacity = float(target_opacity)
            self.setWindowOpacity(0.0)

            fade_ms = max(50, self.duration // 4)
            visible_ms = max(0, self.duration - fade_ms * 2)

            self.fade_in = QPropertyAnimation(self, b"windowOpacity")
            self.fade_in.setDuration(fade_ms)
            self.fade_in.setStartValue(0.0)
            self.fade_in.setEndValue(self.target_opacity)
            self.fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)

            self.fade_out = QPropertyAnimation(self, b"windowOpacity")
            self.fade_out.setDuration(fade_ms)
            self.fade_out.setStartValue(self.target_opacity)
            self.fade_out.setEndValue(0.0)
            self.fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.fade_out.finished.connect(self.close)
            self.fade_out.finished.connect(QApplication.instance().quit) # 动画结束后强制退出应用


            QTimer.singleShot(0, self.fade_in.start)
            total_until_fade_out = fade_ms + visible_ms
            QTimer.singleShot(total_until_fade_out, self.fade_out.start)

        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # 获取屏幕像素颜色
            screen = QGuiApplication.primaryScreen()
            if screen:
                pixmap = screen.grabWindow(0, self.x, self.y, 1, 1)
                if not pixmap.isNull():
                    image = pixmap.toImage()
                    if not image.isNull():
                        pixel_color = QColor(image.pixel(0, 0))
                        # 根据亮度决定圆点颜色
                        # 计算亮度 (L = 0.299*R + 0.587*G + 0.114*B)
                        luminance = (0.299 * pixel_color.red() +
                                     0.587 * pixel_color.green() +
                                     0.114 * pixel_color.blue()) / 255
                        if luminance > 0.5:  # 亮色背景
                            dot_color = QColor(0, 0, 0, 255)  # 黑色
                        else:  # 暗色背景
                            dot_color = QColor(255, 255, 255, 255)  # 白色
                    else:
                        dot_color = QColor(255, 255, 255, 255) # 默认白色
                else:
                    dot_color = QColor(255, 255, 255, 255) # 默认白色
            else:
                dot_color = QColor(255, 255, 255, 255) # 默认白色

            brush = QBrush(dot_color)
            painter.setBrush(brush)
            painter.setPen(Qt.PenStyle.NoPen)
            diameter = self.radius * 2
            painter.drawEllipse(0, 0, diameter, diameter)

    try:
        app = QApplication(sys.argv)
        if len(sys.argv) < 3:
            print("[neko_click_indicator] Usage: neko_click_indicator.py X Y [duration_ms] [radius_px] [target_opacity]", file=sys.stderr)
            return 1
        x = float(sys.argv[1])
        y = float(sys.argv[2])
        duration = int(sys.argv[3]) if len(sys.argv) > 3 else 400
        radius = int(sys.argv[4]) if len(sys.argv) > 4 else 8
        target_opacity = float(sys.argv[5]) if len(sys.argv) > 5 else 0.6

        w = Indicator(x, y, radius=radius, duration=duration, target_opacity=target_opacity)
        w.show()
        app.exec()
        return 0
    except Exception:
        traceback.print_exc(file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
