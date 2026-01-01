import re
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple

from neko_control import Controller


@dataclass(frozen=True)
class _ActionPattern:
    name: str
    regex: re.Pattern


class AgentParser:
    _MODE_LINE_RE = re.compile(r'^\s*\[(?:pro|basic|chat)\]\s*$', re.IGNORECASE)
    _CHAT_LINE_RE = re.compile(r'^\s*CHAT\s*$', re.IGNORECASE)

    def __init__(self):
        self.controller = Controller()

        # 数字：允许负数；允许 1. / .5 这种写法；限制为浮点
        num = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)'

        # 单行双引号字符串：支持 \" 与 \\ 等转义，不跨行
        dq_str = r'"((?:\\.|[^"\\])*)"'

        self._patterns = [
            _ActionPattern("msg", re.compile(r'^\s*Msg\s*-\s*(.+?)\s*$')),
            _ActionPattern("click", re.compile(rf'^\s*click\s+({num})\s+({num})(?:\s+(\d+))?\s*$')),
            _ActionPattern("drag", re.compile(rf'^\s*drag\s+({num})\s+({num})\s+({num})\s+({num})\s*$')),
            _ActionPattern("scroll", re.compile(rf'^\s*scroll\s+({num})\s+({num})\s+({num})\s*$')),
            _ActionPattern("input", re.compile(rf'^\s*input\s+{dq_str}\s+({num})\s+({num})\s*$')),
            _ActionPattern("exec", re.compile(rf'^\s*exec\s+{dq_str}\s*$')),
            _ActionPattern("popen", re.compile(rf'^\s*popen\s+{dq_str}\s*$')),
            _ActionPattern("file_read", re.compile(rf'^\s*file_read\s+{dq_str}\s*$')),
            _ActionPattern("file_write", re.compile(rf'^\s*file_write\s+{dq_str}\s+{dq_str}\s*$')),
            _ActionPattern("finished", re.compile(r'^\s*Act_Finished\s*$')),
            _ActionPattern("task_end", re.compile(r'^\s*Task_Finished\s*$')),
            _ActionPattern("pause", re.compile(r'^\s*Pause\s*$')),
        ]

        self._dispatch: Dict[str, Callable[[re.Match], Optional[str]]] = {
            "msg": self._do_msg,
            "click": self._do_click,
            "drag": self._do_drag,
            "scroll": self._do_scroll,
            "input": self._do_input,
            "exec": self._do_exec,
            "popen": self._do_popen,
            "file_read": self._do_file_read,
            "file_write": self._do_file_write,
            "finished": self._do_finished,
            "task_end": self._do_task_end,
            "pause": self._do_pause,
        }

    def _try_parse_line(self, line: str) -> Tuple[Optional[str], bool]:
        for ap in self._patterns:
            m = ap.regex.match(line)
            if not m:
                continue
            handler = self._dispatch.get(ap.name)
            if not handler:
                return None, True
            return handler(m), True
        return None, False

    def parse_and_execute(self, llm_output: str):
        if not llm_output:
            return None

        lines = llm_output.splitlines()

        # 先清理顶部的模式标记行（可出现多行）
        i = 0
        while i < len(lines) and self._MODE_LINE_RE.match(lines[i] or ""):
            i += 1

        # 仅当“第一条有效行”为 CHAT 时进入聊天模式
        j = i
        while j < len(lines) and not (lines[j] or "").strip():
            j += 1
        if j < len(lines) and self._CHAT_LINE_RE.match(lines[j] or ""):
            return "CHAT"

        # 逐行执行
        for idx in range(i, len(lines)):
            raw = lines[idx]
            line = (raw or "").strip()
            if not line:
                continue
            if self._MODE_LINE_RE.match(line):
                continue

            result, matched = self._try_parse_line(line)
            if matched:
                if result is not None:
                    return result
                continue

            # 未匹配：如果看起来像指令（以关键字开头）则报错；否则当作噪声跳过 这样可容忍 LLM 输出里的解释性文本，能及时发现指令拼写错误
            if re.match(r'^(Msg\b|click\b|input\b|exec\b|popen\b|drag\b|scroll\b|file_read\b|file_write\b|Act_Finished\b|Task_Finished\b|Pause\b)',
                        line):
                return f"ERROR_COMMAND:{line}"
            # 否则忽略（例如：模型的解释文字）
            continue

        return None

    # ----------------- handlers -----------------

    def _do_msg(self, m: re.Match) -> Optional[str]:
        print(m.group(1))
        return None

    def _do_click(self, m: re.Match) -> Optional[str]:
        x = float(m.group(1))
        y = float(m.group(2))
        times = int(m.group(3) or 1)
        self.controller.click(x, y, times)
        return None

    def _do_drag(self, m: re.Match) -> Optional[str]:
        x1, y1, x2, y2 = map(float, m.groups())
        self.controller.drag(x1, y1, x2, y2)
        return None

    def _do_scroll(self, m: re.Match) -> Optional[str]:
        x = float(m.group(1))
        y = float(m.group(2))
        scroll_amount = float(m.group(3))
        self.controller.scroll(scroll_amount, x, y)
        return None

    def _do_input(self, m: re.Match) -> Optional[str]:
        text = str(m.group(1))
        x = float(m.group(2))
        y = float(m.group(3))
        self.controller.type_string(text, x, y)
        return None

    def _do_exec(self, m: re.Match) -> Optional[str]:
        command = str(m.group(1))
        self.controller.exec(command)
        return None

    def _do_popen(self, m: re.Match) -> Optional[str]:
        command = str(m.group(1))
        self.controller.popen(command)
        return None

    def _do_file_read(self, m: re.Match) -> Optional[str]:
        file_path = str(m.group(1))
        self.controller.file_read(file_path)
        return None

    def _do_file_write(self, m: re.Match) -> Optional[str]:
        file_path = str(m.group(1))
        content = str(m.group(2))
        self.controller.file_write(file_path, content)
        return None

    def _do_finished(self, m: re.Match) -> Optional[str]:
        return "WAIT_FOR_NEXT_STEP"

    def _do_pause(self, m: re.Match) -> Optional[str]:
        return "Pause"

    def _do_task_end(self, m: re.Match) -> Optional[str]:
        return "TASK_COMPLETED"
