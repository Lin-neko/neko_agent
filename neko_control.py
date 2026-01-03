import sys
import os
import win32api
import win32con
import win32gui
import time
import subprocess
import ctypes
import sys
from PyQt6.QtWidgets import QApplication
from gui.neko_pms_ctl import NekoPMS

_APP = None

def add_log(log_string):
        with open("cache/log.txt", "a",encoding='utf-8') as f:
            f.write(log_string)
def get_display_scale_factor():
    user32 = ctypes.windll.user32
    desktop_window = user32.GetDesktopWindow()
    dpi = user32.GetDpiForWindow(desktop_window)
    scale_factor = dpi / 96.0
    return scale_factor
def Convert_pos(x, y):
    global _APP
    if QApplication.instance() is None:
        _APP = QApplication(sys.argv)
    else:
        _APP = QApplication.instance()

    screen = _APP.primaryScreen()
    if screen is None:
        raise RuntimeError("primaryScreen() is None")

    screen_geometry = screen.geometry()
    screen_width = screen_geometry.width()
    screen_height = screen_geometry.height()
    scale = get_display_scale_factor()
    return round(screen_width * x * scale, 2), round(screen_height * y * scale, 2)
class Controller:
    def __init__(self):
        self.pms_app = QApplication(sys.argv)
        self.pms = NekoPMS()
    def click(self, x, y,times):
        x , y = Convert_pos(x , y)
        hwnd = win32gui.WindowFromPoint((int(x), int(y)))
        if not hwnd:
            print(f"猫猫未找到坐标 ({x}, {y}) 下的窗口句柄喵...")
            return 1

        rect = win32gui.GetWindowRect(hwnd)
        win_x = int(x - rect[0])
        win_y = int(y - rect[1])
        add_log(f"猫猫向窗口句柄 {hex(hwnd)} 发送点击消息 (相对坐标: {win_x}, {win_y})")
        
        try:
            script_path = os.path.join(os.path.dirname(__file__), "gui","neko_click_indicator.py")
            python_exe = sys.executable if hasattr(sys, "executable") else "python"
            args = [python_exe, script_path, str(x / get_display_scale_factor() ), str(y / get_display_scale_factor() ), "500", "8"]
            try:
                subprocess.Popen(
                    args,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    close_fds=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                subprocess.Popen(
                    args,
                    close_fds=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except Exception as _e:
            print(f"点击可视化程序运行失败：{_e}")
        
        long_position = win32api.MAKELONG(win_x, win_y)
        time.sleep(0.3) #确保动画与点击操作同步
        try:
            for i in range(times):
                win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)
                time.sleep(0.05)
                win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, long_position)
            return 0
        except Exception as e:
            print(f"发送消息点击失败惹: {e}")

    
    
    def type_string(self, text,x,y):
        x , y = Convert_pos(x , y)
        hwnd = win32gui.WindowFromPoint((int(x), int(y)))
        if not hwnd:
            print(f"猫猫未找到坐标 ({x}, {y}) 下的窗口句柄喵...")
            return

        for char in text:
            if char == '\n':
                win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                time.sleep(0.05) # 短暂延迟
                win32gui.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
            else:
                vk = ord(char)
                win32gui.PostMessage(hwnd, win32con.WM_CHAR, vk, 0)
        add_log(f"尝试向{hwnd}发送{text}")
    
    
    def drag(self, current_x, current_y, new_x, new_y):
        current_x , current_y = Convert_pos(current_x , current_y)
        new_x , new_y = Convert_pos(new_x , new_y)
        hwnd = win32gui.WindowFromPoint((int(current_x), int(current_y)))
        if not hwnd:
            print(f"未找到坐标 ({current_x}, {current_y}) 下的窗口句柄喵...")
            return 1

        rect = win32gui.GetWindowRect(hwnd)
        start_win_x = current_x - rect[0]
        start_win_y = current_y - rect[1]
        
        end_win_x = new_x - rect[0]
        end_win_y = new_y - rect[1]

        add_log(f"向窗口句柄 {hex(hwnd)} 发送拖动消息")
        add_log(f"起始相对坐标: ({start_win_x}, {start_win_y}) -> 目标相对坐标: ({end_win_x}, {end_win_y})")

        try:
            script_path = os.path.join(os.path.dirname(__file__), "gui","neko_move_indicator.py")
            python_exe = sys.executable if hasattr(sys, "executable") else "python"
            args = [python_exe, script_path, str(current_x / get_display_scale_factor() ),
                    str(current_y / get_display_scale_factor() ),
                    str(new_x / get_display_scale_factor()),
                    str(new_y / get_display_scale_factor()),
                    "500", "8"]
            try:
                subprocess.Popen(
                    args,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    close_fds=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                subprocess.Popen(
                    args,
                    close_fds=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except Exception as _e:
            print(f"拖动可视化程序运行失败：{_e}")

        time.sleep(0.3) #确保动画与操作同步

        try:
            start_position = win32api.MAKELONG(int(start_win_x), int(start_win_y))
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, start_position)
            time.sleep(0.1)
            
            steps = 20
            for i in range(steps + 1):
                intermediate_x = start_win_x + (end_win_x - start_win_x) * i // steps
                intermediate_y = start_win_y + (end_win_y - start_win_y) * i // steps
                intermediate_position = win32api.MAKELONG(int(intermediate_x), int(intermediate_y))
                win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, intermediate_position)
                time.sleep(0.01)

            end_position = win32api.MAKELONG(int(end_win_x), int(end_win_y))
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, end_position)
            
            return 0

        except Exception as e:
            print(f"发送消息拖动失败惹: {e}")
            return 1
        

    def scroll(self ,scroll_amount, x, y):
        x , y = Convert_pos(x,y)
        null , scroll_amount = Convert_pos(x , scroll_amount)
        hwnd = win32gui.WindowFromPoint((int(x), int(y)))
        if hwnd == 0:
            print(f"未找到{x},{y}下的的窗口。")
            return 1
        lParam = win32api.MAKELONG(int(x), int(y))
        wParam = win32api.MAKELONG(0, int(scroll_amount))
        
        try:
            script_path = os.path.join(os.path.dirname(__file__), "gui","neko_move_indicator.py")
            python_exe = sys.executable if hasattr(sys, "executable") else "python"
            args = [python_exe, script_path, str(x / get_display_scale_factor() ),
                    str(y / get_display_scale_factor() ),
                    str(x / get_display_scale_factor()),
                    str((y + scroll_amount) / get_display_scale_factor()),
                    "500", "8"]
            try:
                subprocess.Popen(
                    args,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    close_fds=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                subprocess.Popen(
                    args,
                    close_fds=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except Exception as _e:
            print(f"滚动可视化程序运行失败：{_e}")

        time.sleep(0.3) #确保动画与操作同步
        
        win32api.PostMessage(hwnd, win32con.WM_MOUSEWHEEL, wParam, lParam)
        add_log(f"已向窗口 '{hwnd}' 发送鼠标滚轮滚动消息 (滚动量: {scroll_amount})。")
    def exec(self,cmd):
        cmd_history = []
        exec_or_not = self.pms.cmd_exec_check(cmd)
        if exec_or_not == "approved":
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                encoding='gbk'
            )
            cmd_history.append(f"{cmd}:{result}")
        else :
            cmd_history.append(f"{cmd}:refused")
        with open(".\\cache\\cmd_history.txt","w",encoding='utf-8') as f :
            f.write(str(cmd_history))
            f.close()
        return 0
    def popen(self,cmd):
        exec_or_not = self.pms.popen_check(cmd)
        if exec_or_not == "approved":
            subprocess.Popen(cmd,shell=True)
            return 0
        else :
            cmd_history = []
            cmd_history.append(f"{cmd}:refused")
            with open(".\\cache\\cmd_history.txt","w",encoding='utf-8') as f :
                f.write(str(cmd_history))
                f.close()
                return 1

    def file_write(self, file_path, content):
        write_or_not = self.pms.file_write_check(file_path)
        if write_or_not == 'approved' :
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    processed_content = content.replace('\\n', '\n')
                    f.write(processed_content)
                print(f"内容已成功写入文件: {file_path}")
                return 0
            except Exception as e:
                print(f"写入内容到文件失败惹: {e}")
                return 1
        else :
            return 1

    def file_read(self, file_path):
        read_or_not = self.pms.file_read_check(file_path)
        if read_or_not == "approved" : 
            try :
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(".\\cache\\file_read.txt","w",encoding='utf-8') as f :
                    f.write(str(content))
                    f.close()
            except FileNotFoundError:
                return "[system]no such a file"
            except Exception as e:
                return f"[system]Error:{e}"
        else :
            return "[system]permission denied"