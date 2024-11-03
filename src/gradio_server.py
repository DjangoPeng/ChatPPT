import gradio as gr
import os

from gradio.data_classes import FileData

from config import Config
from chatbot import ChatBot
from content_formatter import ContentFormatter
from content_assistant import ContentAssistant
from image_advisor import ImageAdvisor
from input_parser import parse_input_text
from ppt_generator import generate_presentation
from template_manager import load_template, get_layout_mapping
from layout_manager import LayoutManager
from logger import LOG
from openai_whisper import asr, transcribe
# from minicpm_v_model import chat_with_image
from docx_parser import generate_markdown_from_docx


os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "ChatPPT"

# 实例化 Config，加载配置文件
config = Config()
chatbot = ChatBot(config.chatbot_prompt)
content_formatter = ContentFormatter(config.content_formatter_prompt)
content_assistant = ContentAssistant(config.content_assistant_prompt)
image_advisor = ImageAdvisor(config.image_advisor_prompt)

# 加载 PowerPoint 模板，并获取可用布局
ppt_template = load_template(config.ppt_template)

# 初始化 LayoutManager，管理幻灯片布局
layout_manager = LayoutManager(get_layout_mapping(ppt_template))


# 定义生成幻灯片内容的函数
def generate_contents(message, history):
    try:
        # 初始化一个列表，用于收集用户输入的文本和音频转录
        texts = []

        # 获取文本输入，如果存在则添加到列表
        text_input = message.get("text")
        if text_input:
            texts.append(text_input)

        # 获取上传的文件列表，如果存在则处理每个文件
        for uploaded_file in message.get("files", []):
            LOG.debug(f"[上传文件]: {uploaded_file}")
            # 获取文件的扩展名，并转换为小写
            file_ext = os.path.splitext(uploaded_file)[1].lower()
            if file_ext in ('.wav', '.flac', '.mp3'):
                # 使用 OpenAI Whisper 模型进行语音识别
                audio_text = asr(uploaded_file)
                texts.append(audio_text)
            # 解释说明图像文件
            # elif file_ext in ('.jpg', '.png', '.jpeg'):
            #     if text_input:
            #         image_desc = chat_with_image(uploaded_file, text_input)
            #     else:
            #         image_desc = chat_with_image(uploaded_file)
            #     return image_desc
            # 使用 Docx 文件作为素材创建 PowerPoint
            elif file_ext in ('.docx', '.doc'):
                # 调用 generate_markdown_from_docx 函数，获取 markdown 内容
                raw_content = generate_markdown_from_docx(uploaded_file)
                markdown_content = content_formatter.format(raw_content)
                return content_assistant.adjust_single_picture(markdown_content)
            else:
                LOG.debug(f"[格式不支持]: {uploaded_file}")

        # 将所有文本和转录结果合并为一个字符串，作为用户需求
        user_requirement = "需求如下:\n" + "\n".join(texts)
        LOG.info(user_requirement)

        # 与聊天机器人进行对话，生成幻灯片内容
        slides_content = chatbot.chat_with_history(user_requirement)

        return slides_content
    except Exception as e:
        LOG.error(f"[内容生成错误]: {e}")
        # 抛出 Gradio 错误，以便在界面上显示友好的错误信息
        raise gr.Error(f"网络问题，请重试:)")
        

def handle_image_generate(history):
    try:
        # 获取聊天记录中的最新内容
        slides_content = history[-1]["content"]

        content_with_images, image_pair = image_advisor.generate_images(slides_content)
        
        # for k, v in image_pair.items():
        #     history.append(
        #         # {"text": k, "files": FileData(path=v)}
        #         {"role": "user", "files": FileData(path=v)}
        #     )

        new_message = {"role": "assistant", "content": content_with_images}

        history.append(new_message)

        return history
    except Exception as e:
        LOG.error(f"[配图生成错误]: {e}")
        # 提示用户先输入主题内容或上传文件
        raise gr.Error(f"【提示】未找到合适配图，请重试！")

# 定义处理生成按钮点击事件的函数
def handle_generate(history):
    try:
        # 获取聊天记录中的最新内容
        slides_content = history[-1]["content"]
        # 解析输入文本，生成幻灯片数据和演示文稿标题
        powerpoint_data, presentation_title = parse_input_text(slides_content, layout_manager)
        # 定义输出的 PowerPoint 文件路径
        output_pptx = f"outputs/{presentation_title}.pptx"
        
        # 生成 PowerPoint 演示文稿
        generate_presentation(powerpoint_data, config.ppt_template, output_pptx)
        return output_pptx
    except Exception as e:
        LOG.error(f"[PPT 生成错误]: {e}")
        # 提示用户先输入主题内容或上传文件
        raise gr.Error(f"【提示】请先输入你的主题内容或上传文件")

# 创建 Gradio 界面
with gr.Blocks(
    title="ChatPPT",
    css="""
    body { animation: fadeIn 2s; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    """
) as demo:

    # 添加标题
    gr.Markdown("## ChatPPT")

    # 定义语音（mic）转文本的接口
    # gr.Interface(
    #     fn=transcribe,  # 执行转录的函数
    #     inputs=[
    #         gr.Audio(sources="microphone", type="filepath"),  # 使用麦克风录制的音频输入
    #     ],
    #     outputs="text",  # 输出为文本
    #     flagging_mode="never",  # 禁用标记功能
    # )

    # 创建聊天机器人界面，提示用户输入
    contents_chatbot = gr.Chatbot(
        placeholder="<strong>AI 一键生成 PPT</strong><br><br>输入你的主题内容或上传音频文件",
        height=800,
        type="messages",
    )

    # 定义 ChatBot 和生成内容的接口
    gr.ChatInterface(
        fn=generate_contents,  # 处理用户输入的函数
        chatbot=contents_chatbot,  # 绑定的聊天机器人
        type="messages",
        multimodal=True  # 支持多模态输入（文本和文件）
    )

    image_generate_btn = gr.Button("一键为 PowerPoint 配图")

    image_generate_btn.click(
        fn=handle_image_generate,
        inputs=contents_chatbot,
        outputs=contents_chatbot,
    )

    # 创建生成 PowerPoint 的按钮
    generate_btn = gr.Button("一键生成 PowerPoint")

    # 监听生成按钮的点击事件
    generate_btn.click(
        fn=handle_generate,  # 点击时执行的函数
        inputs=contents_chatbot,  # 输入为聊天记录
        outputs=gr.File()  # 输出为文件下载链接
    )

# 主程序入口
if __name__ == "__main__":
    # 启动Gradio应用，允许队列功能，并通过 HTTPS 访问
    demo.queue().launch(
        share=False,
        server_name="0.0.0.0",
        # auth=("django", "qaz!@#$") # ⚠️注意：记住修改密码
    )