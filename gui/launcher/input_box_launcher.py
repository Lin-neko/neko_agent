import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from multiprocessing import Process, Queue
import time


def _worker(mode, result_queue):
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        from gui.neko_input_box import InputBox
        inputbox = InputBox()
        if mode == 0:
            inputbox.set_mode("normal")
            result = inputbox.get_content()
        else:
            inputbox.set_mode("chat")
            result = inputbox.get_content()
        result_queue.put(("success", result))
    except Exception as e:
        import traceback
        error_message = str(e) + "\n" + traceback.format_exc()
        result_queue.put(("error", error_message))
    finally:
        result_queue.close()

def start_input_box(mode):
    result_queue = Queue()
    p = Process(target=_worker, args=(mode, result_queue))
    p.start()

    time.sleep(1)

    try:
        status, data = result_queue.get() 
        if status == "error":
            raise RuntimeError(f"InputBox 失败: {data}")
        return data
    except Exception as e:
        raise RuntimeError(f"InputBox 失败: {str(e)}")
    finally:
        p.join() 
        result_queue.close() 
