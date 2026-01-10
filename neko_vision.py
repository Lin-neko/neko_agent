from PIL import ImageGrab
import base64
from io import BytesIO
from PIL import Image
from wechat_ocr.ocr_manager import OcrManager, OCR_MAX_TASK_ID
import json


class ScreenCapture:
    def __init__(self):
        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)
        self.magnification = int(config["neko_vision_settings"]["magnification"])
        try:
            img = ImageGrab.grab()
            self.original_width = img.width
            self.original_height = img.height
        except Exception as e:
            print(f"Error getting screen size: {e}")
    def grab_screen_base64(self, debug=0, log=True):
        pil_img = ImageGrab.grab()
        if pil_img.mode in ('RGBA', 'LA', 'P'):
            pil_img = pil_img.convert('RGB')
            
        # 缩小截图节省token
        new_width = int(pil_img.width / self.magnification)
        new_height = int(pil_img.height / self.magnification)
        pil_img_resized = pil_img.resize((new_width, new_height), Image.LANCZOS)
        buffer = BytesIO()
        pil_img_resized.save(buffer, format="JPEG", quality=95)
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        return img_str, (new_width, new_height, pil_img.width, pil_img.height)
    
    

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
            x = round(( int(primary_item['location']['left']) + int(primary_item['location']['right']) ) / 2 / self.original_width , 2)
            y = round(( int(primary_item['location']['top']) + int(primary_item['location']['bottom']) ) / 2 / self.original_height , 2)
            OCR_result.append({primary_item['text']: (x, y)})
        return OCR_result


#调试网格时使用
# a= ScreenCapture()
# a.grab_screen_base64(1)
# print(a.OCR())
