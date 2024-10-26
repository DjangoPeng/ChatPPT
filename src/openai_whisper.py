from transformers import pipeline
from transformers.pipelines.audio_utils import ffmpeg_read

import gradio as gr
import torch
import tempfile
import os
import subprocess

from logger import LOG

# 模型名称和参数配置
MODEL_NAME = "openai/whisper-large-v3"  # Whisper模型名称
BATCH_SIZE = 8  # 处理批次大小

# 检查是否可以使用GPU，否则使用CPU
device = "cuda:0" if torch.cuda.is_available() else "cpu"

# 初始化语音识别管道
pipe = pipeline(
    task="automatic-speech-recognition",  # 自动语音识别任务
    model=MODEL_NAME,  # 指定模型
    chunk_length_s=60,  # 每个音频片段的长度（秒）
    device=device,  # 指定设备
)

def convert_to_wav(input_path):
    """将音频文件转换为wav格式并返回新文件路径"""
    output_path = tempfile.mktemp(suffix=".wav")  # 创建临时wav文件路径
    try:
        subprocess.run(
            ["ffmpeg", "-i", input_path, "-ar", "16000", "-ac", "1", output_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return output_path
    except subprocess.CalledProcessError as e:
        LOG.error(f"音频文件转换失败: {e}")
        raise gr.Error("Audio conversion failed. Please upload a valid audio file.")

# 定义transcribe函数，用于执行语音转录任务
def transcribe(inputs, task):
    """
    将音频文件转录或翻译为文本。
    
    参数:
    - inputs: 上传的音频文件路径
    - task: 任务类型（"transcribe" 表示转录, "translate" 表示翻译）
    
    返回:
    - 识别的文本内容
    """
    LOG.info(f"[上传音频文件]: {inputs}")

    if inputs is None:
        raise gr.Error("No audio file submitted! Please upload or record an audio file before submitting your request.")
    
    # 检查音频文件格式
    if not inputs.lower().endswith(('.wav', '.flac', '.mp3')):
        LOG.error(f"文件格式错误：{inputs}")
        raise gr.Error("Unsupported file format! Please upload a WAV, FLAC, or MP3 file.")

    # 转换音频文件为wav格式
    wav_path = convert_to_wav(inputs)

    try:
        # 使用管道进行转录或翻译
        text = pipe(wav_path, batch_size=BATCH_SIZE, generate_kwargs={"task": task}, return_timestamps=True)["text"]
        LOG.info(f"[Transcribe]:{text}")

        return text
    except ValueError as e:
        raise gr.Error(f"Error processing audio file: {str(e)}")
    finally:
        # 删除临时转换后的wav文件
        if os.path.exists(wav_path):
            os.remove(wav_path)

# 定义 mf_transcribe 接口实例，可供外部模块调用
mf_transcribe = gr.Interface(
    fn=transcribe,  # 执行转录的函数
    inputs=[
        gr.Audio(sources="microphone", type="filepath"),  # 使用麦克风录制的音频输入
        gr.Radio(["transcribe", "translate"], label="Task", value="transcribe"),  # 任务选择（转录或翻译）
    ],
    outputs="text",  # 输出为文本
    title="Whisper Large V3: 语音识别",  # 接口标题
    flagging_mode="never",  # 禁用标记功能
)

# 定义 file_transcribe 接口实例，用于处理上传的音频文件
file_transcribe = gr.Interface(
    fn=transcribe,  # 执行转录的函数
    inputs=[
        gr.Audio(sources="upload", type="filepath", label="Audio file"),  # 上传的音频文件输入
        gr.Radio(["transcribe", "translate"], label="Task", value="transcribe"),  # 任务选择（转录或翻译）
    ],
    outputs="text",  # 输出为文本
    title="Whisper Large V3: 转录音频(e.g. wav, flac or mp3）",  # 接口标题
    flagging_mode="never",  # 禁用标记功能
)

# 仅当此脚本作为主入口运行时，执行Gradio应用的启动代码
if __name__ == "__main__":
    # 创建一个Gradio Blocks实例，用于包含多个接口
    demo = gr.Blocks()
    with demo:
        # 使用 TabbedInterface 将mf_transcribe和file_transcribe接口分别放置在"Microphone"和"Audio file"选项卡中
        gr.TabbedInterface([mf_transcribe, file_transcribe], ["麦克风", "音频文件"])

    # 启动Gradio应用，允许队列功能，并通过 HTTPS 访问
    demo.queue().launch(
        share=False,
        server_name="0.0.0.0",
        auth=("django", "1234") # ⚠️注意：记住修改密码
    )
