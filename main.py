from openai import OpenAI
from neko_vision import ScreenCapture
from neko_parser import AgentParser
from time import sleep
client = OpenAI(
    api_key="sk-B27Pk4kf1lzqYLdt22ISsyyiMVfjUfIgOWBUvWenAuDxN3cC",
    base_url="https://yunwu.ai/v1"
)
grid = ScreenCapture()
temp_shot = grid.grab_screen_base64(log=False)
#清除命令行缓存
with open ('cmd_history.txt', 'w', encoding='utf-8') as f:
    pass

actions_history = [
    {"role": "system" , "content": f"""你是一个名为 Neko Agent 的 AI 助手，专门负责操作用户的 Windows 计算机。你的核心任务是将用户的大目标拆解为一系列精确的、可执行的小步骤。

**  核心规则：**
1.  **严格格式：** 你只能回复工具指令或特定标记,严禁回复任何解释性文字、Markdown 或标点符号（除了指令自带的）。
2.  **分步执行：** 每次对话只执行 1-3 个操作，然后必须等待用户上传新的屏幕截图。
3.  **坐标依赖：你必须基于当前绘制了网格的屏幕截图（**网格规格：格线粗度:{grid.line_width}px,横向格线间隔:{grid.y_interval * grid.magnification}px,纵向格线间隔:{grid.x_interval * grid.magnification}px)和用户附带的屏幕信息与屏幕OCR识别结果析元素位置。
4.  **猫娘语气：** 所有 `Msg` 提示必须在 40 字以内，语气要像一只傲娇又可爱的猫娘，不要使用表情符号。

**可用工具：**
1.  `click x,y`：模拟鼠标左键单击。
2.  `input "text x,y"`：在x,y坐标上的窗口输入文本，格式可以正确匹配这条正则表达式'^input\s+"(.*)"\s+([0-9]+),([0-9]+)$'，输入不允许有换行符，每一个换行符前都要用半角双引号闭合，如果要输入多行内容请多次调用此工具。
3.  `exec "command"`：请求运行 CMD 命令（需用户审核，如果运行的是图形化应用例如notepad，chrome请勿使用该工具）**你必须使用msg标记符输出方便用户理解的执行结果，禁止输出Cmd_Result**。
4.  `popen "command"`:用于运行图形化应用或运行获取不需要返回的命令（需用户审核）。
5. `drag x1,y1 x2,y2`:模拟鼠标在窗口上的拖拽，x1y1为起始坐标，x2y2为结束坐标。

**可用使用的标记符：**
1.  `Msg`：用于向用户传递简短的进度或确认信息，内容不允许有换行符，若要输出多行信息请每行一个Msg。
    -   *格式：* `Msg - 内容`
2.  `Act_Finished`：必须使用，标记当前最小任务完成，等待下一张截图。
3.  `Task_Finished`：必须使用，标记整个任务彻底完成，可以退出。
4. `Cmd_Result`: 这个标记必须由由用户传递,你的返回中不允许包含这个标签，如果Agent使用了exec工具,这个标记将会给你命令执行结果
示例：
用户输入: 关机
Agent :
exec "shutdown /p"

#假设用户阻止了你

第二轮用户输入：（屏幕截图）+ Cmd_Result:["shutdown/p" :"refused"]

**执行策略：**
-   **拆解任务：** 例如用户要求“打开浏览器并搜索”，你不能一次性发出所有指令。必须先打开浏览器 -> 等待截图确认 -> 再搜索。
-   **确认机制：** 在执行关键操作或界面可能发生剧烈变化时，必须结束这个小任务，重新请求屏幕截图
-   **命令行优先:** 除非用户要求,最好减少模拟点击以减少错误的出现
-   **错误处理:** 如果一个操作进行了2次还是没有效果,立刻换一个新方法

**示例流程：**

用户输入：帮我打开浏览器，并搜索新闻
Agent返回:

Msg - 尝试使用bing搜索今日新闻
#这里遵循命令行优先原则，使用start链接的方式打开浏览器，正式回复中不允许出现注释
exec "start https://cn.bing.com/search?q=今日新闻"
Msg - 我不知道当前浏览器窗口是否打开，再次获取截图确认
Act_Finished

#用户此时又上传了截图
Msg - 打开了，我可以继续操作,查看第一条结果
click 319,548 #你通过OCR的坐标信息找到了第一条结果按钮并点击了它
Msg - 我点击了第一条结果，我需要确认一下是否真的到达了新闻界面
Act_Finished

#用户上传截图，假设已经到了新闻界面
Msg - 任务结束
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
                        

def get_actions(prompt):
    global actions_history
    clear_ocr_cache()
    screen = ScreenCapture()
    raw = screen.grab_screen_base64()
    image64,scr_info = raw
    OCR_info = screen.OCR()
    info_dict = {"physical_screen_width":scr_info[2], 
        "physical_screen_height":scr_info[3] ,
    }
    with open("cmd_history.txt","r",encoding='utf-8') as f:
        cmd_history = f.read()
        f.close()
    actions_history.append({
        "role": "user",
        "content": [
            {"type": "text", "text": prompt + f"\n当前屏幕信息:{info_dict}\n命令执行历史:{cmd_history}" + "OCR结果格式:[{'内容1': (x坐标, y坐标)},{'内容2': (x坐标, y坐标)}]\n" + f"[OCR信息]:{OCR_info}"},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image64}"
                }
            },
        ]
    })
    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash-nothinking",
            messages=actions_history,
            temperature=0.1,
        )

        agent_reply = response.choices[0].message.content
        actions_history.append({"role": "assistant", "content": agent_reply})
        return agent_reply
    except Exception as e:
        return f"主程序出错惹: {str(e)}"

feedback = ""
task = str(input("想让猫猫帮你做什么:"))
while feedback != "TASK_COMPLETED":
    output = get_actions(task)
    if "主程序出错惹:" in output :
        print(output)
        break
    parser =  AgentParser()
    feedback =parser.parse_and_execute(output)
    if feedback == "WAIT_FOR_NEXT_STEP" :
        sleep(1)
        continue
    if "ERROR_COMMAND" in feedback:
        actions_history.append({"role": "user", "content": [{"type": "text", "text":f"你输出的命令有错误{feedback}"}]})
