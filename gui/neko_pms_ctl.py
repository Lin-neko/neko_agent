from PyQt6.QtWidgets import QTextEdit, QApplication , QPushButton, QLabel
from PyQt6.QtCore import Qt, QRect, QEventLoop, QPropertyAnimation
from PyQt6.QtGui import QPixmap, QRegion
import sys
from gui.dark_mode_manager import dark_or_light

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

        self.result = None
        self.loop = None
        self.approve_btn.clicked.connect(self.on_approve)
        self.reject_btn.clicked.connect(self.on_reject)

    def on_approve(self):
        self.result = "approved"
        if self.loop:
            self.loop.quit()

    def on_reject(self):
        self.result = "rejected"
        if self.loop:
            self.loop.quit()

    def _hide_all_icons(self):
        self.cmd_icon.hide()
        self.file_icon.hide()
        self.file_edit_icon.hide()
        self.popen_icon.hide()

    def _update_style_based_on_background(self):
        """根据屏幕背景亮度更新样式表"""
        # 获取窗口中心坐标
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
            approve_bg = "#e0e0e0"
            approve_text = "#333333"
            approve_hover = "#d0d0d0"
            approve_pressed = "#c0c0c0"
            reject_bg = "#f0f0f0"
            reject_text = "#666666"
            reject_hover = "#e0e0e0"
            reject_pressed = "#d0d0d0"
        else:
            # 深色主题（保持原有深色样式）
            text_color = "#abb2bf"
            bg_color = "#282c34"
            border_color = "#3e4452"
            scrollbar_bg = "#282c34"
            scrollbar_handle = "#4b5263"
            approve_bg = "#abb2bf"
            approve_text = "#3e4452"
            approve_hover = "#787d86"
            approve_pressed = "#282c34"
            reject_bg = "#3e4452"
            reject_text = "#abb2bf"
            reject_hover = "#4b5263"
            reject_pressed = "#282c34"
        
        # 更新主窗口样式
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg_color};
                color: {text_color};
                font-family: "Cascadia Code", "Consolas", "Monaco", "Courier New", monospace;
                font-size: 10pt;
                border: 1px solid {border_color};
                border-radius: 5px;
                padding: 5px;
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
        
        # 更新按钮样式
        self.approve_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {approve_bg};
                color: {approve_text};
                font-family: "Cascadia Code", "Consolas", "Monaco", "Courier New", monospace;
                border: 1px solid {border_color};
                border-radius: 10px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {approve_hover};
            }}
            QPushButton:pressed {{
                background-color: {approve_pressed};
            }}
        """)
        
        self.reject_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {reject_bg};
                color: {reject_text};
                font-family: "Cascadia Code", "Consolas", "Monaco", "Courier New", monospace;
                border: 1px solid {border_color};
                border-radius: 10px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {reject_hover};
            }}
            QPushButton:pressed {{
                background-color: {reject_pressed};
            }}
        """)
        
        # 更新标签样式
        self.label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-family: "Cascadia Code", "Consolas", "Monaco", "Courier New", monospace;
                font-size: 10pt;
            }}
        """)

    def _wait_for_decision(self):
        self.setWindowOpacity(0.0)
        # 在显示前更新样式
        self._update_style_based_on_background()
        self.show()
        
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)  # 300ms 渐显
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()

        self.loop = QEventLoop()
        self.loop.exec()

        # 渐隐效果
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(300)  # 300ms 渐隐
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.finished.connect(self.hide)
        self.fade_out.start()

        fade_loop = QEventLoop()
        self.fade_out.finished.connect(fade_loop.quit)
        fade_loop.exec()

        self._hide_all_icons()
        return self.result

    def setRoundedCorners(self):
        """设置窗口圆角"""
        radius = 5
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
        """重写resizeEvent以在窗口大小改变时更新圆角"""
        super().resizeEvent(event)
        self.setRoundedCorners()

    def cmd_exec_check(self, cmd):
        self.cmd_icon.show()
        self.label.setText(f"Neko尝试运行命令\n{cmd}\n是否允许?")
        return self._wait_for_decision()
    
    def popen_check(self, cmd):
        self.popen_icon.show()
        self.label.setText(f'Neko尝试在后台运行命令\n{cmd}\n是否允许?')
        return self._wait_for_decision()

    def file_read_check(self, file_path):
        self.file_icon.show()
        self.label.setText(f"Neko尝试读取文件\n{file_path}\n是否允许")
        return self._wait_for_decision()
    
    def file_write_check(self, file_path):
        self.file_edit_icon.show()
        self.label.setText(f"Neko尝试写入文件\n{file_path}\n是否允许")
        return self._wait_for_decision()
