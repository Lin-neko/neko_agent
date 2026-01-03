from Nkernel import NekoAgentKernel
import sys
import subprocess
import os
def add_log(log_string):
    with open("cache/log.txt", "a",encoding='utf-8') as f:
        f.write(log_string)

def launch_log():
    script = os.path.join(os.path.dirname(__file__), "gui" , "launcher", "log_window_launcher.py")
    return subprocess.Popen([sys.executable, script])

if __name__ == '__main__':
    log_proc = launch_log()
    a = NekoAgentKernel()
    try:
        while True:
            command = input("给neko下达命令:")
            result = a.main_loop(command)
            
            if result == "PAUSE_REQUESTED":
                input("任务已暂停，按回车继续...")
                continue

            more_commands = input("追加更多命令? (y/n): ").strip().lower()
            if more_commands != 'y':
                break
            else:
                a.feedback = ''
                
    except Exception as e:
        print(f"程序出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print(f'任务完成,共计{a.runtime}步')
