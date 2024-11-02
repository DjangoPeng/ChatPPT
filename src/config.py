import json
import os

class Config:
    def __init__(self, config_file='config.json'):
        """
        初始化 Config 类，并从指定的 config 文件中加载配置。
        """
        self.config_file = config_file
        self.load_config()  # 加载配置文件

    def load_config(self):
        """
        从配置文件加载配置项，并设置默认值以防缺少某些键。
        """
        # 检查 config 文件是否存在
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Config file '{self.config_file}' not found.")

        with open(self.config_file, 'r') as f:
            config = json.load(f)
            
            # 加载 ChatPPT 运行模式，默认为 "text" 模式
            self.input_mode = config.get('input_mode', "text")
            
            # 加载 PPT 默认模板路径，若未指定则使用默认模板
            self.ppt_template = config.get('ppt_template', "templates/MasterTemplate.pptx")

            # 加载 ChatBot 提示信息
            self.chatbot_prompt = config.get('chatbot_prompt', '')

            # 加载内容格式化提示和助手提示
            self.content_formatter_prompt = config.get('content_formatter_prompt', '')
            self.content_assistant_prompt = config.get('content_assistant_prompt', '')
            self.image_advisor_prompt = config.get('image_advisor_prompt', '')