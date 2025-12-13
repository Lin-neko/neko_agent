import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import base64
from io import BytesIO
from PIL import Image

class ScreenCapture:
    def __init__(self):
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)

    def grab_screen_base64(self):
        screen = self.app.primaryScreen()
        geometry = screen.geometry()
        pixmap = screen.grabWindow() 
        
        pil_img = Image.fromqimage(pixmap.toImage())
        if pil_img.mode in ('RGBA', 'LA', 'P'):
            pil_img = pil_img.convert('RGB')
        # 缩小截图节省token
        original_width, original_height = pil_img.size
        new_width = original_width // 2
        new_height = original_height // 2
        pil_img_resized = pil_img.resize((new_width, new_height), Image.LANCZOS)

        buffer = BytesIO()
        pil_img_resized.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

        print("喵喵获取了屏幕截图")
        return img_str, (new_width, new_height,original_width, original_height)
