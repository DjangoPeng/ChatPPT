# content_assistant.py
from abc import ABC, abstractmethod

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate  # 导入提示模板相关类
from langchain_core.messages import HumanMessage  # 导入消息类

from logger import LOG  # 导入日志工具

class ContentAssistant(ABC):
    """
    聊天机器人基类，提供聊天功能。
    """
    def __init__(self, prompt_file="./prompts/content_assistant.txt"):
        self.prompt_file = prompt_file
        self.prompt = self.load_prompt()
        # LOG.debug(f"[Formatter Prompt]{self.prompt}")
        self.create_assistant()

    def load_prompt(self):
        """
        从文件加载系统提示语。
        """
        try:
            with open(self.prompt_file, "r", encoding="utf-8") as file:
                return file.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到提示文件 {self.prompt_file}!")


    def create_assistant(self):
        """
        初始化聊天机器人，包括系统提示和消息历史记录。
        """
        # 创建聊天提示模板，包括系统提示和消息占位符
        system_prompt = ChatPromptTemplate.from_messages([
            ("system", self.prompt),  # 系统提示部分
            ("human", "{input}"),  # 消息占位符
        ])

        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.5,
            max_tokens=4096,
        )

        self.assistant = system_prompt | self.model  # 使用的模型名称)

    def adjust_single_picture(self, markdown_content):
        """
        

        参数:
            markdown_content (str): PowerPoint markdown 原始格式

        返回:
            str: 格式化后的 markdown 内容
        """
        response = self.assistant.invoke({
            "input": markdown_content,
        })

        LOG.debug(f"[Assistant 内容重构后]\n{response.content}")  # 记录调试日志
        return response.content  # 返回生成的回复内容