import sys
import os
import time
import threading
import subprocess
import keyboard
from Nkernel import NekoAgentKernel
from gui.launcher.input_box_launcher import start_input_box
from gui.msgbox import ask_yes_no, show_message


log_proc = None
chat_proc = None
try:
    if os.path.exists(".\\cache\\chat_mode.lock"):
        os.remove(".\\cache\\chat_mode.lock")
except Exception as e:
    print(e)
script = os.path.join(os.path.dirname(__file__), "emergency_exit.py")
subprocess.Popen([sys.executable, script])

def win_space_listener():
    keyboard.add_hotkey('win+space', main)
    keyboard.wait() 

def ctl_f1_listener():
    keyboard.add_hotkey('ctrl+f1', launch_setting)
    keyboard.wait()

def launch_log():
    script = os.path.join(os.path.dirname(__file__), "gui", "launcher", "log_window_launcher.py")
    return subprocess.Popen([sys.executable, script])

def launch_setting():
    script = os.path.join(os.path.dirname(__file__), "gui", "launcher", "setting_launcher.py")
    return subprocess.Popen([sys.executable, script])
def launch_chat():
    script = os.path.join(os.path.dirname(__file__), "gui", "launcher", "chat_window_launcher.py")
    return subprocess.Popen([sys.executable, script])

def safe_terminate(proc):
    if proc and proc.poll() is None:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
        except Exception as e:
            print(e)

def monitor_chat_mode(log_process):
    while True:
        if os.path.exists(os.path.join("cache", "chat_mode.lock")):
            log_process.terminate()
            global chat_proc
            chat_proc = launch_chat()
            break

def main():
    global log_proc, chat_proc
    
    if log_proc is None or log_proc.poll() is not None:
        if log_proc:
            safe_terminate(log_proc)
        log_proc = launch_log()
    monitor_thread = threading.Thread(
        target=monitor_chat_mode,
        args=(log_proc,),
        daemon=True
    )
    monitor_thread.start()
    try:
        kernel = NekoAgentKernel()
        while True:
            command = start_input_box(0)
            if log_proc is None or log_proc.poll() is not None:
                 if log_proc:
                     safe_terminate(log_proc)
                 log_proc = launch_log()
            if command:
                result = kernel.main_loop(command)
                if result == "PAUSE_REQUESTED":
                    show_message("Neko已暂停", "按下确认任务将继续进行")
            if chat_proc:
                    safe_terminate(chat_proc)
            if not ask_yes_no("NekoAgent", "是否追加更多命令?"):
                if log_proc:
                     safe_terminate(log_proc)
                if chat_proc:
                    safe_terminate(chat_proc)
                break
                
            else :
                kernel.feedback = ""

    except Exception as e:
        show_message("Neko错误", f"程序出错: {str(e)}")


if __name__ == '__main__':
    show_message("Neko提示","按下确定后Neko将启动\n启动后f1+f2紧急终止\nctl+f1打开配置面板\nwin+空格开始使用")
    win_space_thread = threading.Thread(target=win_space_listener, daemon=True)
    win_space_thread.start()
    ctl_f1_thread = threading.Thread(target=ctl_f1_listener, daemon=True)
    ctl_f1_thread.start()


    print("程序已启动，监听 Win + Space ...")
    try:
        while True:
            time.sleep(1) # 防止主线程占用过多CPU
    except KeyboardInterrupt:
        print("\n接收到中断信号，正在退出...")
        os._exit(0)
