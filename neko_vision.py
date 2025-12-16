import sys
from PyQt6.QtWidgets import QApplication
import base64
from io import BytesIO
from PIL import Image, ImageDraw

class ScreenCapture:
    def __init__(self):
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        self.line_color = "red" #网格线颜色
        self.line_width = 1 #网格线粗度
        self.divide = 16 #x等分 划分越多 Agent可能越容易判断坐标 但是过多的划分反而容易出现误判
        self.magnification = 3 #缩小倍率 高分屏可以填大一点 节省 token
    def grab_screen_base64(self,debug=0):
        screen = self.app.primaryScreen()
        pixmap = screen.grabWindow() 
        
        pil_img = Image.fromqimage(pixmap.toImage())
        if pil_img.mode in ('RGBA', 'LA', 'P'):
            pil_img = pil_img.convert('RGB')
        # 缩小截图节省token
        original_width, original_height = pil_img.size
        new_width = int(original_width // self.magnification)
        new_height = int(original_height // self.magnification)
        pil_img_resized = pil_img.resize((new_width, new_height), Image.LANCZOS)

        # 绘制网格线方便AI定位坐标
        self.x_interval = int(new_width / self.divide)
        self.y_interval = int(new_height / self.divide)
        draw = ImageDraw.Draw(pil_img_resized)      
        for x in range(self.x_interval, new_width, self.x_interval):
            draw.line([(x, 0), (x, new_height)], fill=self.line_color, width=self.line_width)

        for y in range(self.y_interval, new_height, self.y_interval):
            draw.line([(0, y), (new_width, y)], fill=self.line_color, width=self.line_width)

        buffer = BytesIO()
        pil_img_resized.save(buffer, format="JPEG", quality=95) # 增加 quality 防止压缩过度导致线条模糊
        if debug == 1 :
            pil_img_resized.save("screenshot.jpg",format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

        print("喵喵获取了屏幕截图")
        return img_str, (new_width, new_height,original_width, original_height)

#调试网格时使用
# a= ScreenCapture()
# a.grab_screen_base64(1)