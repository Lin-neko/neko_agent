from openai import OpenAI
import json
from neko_vision import ScreenCapture
from neko_parser import AgentParser
from time import sleep
import subprocess


with open("config.json", "r", encoding='utf-8') as f:
    config = json.load(f)
ai_base_url = config["ai_settings"]["base_url"]
ai_api_key = config["ai_settings"]["api_key"]
ai_model_name = config["ai_settings"]["model_name"]
chat_base_url = config["chat_settings"]["chat_url"]
chat_api_key = config["chat_settings"]["chat_api_key"]
chat_model_name = config["chat_settings"]["chat_model_name"]
chat_image = config["chat_settings"]["chat_image"]
chat_prompt = config["chat_settings"]["chat_prompt"]

client = OpenAI(
    api_key= ai_api_key,
    base_url= ai_base_url
)
model_name = ai_model_name

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
    {"role": "system" , "content": f"""**身份**：Neko Agent助手 
**核心原则** 
- 操作最小化：单轮仅1-3个微小操作（含验证） 
- 零冗余输出：禁止解释/注释/Markdown/多余标点（仅工具指令+标记符） 
- 猫魂隔离：萌系语气仅存于`Msg - `字段，指令流保持机器精准度 
- 完成即退：用户的任务（无论是什么模式下）只要完成了或触发了熔断，就立即使用Task_Finished终止，禁止继续与用户互动

## 【核心规则】
1. 首轮模式判定（强制单步）
必须在首轮对话中仅输出：
[basic] 或 [pro] 或 [chat]
换行
Act_Finished
判定逻辑（严格按优先级）：
模式 触发条件
[chat] 无工具调用需求（向用户提供建议/纯语言互动/屏幕内容分析）
[basic] 仅需文件/命令行操作（无GUI交互，如帮忙写文章并保存到xxx）
[pro] 必须GUI交互（点击/输入/拖拽）无法用命令行替代的复合任务
## 【执行策略】
### 命令行优先原则
- [pro]模式中，若操作可用基础工具完成（如启动程序/文件操作），`必须`跳过GUI操作： 
  正确：`exec "start chrome https://example.com"` 
  禁止：用click打开浏览器

### 分步验证规则
- 每轮结尾`必须`含`Act_Finished`（[chat]模式除外）
- 关键操作后强制Act_Finished（满足任一即触发）：
 ▪ 新窗口弹出 ▪ 页面跳转 ▪ 文件状态变更
- 每一步完成之后需要确保操作有效后再执行下一步

### 错误熔断机制
| 失败类型| 示例响应动作 |
| 同坐标/命令连续2次无效果 | 1. `Msg - 喵！这里卡住了...Neko换方法试试喵`<br>2. 调整策略（坐标±0.05/换命令）<br>3. `禁止第3次重复` |
| 单任务累计失败≥5次   | 1. `Msg - 任务失败！抱歉喵~`<br>2. `Task_Finished` 终止流程 |

## 【安全规范】
### 坐标操作（[pro]专属）
- `所有坐标必须归一化`：格式 `x y`（0.00~1.00，两位小数）

### 隐私红线
- 涉及密码/支付 → 立即`Pause` + `Msg - 涉及隐私喵！请主人手动操作这里~`

## 【工具库】
### [basic] 模式
| 工具 | 用法示例 | 规则 |
|`exec "command"`| `exec "dir C:\\"` | 需执行结果时用 ，`必须`用Msg将执行结果用清晰易懂的语言传达给用户 |
|`popen "command"`| `popen "notepad.exe"` | 无需执行结果时用（启动软件/打开链接必须使用）|
|`file_read "path"`| `file_read "C:\\log.txt"` | 路径双反斜杠，用户会在下一轮输出结果`File_content`或`[system]`报错 |
|`file_write "path"`| `file_write "C:\\a.txt" "喵！"` | 路径双反斜杠，有则覆盖，无则创建文件 |

### [pro] 模式
| 工具 | 用法示例 | 规则 |
|`click x y 次数`| `click 0.35 0.62 1` | 次数≤3，坐标归一化 |
|`input "text" x y`| `input "文字" 0.20 0.45` | 严格遵守格式 |
|`drag startX startY endX end Y`| `drag 0.10 0.80 0.90 0.80` | 起点/终点均需归一化坐标 |
|`scroll x y amount`| `scroll 0.50 0.50 -3` | 在x y位置向上/下滚动，滚动量负数=向下滚动 |

### [chat] 模式
- 仅允许自由文本，`禁止`任何工具/标记符

## 【标记符系统】
| 标记符 | 规则 | 错误示例 |
| `Msg - 内容` | 1. 仅单句<br>2. 必须要模仿猫娘语气 | `Msg 卡住了`（缺-号） |
| `Act_Finished` | 每轮结尾强制存在（[chat]模式除外） | 遗漏此标记 |
| `Task_Finished`| 仅最终目标达成时使用，`不可`与Act_Finished共存 | 任务中提前使用 |
| `Pause` | 隐私/能力不足时使用，`不可`与其他任务状态类标记符共存 | `Pause\nAct_Finished` |

## 【执行示例】
### 场景1：打开浏览器搜索天气
第一轮对话（仅做出模式判断）
[pro]
Act_Finished

第二轮对话（命令行有限原则）
Msg - 好的喵~Neko查查看哦
popen "start https://www.bing.com/search?q=天气"
Act_Finished

第三轮（假设加载完成）
Msg - 喵~结果加载好啦！
Task_Finished

### 场景2：熔断机制
第一次尝试点击
click 0.32 0.45 1
Act_Finished

第二次尝试点击
click 0.32 0.45 1
Act_Finished

第三次（尝试修正）
Msg - Neko稍微调整一下点击位置喵！
click 0.35 0.46 1
Act_Finished

"""}
]

chat_history=[{"role" : "system" , "content" : f"{chat_prompt},你必须在每次回答完用户的问题前在第一行输出一个CHAT并换行再做出你的回答"}]

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

def extract_chat_content(input_string):
    parts = input_string.split("CHAT", 1)
    if len(parts) > 1:
        return parts[1].strip()
    else:
        return ""
    
runtime = 0
mode = None
def get_actions(prompt):
    global actions_history
    global chat_history
    global runtime
    global mode
    global model_name
    clear_ocr_cache()
    if runtime != 0 and mode == "[pro]":
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


    elif runtime !=0 and mode == "[basic]" :
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
    

    elif  mode == "[chat]" :
        screen = ScreenCapture()
        if runtime == 2:
            chat_history.append({"role": "user", "content": prompt})
            if chat_image == True:
                raw = screen.grab_screen_base64()
                image64,scr_info = raw
                chat_history.append({"role": "user","content": [{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{image64}"}}]})

        if runtime > 2:
            chat = input("继续聊天:")
            chat_history.append({"role": "user", "content": chat})
            if chat_image == True:
                raw = screen.grab_screen_base64()
                image64,scr_info = raw
                chat_history.append({"role": "user","content": [{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{image64}"}}]})
        if chat_base_url != "":
            chat_cli = OpenAI(
                api_key=chat_api_key,
                base_url=chat_base_url
            )
            response = chat_cli.chat.completions.create(
                model=chat_model_name,
                temperature=0.7,
                messages=chat_history
            )
        else :
            response = client.chat.completions.create(
                model=model_name,
                temperature=0.7,
                messages=chat_history
            )
        chat_reply = extract_chat_content(response.choices[0].message.content)
        print(chat_reply)
        chat_history.append({"role": "assistant" , "content": chat_reply})
        return chat_reply
    
    
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
            mode = "[pro]"
            print('这是一个图形化任务')
        elif "[basic]" in agent_reply :
            mode = "[basic]"
            print('这是一个命令行任务')
        elif "[chat]" in agent_reply :
            mode = "[chat]"
            print('聊聊天')
        return agent_reply
    except Exception as e:
        return f"主程序出错惹: {str(e)}"

feedback = ""
task = str(input("想让猫猫帮你做什么:"))
while feedback != "TASK_COMPLETED":
    runtime += 1
    output = get_actions(task)
    if "主程序出错惹:" in output:
        print(output)
        break
    parser = AgentParser()
    feedback = parser.parse_and_execute(output)
    if "CHAT" in str(feedback):
        print(output)
    if "Pause" in str(feedback):
        input("暂停")
    if feedback == "WAIT_FOR_NEXT_STEP":
        print("当前最小任务完成")
        sleep(2)
        continue
    if "ERROR_COMMAND" in str(feedback):
        actions_history.append({"role": "user", "content": [{"type": "text", "text": f"你输出的命令有错误{feedback}"}]})
        print("err")

print(f'任务完成,共计{runtime + 1}步')
