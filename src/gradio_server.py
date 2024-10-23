import gradio as gr

from config import Config
from chatbot import ChatBot
from input_parser import parse_input_text
from ppt_generator import generate_presentation
from template_manager import load_template, print_layouts, get_layout_mapping
from layout_manager import LayoutManager
from logger import LOG  # 引入 LOG 模块


config = Config()
chatbot = ChatBot(config.chatbot_prompt)
# 加载 PowerPoint 模板，并打印模板中的可用布局
ppt_template = load_template(config.ppt_template)  # 加载模板文件
LOG.info("可用的幻灯片布局:")  # 记录信息日志，打印可用布局
print_layouts(ppt_template)  # 打印模板中的布局

# 初始化 LayoutManager，使用配置文件中的 layout_mapping
layout_manager = LayoutManager(get_layout_mapping(ppt_template))


def generate_contents(message, history):
    slides_content = chatbot.chat_with_history(message["text"])
    return slides_content

# Define the function to handle the generate button click
def handle_generate(history):
    # Generate the slides content based on the chat history
    slides_content = history[-1]["content"]
    # 调用 parse_input_text 函数，解析输入文本，生成 PowerPoint 数据结构
    powerpoint_data, presentation_title = parse_input_text(slides_content, layout_manager)
    # 定义输出 PowerPoint 文件的路径
    output_pptx = f"outputs/{presentation_title}.pptx"
    
    # 调用 generate_presentation 函数生成 PowerPoint 演示文稿
    generate_presentation(powerpoint_data, config.ppt_template, output_pptx)

    return output_pptx

# Create the Gradio ChatInterface within a Blocks context
with gr.Blocks(title="ChatPPT",
               css="body { animation: fadeIn 2s; } @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }"
               ) as demo:

    gr.Markdown("## ChatPPT")  # 场景选择说明

    contents_chatbot = gr.Chatbot(
        placeholder="<strong>AI 一键生成 PPT</strong><br><br>输入你的主题内容，ChatPPT 自动生成",  # 聊天机器人的占位符
        height=800,  # 聊天窗口高度
        type="messages",
    )

    gr.ChatInterface(
        fn=generate_contents,
        chatbot=contents_chatbot,
        type="messages",
        multimodal=True
    )

    # Add a generate button to the interface
    generate_btn = gr.Button("Generate Slides")

    # Define the event listener for the generate button
    generate_btn.click(fn=handle_generate,
                       inputs=contents_chatbot,
                       outputs=gr.File(label="Generated PowerPoint File"))


if __name__ == "__main__":
    demo.launch(share=True)


    