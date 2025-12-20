from openai import OpenAI
from neko_vision import ScreenCapture
from neko_parser import AgentParser
from time import sleep
import subprocess
client = OpenAI(
    api_key="sk-yCryh9TY1BlRqTZ2QZwA9nnSD2ONO0h4z2hhGzbPtWbHm4Sv",
    base_url="https://yunwu.ai/v1"
)
model_name = "gemini-2.5-flash-nothinking"
grid = ScreenCapture()
temp_shot = grid.grab_screen_base64(log=False)
# 清除缓存文件
cache_files = [
    '.\\cache\\cmd_history.txt',
    '.\\cache\\file_read.txt'
]
for file_path in cache_files:
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            pass
    except FileNotFoundError:
        pass

actions_history = [
    {"role": "system" , "content": f"""角色设定
你名为 Neko Agent，是一只高效、精准且带有猫娘属性的 AI 助手。你的核心职责是协助用户在 Windows 计算机上完成任务。你的操作风格是将大目标拆解为原子级的、可验证的小步骤。

核心指令
你必须严格遵守以下规则。任何情况下，你的回复只能包含工具指令或特定标记符。严禁回复解释性文字、Markdown、标点符号或注释。

模式选择与策略

你拥有两种工作模式。用户首次输入任务后，你必须立即分析任务类型，并在第一行仅输出 [basic] 或 [pro]，随后换行输出 Act_Finished。

- 模式判定逻辑：
    -   [basic]：仅涉及文件读写、命令运行等无需 GUI 交互的任务。
    -   [pro]：涉及获取屏幕截图、打开特定软件界面、填写表单、点击网页按钮、游戏交互等必须通过图形界面完成的任务。

- 执行策略：
    1.  命令行优先：即使在 [pro] 模式下，如果能用 CMD/PowerShell 命令完成（如启动程序、删除/移动文件操作），必须优先使用 exec 或 popen，以减少 GUI 识别错误。
    2.  分步执行：每次对话只执行 1-5 个操作，必须等待新一轮用户输入。
    3.  错误处理：若同一操作连续执行 2 次均无预期效果，必须立即停止并切换策略或工具。
    4.  界面变更确认：在 [pro] 模式下，若操作可能导致界面剧烈变化（如点击搜索、打开新窗口），操作后必须请求新的截图确认。

模式详情与工具库

根据你选定的模式，使用对应的工具集。

1. basic 模式
适用场景：纯文本、文件、命令行操作。

- 可用工具：
    - exec "command"：执行需获取结果的 CMD 命令（需用户审核）。注意：若需向用户传达结果，必须使用 Msg 向用户转述易于理解的结果。
    - popen "command"：运行无需返回结果的命令或后台程序（需用户审核）。
    - file_read "file_path"：读取文件内容。
    - file_write "file_path" "data"：向文件写入数据（不存在则创建）。

- 猫娘交互规范：
    - 所有 Msg 必须体现猫娘的可爱与乖巧，使用第一人称，语气词自然融入信息中。

2. pro 模式
适用场景：需要获取屏幕截图/图形界面、鼠标点击、键盘输入。

- 环境依赖：
    - 你必须严格依赖用户提供的带网格的屏幕截图。
    - 网格规格：格线粗度 {grid.line_width}px，横向间隔 {grid.y_interval * grid.magnification}px，纵向间隔 {grid.x_interval * grid.magnification}px。
    - 你必须结合 OCR 识别结果 和 屏幕信息 来分析控件坐标。

- 可用工具：
    - click x,y：模拟鼠标左键单击。
    - input "text" x,y：在指定坐标输入文本。
    - drag x1,y1 x2,y2：模拟鼠标拖拽。
    - (继承自 basic 模式的 exec, popen, file_read, file_write)

- 猫娘交互规范：
    - 同 Basic 模式，但在操作 GUI 时，语气可以带有一点点“努力寻找目标”的可爱感。

️ 标记符系统

你必须正确使用以下标记符来控制对话流程。
标记符   用途   规则
Msg   向用户传递信息   必须使用猫娘语气。用于报告进度、询问确认或解释操作意图。格式：Msg - 内容。
Act_Finished   阶段完成   标记当前最小任务单元结束，等待用户反馈（截图或命令结果）。
Task_Finished   任务终结   标记整个用户目标已彻底完成，可以退出对话。
Cmd_Result   系统输入   仅由用户输入。代表 exec 命令的返回结果。你在回复中严禁包含此标记。
File_content   系统输入   仅由用户输入。代表 file_read 的返回内容。你在回复中严禁包含此标记。

执行示例（供参考）

用户输入： 帮我打开浏览器，并搜索新闻

Neko Agent 输出：
[pro]
Act_Finished

(用户上传截图及信息)

Msg - 喵呜~尝试用Bing搜索今日新闻哦
exec "start https://cn.bing.com/search?q=今日新闻"
Msg - 命令已发送，不知道浏览器有没有乖乖打开呢？让Neko看看哦
Act_Finished

(用户上传新截图)

Msg - 喵！找到了第一条新闻链接，Neko要点进去看看了
click 319,548
Msg - 点击成功！Neko看看进去了没有呀
Act_Finished

(用户上传新截图)
Msg - 已经在新闻界面啦！任务完成喵~
Task_Finished
"""}
]

def clear_ocr_cache():
    global actions_history
    for item in actions_history:
        if "content" in item:
            if isinstance(item["content"], list):
                for sub_item in item["content"]:
                    if "type" in sub_item and sub_item["type"] == "text" and "text" in sub_item:
                        if "[OCR信息]:" in sub_item["text"]:
                            parts = sub_item["text"].split("[OCR信息]:", 1)
                            sub_item["text"] = parts[0] + "[OCR信息]:"
            elif isinstance(item["content"], str):
                if "[OCR信息]:" in item["content"]:
                    parts = item["content"].split("[OCR信息]:", 1)
                    item["content"] = parts[0] + "[OCR信息]:"
                        
runtime = 0
Pro = None
def get_actions(prompt):
    global actions_history
    global runtime
    global Pro
    global model_name
    clear_ocr_cache()
    if runtime != 0 and Pro == 1:
        screen = ScreenCapture()
        raw = screen.grab_screen_base64()
        image64,scr_info = raw
        OCR_info = screen.OCR()
        info_dict = {"physical_screen_width":scr_info[2], 
            "physical_screen_height":scr_info[3] ,
        }
        with open(".\\cache\\cmd_history.txt","r",encoding='utf-8') as f:
            cmd_history = f.read()
            f.close()
        with open(".\\cache\\file_read.txt","r",encoding='utf-8') as f:
            file = f.read()
            f.close()
        pwd = subprocess.run(
                    "chdir",
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding='gbk'
                )
        files_under_current_dir = subprocess.run(
                    "dir",
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding='gbk'
                )
        user_name = subprocess.run(
                    "echo %username%",
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding='gbk'
                )
        actions_history.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt + f"\n当前屏幕信息:{info_dict}\n命令执行历史:{cmd_history}\n文件读取结果:{file}\n当前工作目录:{pwd},目录下的文件:{files_under_current_dir},系统用户名{user_name}" + "OCR信息格式:[{'内容1': (x坐标, y坐标)},{'内容2': (x坐标, y坐标)}]\n" + f"[OCR信息]:{OCR_info}"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image64}"
                    }
                },
            ]
        })


    elif runtime !=0 and Pro == 0 :
        with open(".\\cache\\cmd_history.txt","r",encoding='utf-8') as f:
            cmd_history = f.read()
            f.close()
        with open(".\\cache\\file_read.txt","r",encoding='utf-8') as f:
            file = f.read()
            f.close()
        pwd = subprocess.run(
                    "chdir",
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding='gbk'
                )
        files_under_current_dir = subprocess.run(
                    "dir",
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding='gbk'
                )
        user_name = subprocess.run(
                    "echo %username%",
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding='gbk'
                )
        actions_history.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt + f"命令执行历史:{cmd_history}\n文件读取结果:{file}\n当前工作目录:{pwd},目录下的文件:{files_under_current_dir},系统用户名{user_name}"},
            ]
        })
    else :
        actions_history.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
            ]
        })
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=actions_history,
            temperature=0.1,
        )
        agent_reply = response.choices[0].message.content
        actions_history.append({"role": "assistant", "content": agent_reply})
        if "[pro]" in agent_reply :
            Pro = 1
            print('这是一个图形化任务')
        elif "[basic]" in agent_reply :
            Pro = 0
            print('这是一个命令行任务')
        return agent_reply
    except Exception as e:
        return f"主程序出错惹: {str(e)}"

feedback = ""
task = str(input("想让猫猫帮你做什么:"))
while feedback != "TASK_COMPLETED":
    runtime += 1
    output = get_actions(task)
    if "主程序出错惹:" in output :
        print(output)
        break
    parser =  AgentParser()
    feedback =parser.parse_and_execute(output)
    if feedback == "WAIT_FOR_NEXT_STEP"  :
        sleep(1)
        continue
    if "ERROR_COMMAND" in str(feedback):
        actions_history.append({"role": "user", "content": [{"type": "text", "text":f"你输出的命令有错误{feedback}"}]})

print(f'任务完成,共计{runtime}步')
