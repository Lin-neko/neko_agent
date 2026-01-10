import sys
import json
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QComboBox , QScrollArea, QCheckBox
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QEventLoop , QTimer
from gui.dark_mode_manager import dark_or_light
import json , ctypes

class WheelEventComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    def wheelEvent(self, event):
        event.ignore()

class NekoSettingsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)
        
        self.anti_grab = config["anti_grab"]
        if self.anti_grab == True :
            SetWindowDisplayAffinity = ctypes.windll.user32.SetWindowDisplayAffinity
            SetWindowDisplayAffinity.restype = ctypes.c_bool
            SetWindowDisplayAffinity(int(self.winId()) , 0x00000011)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self._result = None
        self._app = QApplication.instance() if QApplication.instance() else QApplication(sys.argv)
        
        self.overall_layout = QVBoxLayout(self) 
        self.overall_layout.setContentsMargins(20, 20, 20, 20)
        self.overall_layout.setSpacing(20)

        self.title_label = QLabel("Neko Agent 设置", self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overall_layout.addWidget(self.title_label)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # Disable horizontal scroll bar

        self.scroll_content_widget = QWidget()
        self.main_layout = QVBoxLayout(self.scroll_content_widget) 
        self.main_layout.setContentsMargins(0, 0, 0, 0) 
        self.main_layout.setSpacing(15)
        
        self.ai_setting_label = QLabel('AI模型设置', self.scroll_content_widget)
        self.main_layout.addWidget(self.ai_setting_label)

        self.base_url_container, self.base_url_label, self.base_url_line_edit = self._create_labeled_input_field("base_url:", "例如https://example.com/v1")
        self.main_layout.addWidget(self.base_url_container) 
        
        self.api_key_container, self.api_key_label, self.api_key_line_edit = self._create_labeled_input_field("api_key:", "你的api_key")
        self.main_layout.addWidget(self.api_key_container) 
        
        self.model_name_container, self.model_name_label, self.model_name_line_edit = self._create_labeled_input_field("模型名称:" , "例如gpt-4o")
        self.main_layout.addWidget(self.model_name_container)


        self.nv_setting_label = QLabel('Neko Vision设置', self.scroll_content_widget)
        self.main_layout.addWidget(self.nv_setting_label)
        
        # self.divide_setting , self.divide_label , self.divede_edit = self._create_labeled_input_field("网格等分数量:" , "帮助模型识别坐标,在截图上绘制网格")
        # self.main_layout.addWidget(self.divide_setting)
        # self.line_width_setting , self.line_width_label , self.line_width_edit = self._create_labeled_input_field("网格线粗细:" , "1px差不多")
        # self.main_layout.addWidget(self.line_width_setting)
        self.magnification_setting , self.magnification_label , self.magnification_edit =  self._create_labeled_input_field("截图缩小倍率:" , "将截图宽高分别除以x")  
        self.main_layout.addWidget(self.magnification_setting)


        self.dark_mode_setting_label = QLabel("深色模式设置" , self.scroll_content_widget)
        self.main_layout.addWidget(self.dark_mode_setting_label)
        self.dark_mode_setting = WheelEventComboBox()
        self.dark_mode_setting.addItems(["自动" , "始终深色" , "始终浅色"])
        self.main_layout.addWidget(self.dark_mode_setting)

        self.chat_setting_label = QLabel("聊天模式设置" , self.scroll_content_widget)
        self.main_layout.addWidget(self.chat_setting_label)
        self.chat_url_setting , self.chat_url_label , self.chat_url_edit = self._create_labeled_input_field("Chat模式下baseurl:" , "留空与agent使用同一个模型")
        self.main_layout.addWidget(self.chat_url_setting)
        
        self.chat_api_key, self.chat_key_label, self.chat_api_key_line_edit = self._create_labeled_input_field("Chat模式下api_key:", "留空与agent使用同一api_key")
        self.main_layout.addWidget(self.chat_api_key) 

        self.chat_model_name, self.chat_model_name_label, self.chat_model_name_line_edit = self._create_labeled_input_field("Chat模式下的模型名称:", "留空与agent使用同一模型")
        self.main_layout.addWidget(self.chat_model_name) 
        
        self.chat_prompt, self.chat_prompt_label, self.chat_prompt_line_edit = self._create_labeled_input_field("Chat模式下的系统提示词:", "也就是人物设定之类的")
        self.main_layout.addWidget(self.chat_prompt) 
        
        

        self.chat_agent_name_setting , self.chat_agent_label , self.chat_agent_edit = self._create_labeled_input_field("Agent昵称:" , "agent的昵称")
        self.main_layout.addWidget(self.chat_agent_name_setting)

        self.chat_user_name_setting , self.chat_user_label , self.chat_user_edit = self._create_labeled_input_field("用户昵称:" , "用户的昵称")
        self.main_layout.addWidget(self.chat_user_name_setting)

        self.chat_avatar_setting , self.chat_avatar_label = self._create_labeled_input_field("头像设置")
        self.main_layout.addWidget(self.chat_avatar_setting)

        # 用户头像
        self.user_avatar_container = QWidget()
        self.user_avatar_hlayout = QVBoxLayout(self.user_avatar_container)
        self.user_avatar_layout = QVBoxLayout()
        self.user_avatar_label = QLabel()
        user_avatar_path = os.path.join("gui", "img", "user_avatar.png")
        from PyQt6.QtGui import QPixmap
        self.user_avatar_label.setPixmap(QPixmap(user_avatar_path).scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
        self.user_avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.user_avatar_layout.addWidget(self.user_avatar_label)
        self.user_avatar_name_label = QLabel("用户头像")
        self.user_avatar_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.user_avatar_layout.addWidget(self.user_avatar_name_label)
        self.user_avatar_hlayout.addLayout(self.user_avatar_layout)
        self.user_avatar_button = QPushButton("选择文件")
        self.user_avatar_hlayout.addWidget(self.user_avatar_button)

        # Agent头像
        self.agent_avatar_container = QWidget()
        self.agent_avatar_hlayout = QVBoxLayout(self.agent_avatar_container)
        self.agent_avatar_layout = QVBoxLayout()
        self.agent_avatar_label = QLabel()
        agent_avatar_path = os.path.join("gui", "img", "agent_avatar.JPG")
        self.agent_avatar_label.setPixmap(QPixmap(agent_avatar_path).scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
        self.agent_avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.agent_avatar_layout.addWidget(self.agent_avatar_label)
        self.agent_avatar_name_label = QLabel("Agent头像")
        self.agent_avatar_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.agent_avatar_layout.addWidget(self.agent_avatar_name_label)
        self.agent_avatar_hlayout.addLayout(self.agent_avatar_layout)
        self.agent_avatar_button = QPushButton("选择文件")
        self.agent_avatar_hlayout.addWidget(self.agent_avatar_button)

        self.user_avatar_button.clicked.connect(self._on_user_avatar_button_clicked)
        self.agent_avatar_button.clicked.connect(self._on_agent_avatar_button_clicked)

        avatar_layout = QHBoxLayout()
        avatar_layout.addWidget(self.user_avatar_container)
        avatar_layout.addWidget(self.agent_avatar_container)
        self.main_layout.addLayout(avatar_layout)

        self.chat_image_label = QLabel("在聊天时附带屏幕截图:")
        self.chat_image_setting_switch = QCheckBox()
        self.chat_image_settings = QWidget()
        self.chat_image_layout = QHBoxLayout(self.chat_image_settings)
        self.chat_image_layout.addWidget(self.chat_image_label)
        self.chat_image_layout.addWidget(self.chat_image_setting_switch)
        self.main_layout.addWidget(self.chat_image_settings)


        self.other_setting_label = QLabel('其他设置', self.scroll_content_widget)
        self.main_layout.addWidget(self.other_setting_label)
        self.anti_grab_label = QLabel("控件反截图:")
        self.anti_grab_setting_switch = QCheckBox()
        self.anti_grab_settings = QWidget()
        self.anti_grab_layout = QHBoxLayout(self.anti_grab_settings)
        self.anti_grab_layout.addWidget(self.anti_grab_label)
        self.anti_grab_layout.addWidget(self.anti_grab_setting_switch)
        self.main_layout.addWidget(self.anti_grab_settings)
        



        self.scroll_area.setWidget(self.scroll_content_widget)
        self.overall_layout.addWidget(self.scroll_area) 

        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(10)

        self.confirm_button = QPushButton("确认", self)
        self.confirm_button.clicked.connect(self.on_confirm_clicked)
        self.button_layout.addWidget(self.confirm_button)
        
        self.cancel_button = QPushButton("取消", self)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.button_layout.addWidget(self.cancel_button)
        
        self.overall_layout.addLayout(self.button_layout) 
        
        # 动画效果
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(400)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.initial_pos_set = False

    def save_settings_to_config(self, settings):
        config_path = "config.json"
        current_config = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    current_config = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: config.json is malformed. Starting with empty config.")
                current_config = {}

        if 'ai_settings' not in current_config:
            current_config['ai_settings'] = {}
        current_config['ai_settings']['base_url'] = settings.get('base_url')
        current_config['ai_settings']['api_key'] = settings.get('api_key')
        current_config['ai_settings']['model_name'] = settings.get('model_name')

        if 'neko_vision_settings' not in current_config:
            current_config['neko_vision_settings'] = {}
        # current_config['neko_vision_settings']['line_width'] = settings.get('line_width')
        # current_config['neko_vision_settings']['divide'] = settings.get('divide')
        current_config['neko_vision_settings']['magnification'] = settings.get('magnification')

        if 'chat_settings' not in current_config:
            current_config['chat_settings'] = {}
        current_config['chat_settings']['chat_url'] = settings.get('chat_url')
        current_config['chat_settings']['chat_api_key'] = settings.get('chat_api_key')
        current_config['chat_settings']['chat_model_name'] = settings.get('chat_model_name')
        current_config['chat_settings']['chat_prompt'] = settings.get('chat_prompt')
        current_config['chat_settings']['chat_agent_name'] = settings.get('chat_agent_name')
        current_config['chat_settings']['chat_user_name'] = settings.get('chat_user_name')
        current_config['chat_settings']['chat_image'] = settings.get('chat_image')
        
        current_config['anti_grab'] = settings.get('anti_grab')

        current_config['dark_mode'] = settings.get('darkmode')

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(current_config, f, indent=4, ensure_ascii=False)
        print(f"Settings saved to {config_path}")

    def _load_settings_from_config(self):
        config_path = "config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # Load AI settings
                ai_settings = config.get('ai_settings', {})
                self.base_url_line_edit.setText(ai_settings.get('base_url', ''))
                self.api_key_line_edit.setText(ai_settings.get('api_key', ''))
                self.model_name_line_edit.setText(ai_settings.get('model_name', ''))

                # Load Neko Vision settings
                neko_vision_settings = config.get('neko_vision_settings', {})
                # self.divede_edit.setText(neko_vision_settings.get('divide', ''))
                # self.line_width_edit.setText(neko_vision_settings.get('line_width', ''))
                self.magnification_edit.setText(neko_vision_settings.get('magnification', ''))

                # Load Dark Mode setting
                dark_mode_setting_text = config.get('dark_mode', '自动')
                index = self.dark_mode_setting.findText(dark_mode_setting_text)
                if index != -1:
                    self.dark_mode_setting.setCurrentIndex(index)

                # Load Chat settings
                chat_settings = config.get('chat_settings', {})
                self.chat_url_edit.setText(chat_settings.get('chat_url', ''))
                self.chat_api_key_line_edit.setText(chat_settings.get('chat_api_key', ''))
                self.chat_model_name_line_edit.setText(chat_settings.get('chat_model_name', ''))
                self.chat_prompt_line_edit.setText(chat_settings.get('chat_prompt',''))
                self.chat_agent_edit.setText(chat_settings.get('chat_agent_name', ''))
                self.chat_user_edit.setText(chat_settings.get('chat_user_name', ''))
                self.chat_image_setting_switch.setChecked(chat_settings.get('chat_image', False))
                self.anti_grab_setting_switch.setChecked(config.get('anti_grab', False))

            except json.JSONDecodeError:
                print(f"Error: config.json is malformed. Could not load settings.")
            except Exception as e:
                print(f"An error occurred while loading settings: {e}")
        else:
            print(f"config.json not found at {config_path}. Starting with default settings.")
        
    def _create_labeled_input_field(self, label_text, placeholder_text=None):
        container_widget = QWidget()
        layout = QVBoxLayout(container_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        label = QLabel(label_text, container_widget)
        label.setStyleSheet("font-size: 14px; padding-bottom: 5px")
        layout.addWidget(label)
        
        if placeholder_text != None:
            line_edit = QLineEdit(container_widget)
            line_edit.setPlaceholderText(placeholder_text)
            layout.addWidget(line_edit)
            container_widget.setStyleSheet("QWidget { border: none; }")
            return container_widget, label, line_edit
        else :
            container_widget.setStyleSheet("QWidget { border: none; }")
            return container_widget, label

    def showEvent(self, event):
        if not self.initial_pos_set:
            screen = QApplication.primaryScreen()
            screen_rect = screen.geometry()
            
            width = int(screen_rect.width() * 0.25)  
            height = int(screen_rect.height() * 0.5)
            
            x = (screen_rect.width() - width) // 2
            y = (screen_rect.height() - height) // 2
            
            start_y = -height
            self.setGeometry(x, start_y, width, height)
            
            self.animation.setStartValue(QRect(x, start_y, width, height))
            self.animation.setEndValue(QRect(x, y, width, height))
            self._update_style_based_on_background()
            self._load_settings_from_config() # Load settings before showing
            QApplication.processEvents()
        self.animation.start()
        self.initial_pos_set = True

        super().showEvent(event)
        
    def _update_style_based_on_background(self):
        screen = QApplication.primaryScreen()
        screen_rect = screen.geometry()
        x = screen_rect.width() // 2

        y = screen_rect.height() // 2
        
        dark_mode = dark_or_light(x, y)
        
        base_styles = {
            "title_label": {
                "font-size": "20px", # Increased font size
                "font-weight": "bold",
            },
            "section_label": { # New style for section labels
                "font-size": "16px",
                "font-weight": "bold",
                "margin-top": "10px", # Added margin for spacing
            },
            "label": {
                "font-size": "14px",
                "padding-bottom": "5px",
            },
            "line_edit": {
                "padding": "8px",
                "font-size": "14px",
                "border-radius": "4px", # Increased border-radius
                "border": "1px solid",
            },
            "line_edit_focus": {
                "border": "1px solid",
                "outline": "none",
            },
            "combobox": { # New style for QComboBox
                "padding": "8px",
                "font-size": "14px",
                "border-radius": "4px",
                "border": "1px solid",
            },
            "button": {
                "padding": "8px 16px",
                "font-size": "12px",
                "font-weight": "normal",
                "border-radius": "4px", # Increased border-radius
                "border": "1px solid",
            }
        }

        if dark_mode == "Light":
            theme_colors = {
                "bg_color": "#f3f3f3",
                "text_color": "#323130",
                "border_color": "#d1d1d1",
                "input_bg": "white",
                "input_border": "#d1d1d1",
                "input_focus_border": "#0078d4",
                "confirm_bg": "#0078d4",
                "confirm_hover": "#106ebe",
                "confirm_pressed": "#005a9e",
                "cancel_bg": "#f3f3f3",
                "cancel_hover": "#e1e1e1",
                "cancel_pressed": "#c8c8c8",
                "cancel_text": "#323130",
                "cancel_border": "#8a8886",
                "combobox_bg": "white", # New combobox colors
                "combobox_border": "#d1d1d1",
                "combobox_arrow": "#323130",
                "scrollbar_bg": "#f0f0f0",
                "scrollbar_handle_bg": "#c0c0c0",
                "scrollbar_handle_hover_bg": "#a0a0a0",
                "scrollbar_handle_pressed_bg": "#808080",
            }
        else: 
            theme_colors = {
                "bg_color": "#2d2d2d",
                "text_color": "#ffffff",
                "border_color": "#3e3e3e",
                "input_bg": "#1e1e1e",
                "input_border": "#3e3e3e",
                "input_focus_border": "#0078d4",
                "confirm_bg": "#0078d4",
                "confirm_hover": "#106ebe",
                "confirm_pressed": "#005a9e",
                "cancel_bg": "#3e3e3e",
                "cancel_hover": "#4f4f4f",
                "cancel_pressed": "#5f5f5f",
                "cancel_text": "#ffffff",
                "cancel_border": "#5f5f5f",
                "combobox_bg": "#1e1e1e", # New combobox colors
                "combobox_border": "#3e3e3e",
                "combobox_arrow": "#ffffff",
                "scrollbar_bg": "#3e3e3e",
                "scrollbar_handle_bg": "#606060",
                "scrollbar_handle_hover_bg": "#808080",
                "scrollbar_handle_pressed_bg": "#a0a0a0",
            }
            
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme_colors['bg_color']};
                border-radius: 8px; /* Added border-radius to the main window */
            }}
            QScrollArea {{
                border: none; /* Remove border from scroll area */
            }}
            QScrollArea > QWidget {{
                background-color: {theme_colors['bg_color']}; /* Ensure scroll content has correct background */
            }}
            QScrollBar:vertical {{
                border: none;
                background: {theme_colors['scrollbar_bg']};
                width: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {theme_colors['scrollbar_handle_bg']};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {theme_colors['scrollbar_handle_hover_bg']};
            }}
            QScrollBar::handle:vertical:pressed {{
                background: {theme_colors['scrollbar_handle_pressed_bg']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        
        self.title_label.setStyleSheet(f"""
            QLabel {{
                font-size: {base_styles['title_label']['font-size']};
                font-weight: {base_styles['title_label']['font-weight']};
                color: {theme_colors['text_color']};
            }}
        """)
        
        section_label_style = f"""
            QLabel {{
                font-size: {base_styles['section_label']['font-size']};
                font-weight: {base_styles['section_label']['font-weight']};
                color: {theme_colors['text_color']};
                margin-top: {base_styles['section_label']['margin-top']};
            }}
        """
        #大标题label
        self.ai_setting_label.setStyleSheet(section_label_style)
        self.nv_setting_label.setStyleSheet(section_label_style)
        self.dark_mode_setting_label.setStyleSheet(section_label_style)
        self.chat_setting_label.setStyleSheet(section_label_style)
        self.other_setting_label.setStyleSheet(section_label_style)
        
        label_style = f"""
            QLabel {{
                font-size: {base_styles['label']['font-size']};
                padding-bottom: {base_styles['label']['padding-bottom']};
                color: {theme_colors['text_color']};
            }}
        """
        #设置项的label
        self.base_url_label.setStyleSheet(label_style)
        self.api_key_label.setStyleSheet(label_style)
        self.model_name_label.setStyleSheet(label_style)

        # self.divide_label.setStyleSheet(label_style)
        # self.line_width_label.setStyleSheet(label_style)
        self.magnification_label.setStyleSheet(label_style)
        
        self.chat_url_label.setStyleSheet(label_style)
        self.chat_key_label.setStyleSheet(label_style)
        self.chat_model_name_label.setStyleSheet(label_style)
        self.chat_prompt_label.setStyleSheet(label_style) 
        self.chat_agent_label.setStyleSheet(label_style)
        self.chat_user_label.setStyleSheet(label_style)
        self.chat_image_settings.setStyleSheet(label_style)
        self.chat_avatar_label.setStyleSheet(label_style)
        self.agent_avatar_name_label.setStyleSheet(label_style)
        self.user_avatar_name_label.setStyleSheet(label_style)
        
        self.anti_grab_label.setStyleSheet(label_style)
        input_style = f"""
            QLineEdit {{
                background-color: {theme_colors['input_bg']};
                padding: {base_styles['line_edit']['padding']};
                font-size: {base_styles['line_edit']['font-size']};
                color: {theme_colors['text_color']};
                border: {base_styles['line_edit']['border']} {theme_colors['input_border']};
                border-radius: {base_styles['line_edit']['border-radius']};
            }}
            QLineEdit:focus {{
                border: {base_styles['line_edit_focus']['border']} {theme_colors['input_focus_border']};
                outline: {base_styles['line_edit_focus']['outline']};
            }}
        """
        #设置项输入框的样式
        self.base_url_line_edit.setStyleSheet(input_style)
        self.api_key_line_edit.setStyleSheet(input_style)
        self.model_name_line_edit.setStyleSheet(input_style)
        
        # self.divede_edit.setStyleSheet(input_style)
        # self.line_width_edit.setStyleSheet(input_style)
        self.magnification_edit.setStyleSheet(input_style)
        
        self.chat_url_edit.setStyleSheet(input_style)
        self.chat_model_name_line_edit.setStyleSheet(input_style)
        self.chat_api_key_line_edit.setStyleSheet(input_style)
        self.chat_agent_edit.setStyleSheet(input_style)
        self.chat_user_edit.setStyleSheet(input_style)
        self.chat_prompt_line_edit.setStyleSheet(input_style)

        combobox_style = f"""
            QComboBox {{
                background-color: {theme_colors['combobox_bg']};
                color: {theme_colors['text_color']};
                padding: {base_styles['combobox']['padding']};
                font-size: {base_styles['combobox']['font-size']};
                border: {base_styles['combobox']['border']} {theme_colors['combobox_border']};
                border-radius: {base_styles['combobox']['border-radius']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                /* image: url(gui/img/down_arrow_{dark_mode.lower()}.png); */ /* User will handle arrow images */
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme_colors['combobox_bg']};
                color: {theme_colors['text_color']};
                selection-background-color: {theme_colors['confirm_bg']};
            }}
        """
        #选择框
        self.dark_mode_setting.setStyleSheet(combobox_style)



        self.avatar_button_style = f"""
            QPushButton {{
                background-color: {theme_colors['cancel_bg']};
                color: {theme_colors['cancel_text']};
                padding: {base_styles['button']['padding']};
                font-size: {base_styles['button']['font-size']};
                font-weight: {base_styles['button']['font-weight']};
                border: {base_styles['button']['border']} {theme_colors['cancel_border']};
                border-radius: {base_styles['button']['border-radius']};
            }}
            QPushButton:hover {{
                background-color: {theme_colors['cancel_hover']};
                border-color: {theme_colors['cancel_border']};
            }}
            QPushButton:pressed {{
                background-color: {theme_colors['cancel_pressed']};
                border-color: {theme_colors['cancel_pressed']};
            }}
        """

        self.user_avatar_button.setStyleSheet(self.avatar_button_style)
        self.agent_avatar_button.setStyleSheet(self.avatar_button_style)
        
        self.confirm_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_colors['confirm_bg']};
                color: white;
                padding: {base_styles['button']['padding']};
                font-size: {base_styles['button']['font-size']};
                font-weight: {base_styles['button']['font-weight']};
                border: {base_styles['button']['border']} {theme_colors['confirm_bg']};
                border-radius: {base_styles['button']['border-radius']};
            }}
            QPushButton:hover {{
                background-color: {theme_colors['confirm_hover']};
                border-color: {theme_colors['confirm_hover']};
            }}
            QPushButton:pressed {{
                background-color: {theme_colors['confirm_pressed']};
                border-color: {theme_colors['confirm_pressed']};
            }}
        """)
        
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_colors['cancel_bg']};
                color: {theme_colors['cancel_text']};
                padding: {base_styles['button']['padding']};
                font-size: {base_styles['button']['font-size']};
                font-weight: {base_styles['button']['font-weight']};
                border: {base_styles['button']['border']} {theme_colors['cancel_border']};
                border-radius: {base_styles['button']['border-radius']};
            }}
            QPushButton:hover {{
                background-color: {theme_colors['cancel_hover']};
                border-color: {theme_colors['cancel_border']};
            }}
            QPushButton:pressed {{
                background-color: {theme_colors['cancel_pressed']};
                border-color: {theme_colors['cancel_pressed']};
            }}
        """)
        
    def on_confirm_clicked(self):
        self._result = {
            "base_url": self.base_url_line_edit.text(),
            "api_key": self.api_key_line_edit.text(),
            "model_name": self.model_name_line_edit.text(),
            # "line_width": self.line_width_edit.text(),
            # "divide": self.divede_edit.text(),
            "magnification": self.magnification_edit.text(),
            "darkmode": self.dark_mode_setting.currentText(),
            "chat_url": self.chat_url_edit.text(),
            "chat_api_key": self.chat_api_key_line_edit.text(),
            "chat_model_name": self.chat_model_name_line_edit.text(),
            "chat_prompt":self.chat_prompt_line_edit.text(),
            "chat_agent_name": self.chat_agent_edit.text(),
            "chat_user_name": self.chat_user_edit.text(),
            "chat_image": self.chat_image_setting_switch.isChecked(),
            "anti_grab": self.anti_grab_setting_switch.isChecked()
        }
        self.save_settings_to_config(self._result)
        self._close_window()
        
    def on_cancel_clicked(self):
        self._close_window()
        
    def _close_window(self):
        start_rect = self.geometry()
        end_rect = QRect(start_rect.x(), -start_rect.height(), start_rect.width(), start_rect.height())
        
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.start()
        
        self.animation.finished.connect(self._delayed_exit)
        if hasattr(self, '_event_loop'):
            self._event_loop.exit()
        
    def _delayed_exit(self):
        QTimer.singleShot(450, lambda: sys.exit(0))

    def _on_user_avatar_button_clicked(self):
        self._open_file_dialog(self.user_avatar_label, "user_avatar.png")

    def _on_agent_avatar_button_clicked(self):
        self._open_file_dialog(self.agent_avatar_label, "agent_avatar.JPG")

    def _open_file_dialog(self, avatar_label, default_file_name):
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择头像",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            from PyQt6.QtGui import QPixmap
            avatar_label.setPixmap(QPixmap(file_path).scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
            import shutil
            destination_path = os.path.join("gui", "img", default_file_name)
            try:
                shutil.copy2(file_path, destination_path)
                print(f"Avatar file copied to {destination_path}")
            except Exception as e:
                print(f"Error copying avatar file: {e}")
            
    def get_settings(self):
        self.show()
        self._event_loop = QEventLoop()
        self._event_loop.exec()
