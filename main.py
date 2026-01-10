from Nkernel import NekoAgentKernel
from gui.launcher.input_box_launcher import start_input_box
import sys
import subprocess
import threading
import os
import time

def add_log(log_string):
    with open("cache/log.txt", "a",encoding='utf-8') as f:
        f.write(log_string)

def launch_log():
    script = os.path.join(os.path.dirname(__file__), "gui" , "launcher", "log_window_launcher.py")
    return subprocess.Popen([sys.executable, script])

def monitor_chat_mode(log_proc):
    while True:
        if os.path.exists(".\\cache\\chat_mode.lock"):
            log_proc.terminate()
            break
        time.sleep(1)

if __name__ == '__main__':
    log_proc = launch_log()
    kernel = NekoAgentKernel()

    chat_mode_thread = threading.Thread(target=monitor_chat_mode, args=(log_proc,))
    chat_mode_thread.daemon = True 
    chat_mode_thread.start()

    try:
        while True:
            command = start_input_box(0)
            if command :
                result = kernel.main_loop(command)
                if result:
                    if result == "PAUSE_REQUESTED":
                        input("任务已暂停，按回车继续...")
                        continue

            more_commands = input("追加更多命令? (y/n): ").strip().lower()
            if more_commands != 'y':
                log_proc.terminate()
                break
            else:
                kernel.feedback = ''
                
    except Exception as e:
        print(f"程序出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print(f'任务完成,共计{kernel.runtime}步')
