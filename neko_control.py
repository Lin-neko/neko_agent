# control.py
import win32api
import win32con
import win32gui
import time
import subprocess


class Controller:
    def __init__(self):
        self.is_relative_mode = False 
    
    def click(self, x, y):
        global hwnd
        hwnd = win32gui.WindowFromPoint((x, y))
        if not hwnd:
            print(f"猫猫未找到坐标 ({x}, {y}) 下的窗口句柄喵...")
            return 1

        rect = win32gui.GetWindowRect(hwnd)
        win_x = x - rect[0]
        win_y = y - rect[1]

        print(f"猫猫向窗口句柄 {hex(hwnd)} 发送点击消息 (相对坐标: {win_x}, {win_y})")
        
        long_position = win32api.MAKELONG(win_x, win_y)
        
        try:
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)
            time.sleep(0.05)
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, long_position)
            return 0
        except Exception as e:
            print(f"发送消息点击失败惹: {e}")

    def type_string(self, text):
        for char in text:
            vk = ord(char)
            win32gui.PostMessage(hwnd, win32con.WM_CHAR, vk, 0)
        print(f"尝试向{hwnd}发送{text}")
    
    def exec(self,cmd):
        cmd_history = []
        exec_or_not = str(input(f"猫猫尝试运行命令{cmd},是否允许(y/n):"))
        if exec_or_not == "y":
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
        with open("cmd_history.txt","w",encoding='utf-8') as f :
            f.write(str(cmd_history))
            f.close()
        return result
    def popen(self,cmd):
        exec_or_not = str(input(f"猫猫尝试运行命令{cmd},是否允许(y/n):"))
        if exec_or_not == "y":
            subprocess.Popen(cmd)