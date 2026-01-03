from multiprocessing import Process, Queue

def _worker(task_data, result_queue):
    try:
        from neko_parser import AgentParser
        
        parser = AgentParser()
        result = parser.parse_and_execute(task_data)
        result_queue.put(("success", result))
    except Exception as e:
        import traceback
        result_queue.put(("error", str(e) + "\n" + traceback.format_exc()))

def run_parser_safe(task_data, timeout=15):
    result_queue = Queue()
    p = Process(target=_worker, args=(task_data, result_queue))
    p.start()
    p.join(timeout=timeout)
    
    if p.is_alive():
        p.terminate()
        p.join()
        raise TimeoutError("Controller 操作超时")
    
    if result_queue.empty():
        raise RuntimeError("Controller 子进程无返回")
    
    status, data = result_queue.get()
    if status == "error":
        raise RuntimeError(f"Controller 失败: {data}")
    return data