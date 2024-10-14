import os
import argparse
from input_parser import parse_input_text
from ppt_generator import generate_presentation
from template_manager import load_template, get_layout_mapping, print_layouts
from layout_manager import LayoutManager
from config import Config
from logger import LOG  # 引入 LOG 模块


def main(input_file):
    config = Config()

    # 检查文件是否存在
    if not os.path.exists(input_file):
        LOG.error(f"{input_file} 不存在。")
        return
    
    # 读取 markdown 文件
    with open(input_file, 'r', encoding='utf-8') as file:
        input_text = file.read()

    # 加载 PPT 模板，并打印模板中的可用布局
    prs = load_template(config.ppt_template)
    LOG.info("可用的幻灯片布局:")
    print_layouts(prs)
    layout_mapping = get_layout_mapping(prs)

    # 初始化 LayoutManager，使用 config 中的 layout_mapping
    layout_manager = LayoutManager(config.layout_mapping)

    # 调用 parse_input_text，传递 layout_manager 实例
    powerpoint_data, presentation_title = parse_input_text(input_text, layout_manager)

    LOG.debug(f"解析的 PowerPoint 数据: {powerpoint_data}")

    # 定义输出 PowerPoint 路径
    output_pptx = f"outputs/{presentation_title}.pptx"
    
    # 生成演示文稿
    generate_presentation(powerpoint_data, config.ppt_template, output_pptx)

if __name__ == "__main__":
    # 设置参数解析器
    parser = argparse.ArgumentParser(description='从 markdown 文件生成 PowerPoint 演示文稿。')
    parser.add_argument(
        'input_file',
        nargs='?',
        default='inputs/test_input.md',
        help='输入 markdown 文件的路径（默认: inputs/test_input.md）'
    )
    
    # 解析参数
    args = parser.parse_args()

    # 使用输入文件参数运行主函数
    main(args.input_file)
