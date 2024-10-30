import os
import argparse
from input_parser import parse_input_text
from ppt_generator import generate_presentation
from template_manager import load_template, print_layouts, get_layout_mapping
from layout_manager import LayoutManager
from config import Config
from logger import LOG  # 引入 LOG 模块
from content_formatter import ContentFormatter
from content_assistant import ContentAssistant

# 新增导入 docx_parser 模块中的函数
from docx_parser import generate_markdown_from_docx

# 定义主函数，处理输入并生成 PowerPoint 演示文稿
def main(input_file):
    config = Config()  # 加载配置文件
    content_formatter = ContentFormatter()
    content_assistant = ContentAssistant()

    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        LOG.error(f"{input_file} 不存在。")  # 如果文件不存在，记录错误日志
        return

    # 根据输入文件的扩展名判断文件类型
    file_extension = os.path.splitext(input_file)[1].lower()

    if file_extension in ['.md', '.markdown']:
        # 处理 markdown 文件
        with open(input_file, 'r', encoding='utf-8') as file:
            input_text = file.read()
    elif file_extension == '.docx':
        # 处理 docx 文件
        LOG.info(f"正在解析 docx 文件: {input_file}")
        # 调用 generate_markdown_from_docx 函数，获取 markdown 内容
        raw_content = generate_markdown_from_docx(input_file)
        markdown_content = content_formatter.format(raw_content)
        input_text = content_assistant.adjust_single_picture(markdown_content)
    else:
        # 不支持的文件类型
        LOG.error(f"暂不支持的文件格式: {file_extension}")
        return

    # 加载 PowerPoint 模板，并打印模板中的可用布局
    ppt_template = load_template(config.ppt_template)  # 加载模板文件
    LOG.info("可用的幻灯片布局:")  # 记录信息日志，打印可用布局
    print_layouts(ppt_template)  # 打印模板中的布局

    # 初始化 LayoutManager，使用配置文件中的 layout_mapping
    layout_manager = LayoutManager(get_layout_mapping(ppt_template))

    # 调用 parse_input_text 函数，解析输入文本，生成 PowerPoint 数据结构
    powerpoint_data, presentation_title = parse_input_text(input_text, layout_manager)

    LOG.info(f"解析转换后的 ChatPPT PowerPoint 数据结构:\n{powerpoint_data}")  # 记录信息日志，打印解析后的 PowerPoint 数据

    # 定义输出 PowerPoint 文件的路径
    output_pptx = f"outputs/{presentation_title}.pptx"

    # 调用 generate_presentation 函数生成 PowerPoint 演示文稿
    generate_presentation(powerpoint_data, config.ppt_template, output_pptx)

# 程序入口
if __name__ == "__main__":
    # 设置命令行参数解析器
    parser = argparse.ArgumentParser(description='从 markdown 或 docx 文件生成 PowerPoint 演示文稿。')
    parser.add_argument(
        'input_file',  # 输入文件参数
        nargs='?',  # 可选参数
        default='inputs/markdown/test_input.md',  # 默认值
        help='输入 markdown 或 docx 文件的路径（默认: inputs/markdown/test_input.md）'
    )

    # 解析命令行参数
    args = parser.parse_args()

    # 使用解析后的输入文件参数运行主函数
    main(args.input_file)
