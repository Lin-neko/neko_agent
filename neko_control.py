import win32api
import win32con
import win32gui
import time
import subprocess


class Controller:
    def click(self, x, y):
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

    def type_string(self, text,x,y):
        hwnd = win32gui.WindowFromPoint((x, y))
        for char in text:
            vk = ord(char)
            win32gui.PostMessage(hwnd, win32con.WM_CHAR, vk, 0)
        print(f"尝试向{hwnd}发送{text}")
    
    
    def drag(self, current_x, current_y, new_x, new_y):
        hwnd = win32gui.WindowFromPoint((current_x, current_y))
        if not hwnd:
            print(f"未找到坐标 ({current_x}, {current_y}) 下的窗口句柄喵...")
            return 1

        rect = win32gui.GetWindowRect(hwnd)
        start_win_x = current_x - rect[0]
        start_win_y = current_y - rect[1]
        
        end_win_x = new_x - rect[0]
        end_win_y = new_y - rect[1]

        print(f"向窗口句柄 {hex(hwnd)} 发送拖动消息")
        print(f"起始相对坐标: ({start_win_x}, {start_win_y}) -> 目标相对坐标: ({end_win_x}, {end_win_y})")

        try:
            start_position = win32api.MAKELONG(start_win_x, start_win_y)
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, start_position)
            time.sleep(0.1)
            
            steps = 20
            for i in range(steps + 1):
                intermediate_x = start_win_x + (end_win_x - start_win_x) * i // steps
                intermediate_y = start_win_y + (end_win_y - start_win_y) * i // steps
                intermediate_position = win32api.MAKELONG(intermediate_x, intermediate_y)
                win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, intermediate_position)
                time.sleep(0.01)

            end_position = win32api.MAKELONG(end_win_x, end_win_y)
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, end_position)
            
            return 0

        except Exception as e:
            print(f"发送消息拖动失败惹: {e}")
            return 1
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
        return 0
    def popen(self,cmd):
        exec_or_not = str(input(f"猫猫尝试在后台运行命令{cmd},是否允许(y/n):"))
        if exec_or_not == "y":
            subprocess.Popen(cmd,shell=True)
            return 0
        else :
            cmd_history = []
            cmd_history.append(f"{cmd}:refused")
            with open("cmd_history.txt","w",encoding='utf-8') as f :
                f.write(str(cmd_history))
                f.close()
                return 1