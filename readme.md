## 🐾 项目简介

哈喽哈喽，我是Neko Agentο(=•ω＜=)ρ⌒☆ 是一个住在Windows里的人工智能小助手喵(≧ω≦) 
我会努力听懂主人的话，帮主人做各种各样的事情哦！不仅可以陪主人聊天，还能分析屏幕上的内容，超厉害的说！

### ✨ Neko的优点

*   **可自定义的API**：主人可以根据自己的喜好配置Neko的openai API呀(。・ω・。)
*   **自动解析llm指令并执行**：Neko可以自动理解主人的指令，然后乖乖执行的哦~
*   **支持多种交互方式**：Neko可以点击、输入文本、执行命令，什么都会一点的ヾ(≧▽≦*)o
*   **自动分析场景并高效执行**：不管是图形界面任务、命令行任务还是聊天，Neko都能~~轻松应对~~的说
(小声说)Neko其实很依赖模型的...如果模型参数不高会很影响Neko的运行...并且在图形化任务中处理能力很弱〒▽〒

### 🧠 Neko是怎么工作的呢？

1.  主人给Neko发送信息
2.  Neko会认真分析信息类型，判断是否需要使用工具，或者进入聊天模式的哈

### 🔧 怎么安装Neko呢？

1.  首先要克隆这个仓库(GUI版本)哦！
    ```cmd
    git clone -b gui_dev https://github.com/Lin-neko/neko_agent
    ```
2.  然后**直接运行**install.bat就可以啦(记得提前装好python哦)！

### 📜 怎么使用Neko呢？

运行start.bat就可以开始和Neko互动啦！启动后Neko会给主人使用指引的

### 🛠️ Neko可以使用的工具

*   `exec "command"`：执行命令
*   `popen "command"`：静默执行命令
*   `file_read "path"`：读取文件
*   `file_write "path"`：写入文件
*   `click x y n`：点击屏幕上的某个位置n次
*   `input "text" x y`：在屏幕上的某个位置输入文字
*   `drag startX startY endX end Y`：拖动屏幕上的某个东西
*   `scroll x y amount`：滚动屏幕

### 📁 文件结构

*   `config.json`：这里面保存着Neko的配置信息，比如API Key什么的哦~
*   `default_callback.py`,`ocr_manager.py`: 这两个是WechatOCR的修改版组件
*   `emergency_exit.py`：这个是紧急退出，如果Neko出问题了可以用它来退出的喵~
*   `install.bat`：这个是安装Neko的批处理文件
*   `main.py`：这个是Neko的主程序，运行它就可以启动Neko啦！
*   `neko_control.py`：这个是Neko的控制模块，控制Neko的各种行为的说！
*   `neko_parser.py`：这个是Neko的解析器，用于解析并调用Controller执行操作
*   `neko_vision.py`：这个是Neko的眼睛，用来识别屏幕上的内容
*   `Nkernel.py`：这个也是Neko的大脑
*   `safe_parser.py`：这个是Neko的安全解析器，用来防止上下文污染,可能没什么用吧(～￣▽￣)～
*   `safe_screen.py`：这个是Neko的安全屏幕操作模块，同样用来防止上下文污染
*   `start.bat`：这个是启动Neko的批处理文件，双击它就可以启动Neko啦！
*   `system_prompt.txt`：这里面保存着Neko的系统提示词~
*   `gui/`：这个文件夹用来保存Neko的图形界面相关文件哦~
*   `OCR/`：这个文件夹用来保存Neko的OCR引擎(使用WechatOCR)
