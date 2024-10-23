import os
import argparse
from input_parser import parse_input_text
from ppt_generator import generate_presentation
from template_manager import load_template, print_layouts, get_layout_mapping
from layout_manager import LayoutManager
from config import Config
from logger import LOG  # 引入 LOG 模块

# 定义主函数，处理输入并生成 PowerPoint 演示文稿
def main(input_file):
    config = Config()  # 加载配置文件

    # 检查输入的 markdown 文件是否存在
    if not os.path.exists(input_file):
        LOG.error(f"{input_file} 不存在。")  # 如果文件不存在，记录错误日志
        return
    
    # 读取 markdown 文件的内容
    with open(input_file, 'r', encoding='utf-8') as file:
        input_text = file.read()

    # 加载 PowerPoint 模板，并打印模板中的可用布局
    ppt_template = load_template(config.ppt_template)  # 加载模板文件
    LOG.info("可用的幻灯片布局:")  # 记录信息日志，打印可用布局
    print_layouts(ppt_template)  # 打印模板中的布局

    # 初始化 LayoutManager，使用配置文件中的 layout_mapping
    layout_manager = LayoutManager(get_layout_mapping(ppt_template))

    # 调用 parse_input_text 函数，解析输入文本，生成 PowerPoint 数据结构
    powerpoint_data, presentation_title = parse_input_text(input_text, layout_manager)

    LOG.info(f"解析转换后的 ChatPPT PowerPoint 数据结构:\n{powerpoint_data}")  # 记录调试日志，打印解析后的 PowerPoint 数据

    # 定义输出 PowerPoint 文件的路径
    output_pptx = f"outputs/{presentation_title}.pptx"
    
    # 调用 generate_presentation 函数生成 PowerPoint 演示文稿
    generate_presentation(powerpoint_data, config.ppt_template, output_pptx)

# 程序入口
if __name__ == "__main__":
    # 设置命令行参数解析器
    parser = argparse.ArgumentParser(description='从 markdown 文件生成 PowerPoint 演示文稿。')
    parser.add_argument(
        'input_file',  # 输入文件参数
        nargs='?',  # 可选参数
        default='inputs/test_input.md',  # 默认值为 'inputs/test_input.md'
        help='输入 markdown 文件的路径（默认: inputs/test_input.md）'
    )
    
    # 解析命令行参数
    args = parser.parse_args()

    # 使用解析后的输入文件参数运行主函数
    main(args.input_file)