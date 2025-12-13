import re
from neko_control import Controller
class AgentParser:
    def __init__(self):
        self.controller = Controller()
        self.patterns = {
            'msg': re.compile(r'^Msg\s*-\s*(.+)$'),
            'click': re.compile(r'^click\s+([0-9]+),([0-9]+)$'),
            'input': re.compile(r'^input\s+"(.*)"$'),
            'exec': re.compile(r'^exec\s+"(.*)"$'),
            'popen': re.compile(r'^popen\s+"(.*)"$'),
            'finished': re.compile(r'^Act_Finished$'),
            'task_end': re.compile(r'^Task_Finished$')
        }

    def parse_and_execute(self, llm_output):
        lines = llm_output.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 处理 Msg
            if self.patterns['msg'].match(line):
                match = self.patterns['msg'].match(line)
                content = match.group(1)
                print(f"Msg: {content}")

            # 处理 click
            elif self.patterns['click'].match(line):
                match = self.patterns['click'].match(line)
                x, y = int(match.group(1)), int(match.group(2))
                self.controller.click(x, y)

            # 处理 input
            elif self.patterns['input'].match(line):
                match = self.patterns['input'].match(line)
                text = match.group(1)
                self.controller.type_string(text)

            # 处理 exec
            elif self.patterns['exec'].match(line):
                match = self.patterns['exec'].match(line)
                command = match.group(1)
                self.controller.exec(command)
            
            #处理popen
            elif self.patterns['popen'].match(line):
                match = self.patterns['popen'].match(line)
                command = match.group(1)
                self.controller.popen(command)

            # 处理 Act_Finished
            elif self.patterns['finished'].match(line):
                print("当前小任务完成")
                return "WAIT_FOR_NEXT_STEP" # 返回状态，通知主循环暂停

            # 6. 处理 Task_Finished
            elif self.patterns['task_end'].match(line):
                print("整个任务已彻底完成。")
                return "TASK_COMPLETED"

            else:
                print(f"警告: 无法解析的指令 '{line}'")

