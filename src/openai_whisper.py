from transformers import pipeline
import gradio as gr
import torch
import tempfile
import os
import subprocess

from logger import LOG

# 模型名称和参数配置
MODEL_NAME = "openai/whisper-large-v3"  # Whisper 模型名称
BATCH_SIZE = 8  # 处理批次大小

# 检查是否可以使用 GPU，否则使用 CPU
device = "cuda:0" if torch.cuda.is_available() else "cpu"

# 初始化语音识别管道
pipe = pipeline(
    task="automatic-speech-recognition",  # 自动语音识别任务
    model=MODEL_NAME,  # 指定模型
    chunk_length_s=60,  # 每个音频片段的长度（秒）
    device=device,  # 指定设备
)

def convert_to_wav(input_path):
    """
    将音频文件转换为 WAV 格式并返回新文件路径。

    参数:
    - input_path: 输入的音频文件路径

    返回:
    - output_path: 转换后的 WAV 文件路径
    """
    # 创建临时 WAV 文件，用于存储转换结果
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav_file:
        output_path = temp_wav_file.name

    try:
        # 使用 ffmpeg 将音频文件转换为指定格式
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", output_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return output_path
    except subprocess.CalledProcessError as e:
        LOG.error(f"音频文件转换失败: {e}")
        # 如果转换失败，删除临时文件并抛出错误
        if os.path.exists(output_path):
            os.remove(output_path)
        raise gr.Error("音频文件转换失败。请上传有效的音频文件。")
    except FileNotFoundError:
        LOG.error("未找到 ffmpeg 可执行文件。请确保已安装 ffmpeg。")
        if os.path.exists(output_path):
            os.remove(output_path)
        raise gr.Error("服务器配置错误，缺少 ffmpeg。请联系管理员。")

def asr(audio_file, task="transcribe"):
    """
    对音频文件进行语音识别或翻译。

    参数:
    - audio_file: 输入的音频文件路径
    - task: 任务类型（"transcribe" 表示转录，"translate" 表示翻译）

    返回:
    - text: 识别或翻译后的文本内容
    """
    # 转换音频文件为 WAV 格式
    wav_file = convert_to_wav(audio_file)

    try:
        # 使用管道进行转录或翻译
        result = pipe(
            wav_file,
            batch_size=BATCH_SIZE,
            generate_kwargs={"task": task},
            return_timestamps=True
        )
        text = result["text"]
        LOG.info(f"[识别结果]：{text}")

        return text
    except Exception as e:
        LOG.error(f"处理音频文件时出错: {e}")
        raise gr.Error(f"处理音频文件时出错：{str(e)}")
    finally:
        # 删除临时转换后的 WAV 文件
        if os.path.exists(wav_file):
            os.remove(wav_file)

def transcribe(inputs, task):
    """
    将音频文件转录或翻译为文本。

    参数:
    - inputs: 上传的音频文件路径
    - task: 任务类型（"transcribe" 表示转录，"translate" 表示翻译）

    返回:
    - 识别的文本内容
    """
    LOG.info(f"[上传的音频文件]: {inputs}")

    # 检查是否提供了音频文件
    if not inputs or not os.path.exists(inputs):
        raise gr.Error("未提交音频文件！请在提交请求前上传或录制音频文件。")

    # 检查音频文件格式
    file_ext = os.path.splitext(inputs)[1].lower()
    if file_ext not in ['.wav', '.flac', '.mp3']:
        LOG.error(f"文件格式错误：{inputs}")
        raise gr.Error("不支持的文件格式！请上传 WAV、FLAC 或 MP3 文件。")

    # 调用语音识别或翻译函数
    return asr(inputs, task)

# 定义麦克风输入的接口实例，可供外部模块调用
mf_transcribe = gr.Interface(
    fn=transcribe,  # 执行转录的函数
    inputs=[
        gr.Audio(sources="microphone", type="filepath", label="麦克风输入"),  # 使用麦克风录制的音频输入
        gr.Radio(["transcribe", "translate"], label="任务类型", value="transcribe"),  # 任务选择（转录或翻译）
    ],
    outputs="text",  # 输出为文本
    title="Whisper Large V3: 语音识别",  # 接口标题
    description="使用麦克风录制音频并进行语音识别或翻译。",  # 接口描述
    flagging_mode="never",  # 禁用标记功能
)

# 定义文件上传的接口实例，用于处理上传的音频文件
file_transcribe = gr.Interface(
    fn=transcribe,  # 执行转录的函数
    inputs=[
        gr.Audio(sources="upload", type="filepath", label="上传音频文件"),  # 上传的音频文件输入
        gr.Radio(["transcribe", "translate"], label="任务类型", value="transcribe"),  # 任务选择（转录或翻译）
    ],
    outputs="text",  # 输出为文本
    title="Whisper Large V3: 转录音频文件",  # 接口标题
    description="上传音频文件（WAV、FLAC 或 MP3）并进行语音识别或翻译。",  # 接口描述
    flagging_mode="never",  # 禁用标记功能
)

# 仅当此脚本作为主程序运行时，执行 Gradio 应用的启动代码
if __name__ == "__main__":
    # 创建一个 Gradio Blocks 实例，用于包含多个接口
    with gr.Blocks() as demo:
        # 使用 TabbedInterface 将 mf_transcribe 和 file_transcribe 接口分别放置在 "麦克风" 和 "音频文件" 选项卡中
        gr.TabbedInterface(
            [mf_transcribe, file_transcribe],
            ["麦克风", "音频文件"]
        )

    # 启动Gradio应用，允许队列功能，并通过 HTTPS 访问
    demo.queue().launch(
        share=False,
        server_name="0.0.0.0",
        # auth=("django", "1234") # ⚠️注意：记住修改密码
    )
