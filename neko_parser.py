import re
from neko_control import Controller
class AgentParser:
    def __init__(self):
        self.controller = Controller()
        self.patterns = {
            'msg': re.compile(r'^Msg\s*-\s*(.+)$', re.MULTILINE),
            'click': re.compile(r'^click\s+([0-9]+),([0-9]+)$', re.MULTILINE),
            'input': re.compile(r'^input\s+"((?:.|\n)*?)"\s+([0-9]+),([0-9]+)$', re.MULTILINE),
            'exec': re.compile(r'^exec\s+"(.*)"$', re.MULTILINE),
            'popen': re.compile(r'^popen\s+"(.*)"$', re.MULTILINE),
            'finished': re.compile(r'^Act_Finished$', re.MULTILINE),
            'task_end': re.compile(r'^Task_Finished$', re.MULTILINE),
            'drag' : re.compile(r'^drag\s+([0-9]+),([0-9]+)\s+([0-9]+),([0-9]+)$', re.MULTILINE),
            'file_read': re.compile(r'^file_read\s+"(.*)"$', re.MULTILINE),
            'file_write': re.compile(r'^file_write\s+"((?:.|\n)*?)"\s+"((?:.|\n)*?)"$', re.MULTILINE),
            'scroll': re.compile(r'^scroll\s+([0-9]+),([0-9]+)\s+([0-9]+)$', re.MULTILINE),
        }

    def parse_and_execute(self, llm_output):
        remaining_output = llm_output.strip()

        if "[pro]" in remaining_output or "[basic]" in remaining_output or "[chat]" in remaining_output:
            return "WAIT_FOR_NEXT_STEP"
        if "CHAT" in remaining_output:
            return "CHAT"
        
        while remaining_output:
            matched = False
            for action_type, args in self.patterns.items():
                match = args.match(remaining_output)
                if match:
                    matched = True
                    # Execute the corresponding action
                    if action_type == 'msg':
                        content = match.group(1)
                        print(content)
                    elif action_type == 'click':
                        x, y = int(match.group(1)), int(match.group(2))
                        self.controller.click(x, y)
                    elif action_type == 'input':
                        text = match.group(1)
                        x = int(match.group(2))
                        y = int(match.group(3))
                        self.controller.type_string(text, x, y)
                    elif action_type == 'exec':
                        command = match.group(1)
                        self.controller.exec(command)
                    elif action_type == 'popen':
                        command = match.group(1)
                        self.controller.popen(command)
                    elif action_type == 'drag':
                        x1, y1, x2, y2 = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
                        self.controller.drag(x1, y1, x2, y2)
                    elif action_type == 'scroll':
                        x, y = int(match.group(1)), int(match.group(2))
                        scroll_amount = int(match.group(3))
                        self.controller.scroll(scroll_amount, x, y)
                    elif action_type == 'finished':
                        print("当前最小任务完成")
                        return "WAIT_FOR_NEXT_STEP"
                    elif action_type == 'task_end':
                        print("整个任务已彻底完成。")
                        return "TASK_COMPLETED"
                    elif action_type == 'file_read':
                        file_path = match.group(1)
                        content = self.controller.file_read(file_path)
                    elif action_type == 'file_write':
                        file_path = match.group(1)
                        content = match.group(2)
                        self.controller.file_write(file_path, content)
                        
                    
                    remaining_output = remaining_output[match.end():].strip()
                    break 
            
            if not matched:
                return f"ERROR_COMMAND:{remaining_output.splitlines()[0]}"
        
        return 1
