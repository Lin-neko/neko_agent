from PIL import ImageGrab

def dark_or_light(x, y, threshold = 128):
    try:
        screenshot = ImageGrab.grab()
        pixel_color = screenshot.getpixel((x, y))
    except Exception as e:
        print(f"huh?获取像素过程似乎出了点问题哦: {e}")              
    # 计算亮度 
    luminance = (0.299 * pixel_color[0] + 0.587 * pixel_color[1] + 0.114 * pixel_color[2])
    if luminance < threshold :
        return "Light"
    else :
        return "Dark"
