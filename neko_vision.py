import sys
from PyQt6.QtWidgets import QApplication
import base64
import json
from io import BytesIO
from PIL import Image, ImageDraw
from wechat_ocr.ocr_manager import OcrManager, OCR_MAX_TASK_ID


class ScreenCapture:
    def __init__(self):
        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
        self.line_color = "red" #网格线颜色
        self.line_width = int(config["neko_vision_settings"]["line_width"]) #网格线粗度
        self.divide = int(config["neko_vision_settings"]["divide"]) #x等分 划分越多 Agent可能越容易判断坐标 但是过多的划分反而容易出现误判
        self.magnification = int(config["neko_vision_settings"]["magnification"]) #缩小倍率 高分屏可以填大一点 节省 token
    def grab_screen_base64(self,debug=0,log=True):
        screen = self.app.primaryScreen()
        pixmap = screen.grabWindow() 
        
        pil_img = Image.fromqimage(pixmap.toImage())
        if pil_img.mode in ('RGBA', 'LA', 'P'):
            pil_img = pil_img.convert('RGB')
        pil_img.save(".\\cache\\OCR.jpg",format="JPEG")
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
        if log == True :
            print("喵喵获取了屏幕截图")
        return img_str, (new_width, new_height,original_width, original_height)
    
    

    def OCR(self) :
        def ocr_result_callback(img_path: str, results: dict):
            global result
            result = results
        ocr_manager = OcrManager(r'.\OCR')
        ocr_manager.SetExePath(r'.\OCR\WeChatOCR\WeChatOCR.exe')
        ocr_manager.SetUsrLibDir(r'.\OCR')
        ocr_manager.SetOcrResultCallback(ocr_result_callback)
        ocr_manager.StartWeChatOCR()
        print("正在调用OCR")
        ocr_manager.DoOCRTask(r'.\\cache\\OCR.jpg')
        while ocr_manager.m_task_id.qsize() != OCR_MAX_TASK_ID:
            pass
        ocr_manager.KillWeChatOCR()

        #格式化输出
        OCR_result = []
        for primary_item in result['ocrResult']:
            x = ( int(primary_item['location']['left']) + int(primary_item['location']['right']) ) / 2
            y = ( int(primary_item['location']['top']) + int(primary_item['location']['bottom']) ) / 2
            OCR_result.append({primary_item['text']: (x, y)})
        return OCR_result


#调试网格时使用
# a= ScreenCapture()
# a.grab_screen_base64(1)
# print(a.OCR())
