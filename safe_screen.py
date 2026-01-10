from multiprocessing import Process, Queue
import time

def _screenshot_worker(result_queue: Queue):
    try:
        from neko_vision import ScreenCapture
        screen = ScreenCapture()
        image64 = screen.grab_screen_base64()[0]
        result_queue.put(("success", image64))
    except Exception as e:
        print(e)

def _ocr_worker(result_queue: Queue):
    try:
        from neko_vision import ScreenCapture
        screen = ScreenCapture()
        ocr_result = screen.OCR()
        result_queue.put(("success", ocr_result))
    except Exception as e:
        import traceback
        result_queue.put(("error", str(e) + "\n" + traceback.format_exc()))


def _run_in_subprocess(worker_func, timeout: int = 15, operation_name: str = "操作"):
    """
    改进的子进程执行器，先获取结果再等待进程结束
    """
    result_queue = Queue()
    p = Process(target=worker_func, args=(result_queue,))
    p.start()
    
    try:
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not result_queue.empty():
                status, data = result_queue.get()
                if status == "error":
                    raise RuntimeError(f"{operation_name}失败: {data}")
                p.join(timeout=1)
                if p.is_alive():
                    p.terminate()
                    p.join()
                return data
            time.sleep(0.1)  # 避免CPU空转
        
        # 超时处理
        if p.is_alive():
            p.terminate()
            p.join()
        if not result_queue.empty():
            status, data = result_queue.get()
            if status == "error":
                raise RuntimeError(f"{operation_name}失败: {data}")
        raise TimeoutError(f"{operation_name}超时（>{timeout}秒）")
        
    except Exception as e:
        if p.is_alive():
            p.terminate()
            p.join()
        raise
    finally:
        # 确保队列被清理
        while not result_queue.empty():
            try:
                result_queue.get_nowait()
            except:
                break


def take_screenshot_safe(timeout: int = 10) -> str:
    """安全截图，返回 base64 字符串"""
    return _run_in_subprocess(_screenshot_worker, timeout=timeout, operation_name="屏幕截图")


def perform_ocr_safe(timeout: int = 20) -> list:
    """安全 OCR，返回 OCR 结果（列表类型）"""
    return _run_in_subprocess(_ocr_worker, timeout=timeout, operation_name="OCR 识别")