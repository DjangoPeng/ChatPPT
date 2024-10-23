import gradio as gr

from config import Config
from chatbot import ChatBot


config = Config()
chatbot = ChatBot(config.chatbot_prompt)


def generate_contents(message, history):
    slides_content = chatbot.chat_with_history(message["text"])
    return slides_content

demo = gr.ChatInterface(
    fn=generate_contents,
    type="messages",
    examples=[{"text": "AI 一键生成 PPT：输入你的主题", "files": []}],
    title="ChatPPT",
    multimodal=True
    )


if __name__ == "__main__":
    demo.launch(share=True)


    