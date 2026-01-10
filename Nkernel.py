from openai import OpenAI
import json
from safe_screen import take_screenshot_safe , perform_ocr_safe
from safe_parser import run_parser_safe
from gui.launcher.input_box_launcher import start_input_box
from time import sleep
import subprocess
import os

class NekoAgentKernel:
    def __init__(self):
        self.runtime = 0
        self.feedback = ""
        self.mode = None
        try:
            if os.path.exists(".\\cache\\chat_mode.lock"):
                os.remove(".\\cache\\chat_mode.lock")
        except Exception as e:
            self.add_log(f"删除锁文件失败: {str(e)}")
        with open("config.json", "r", encoding='utf-8') as f:
            self.config = json.load(f)
        self.ai_base_url = self.config["ai_settings"]["base_url"]
        self.ai_api_key = self.config["ai_settings"]["api_key"]
        self.ai_model_name = self.config["ai_settings"]["model_name"]
        self.chat_base_url = self.config["chat_settings"]["chat_url"]
        self.chat_api_key = self.config["chat_settings"]["chat_api_key"]
        self.chat_model_name = self.config["chat_settings"]["chat_model_name"]
        self.chat_image = self.config["chat_settings"]["chat_image"]
        self.chat_prompt = self.config["chat_settings"]["chat_prompt"]
        with open("system_prompt.txt","r",encoding='utf-8') as p:
            self.sys_prompt = p.read()

        self.chat_history=[{"role" : "system" , "content" : f"{self.chat_prompt}"}]
        self.actions_history = [{"role": "system" , "content": self.sys_prompt}]

        self.client = OpenAI(
            api_key= self.ai_api_key,
            base_url= self.ai_base_url
        )
        self.model_name = self.ai_model_name

        cache_files = [
            '.\\cache\\cmd_history.txt',
            '.\\cache\\file_read.txt',
            '.\\cache\\log.txt',
            '.\\cache\\user_message.txt',
            '.\\cache\\agent_message.txt'
        ]
        for file_path in cache_files:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    pass
            except FileNotFoundError:
                pass

    def clear_log(self):
        with open('.\\cache\\log.txt', 'w', encoding='utf-8') as f:
            pass
    def add_log(self,log_string):
        with open("cache/log.txt", "a",encoding='utf-8') as f:
            f.write(log_string)
    def add_user_msg(self,msg):
        with open("cache/user_message.txt", "a",encoding='utf-8') as f:
            f.write(msg + '[message_end]')
    def add_agent_msg(self,msg):
        with open("cache/agent_message.txt", "a",encoding='utf-8') as f:
            f.write(msg + '[message_end]')

    def clear_ocr_cache(self):
        for item in self.actions_history:
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

    def get_actions(self, prompt):
        self.clear_ocr_cache()
        if self.runtime != 0 and self.mode == "[pro]":
            image64 = take_screenshot_safe()
            OCR_info = perform_ocr_safe()
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
            self.actions_history.append(
                {"role": "user",
                    "content": [
                        {"type": "text",
                        "text": prompt + f"[system]命令执行历史:{cmd_history}\n文件读取结果:{file}\n当前工作目录:{pwd},目录下的文件:{files_under_current_dir},系统用户名{user_name}" + "OCR信息格式:[{'内容1': (x坐标, y坐标)},{'内容2': (x坐标, y坐标)}]\n" + f"[OCR信息]:{OCR_info}"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image64}"
                            }
                        },
                    ]
                }
            )


        elif self.runtime !=0 and self.mode == "[basic]" :
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
            self.actions_history.append(
                {"role": "user",
                    "content": [
                        {"type": "text",
                        "text": prompt + f"[system]命令执行历史:{cmd_history}\n文件读取结果:{file}\n当前工作目录:{pwd},目录下的文件:{files_under_current_dir},系统用户名{user_name}"},
                    ]
                }
            )

        elif self.mode == "[chat]":
            if self.runtime == 2:
                self.chat_history.append({"role": "user", "content": prompt})
                self.add_user_msg(prompt)
                if self.chat_image:
                    image64 = take_screenshot_safe()
                    self.chat_history.append({"role": "user",
                        "content": [{"type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image64}"}}]})

            if self.runtime > 2:
                chat = start_input_box(1)
                if not chat :
                    return False
                self.chat_history.append({"role": "user", "content": chat})
                self.add_user_msg(chat)
                if self.chat_image:
                    image64 = take_screenshot_safe()
                    self.chat_history.append({"role": "user","content": [{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{image64}"}}]})
            if self.chat_base_url != "":
                chat_cli = OpenAI(
                    api_key=self.chat_api_key,
                    base_url=self.chat_base_url
                )
                try :
                    response = chat_cli.chat.completions.create(
                        model=self.chat_model_name,
                        temperature=0.7,
                        messages=self.chat_history
                    )
                except Exception as e:
                    self.add_log("e")
            else:
                try :
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        temperature=0.7,
                        messages=self.chat_history
                    )
                except Exception as e:
                    self.add_log("e")
                
            self.chat_reply = response.choices[0].message.content
            self.chat_history.append({"role": "assistant", "content": self.chat_reply})
            result = "CHAT\n" + self.chat_reply
            return result

        else:
            self.actions_history.append(
                {"role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                    ]
                }
            )
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.actions_history,
                temperature=0.1,
            )
            agent_reply = response.choices[0].message.content
            self.actions_history.append({"role": "assistant", "content": agent_reply})
            if "[pro]" in agent_reply:
                self.mode = "[pro]"
                self.add_log('这是一个图形化任务\n')
            elif "[basic]" in agent_reply:
                self.mode = "[basic]"
                self.add_log('这是一个命令行任务\n')
            elif "[chat]" in agent_reply:
                self.mode = "[chat]"
                # 创建锁文件
                try:
                    with open(".\\cache\\chat_mode.lock", "w", encoding='utf-8') as f:
                        f.write("chat_mode")
                except Exception as e:
                    self.add_log(f"创建锁文件失败: {str(e)}")
            else:
                try:
                    if os.path.exists(".\\cache\\chat_mode.lock"):
                        os.remove(".\\cache\\chat_mode.lock")
                except Exception as e:
                    self.add_log(f"删除锁文件失败: {str(e)}")
            return agent_reply
        except Exception as e:
            return f"主程序出错惹: {str(e)}"


    def main_loop(self, task):
        while self.feedback != "TASK_COMPLETED":
            try:
                self.runtime += 1
                output = self.get_actions(task)
                if output:
                    if "主程序出错惹:" in output:
                        self.add_log(output)
                        return False
                        
                    self.feedback = run_parser_safe(output)
                    
                    if "CHAT" in str(self.feedback):
                        self.add_agent_msg(self.chat_reply)
                    if "Pause" in str(self.feedback):
                        return "PAUSE_REQUESTED"
                    if "ERROR_COMMAND" in str(self.feedback):
                        self.actions_history.append({
                            "role": "user", 
                            "content": [{"type": "text", "text": f"你输出的命令有错误{self.feedback},请严格按照规则重新输出"}]
                        })
                        self.add_log(f"出现错误命令{self.feedback}")
                    sleep(3)
                else :
                    return True
            except Exception as e:
                self.add_log(f"发生异常: {str(e)}")
                return False
        return True
