import os
import argparse
from input_parser import parse_input_text
from ppt_generator import generate_presentation
from template_manager import load_template, get_layout_mapping, print_layouts

from logger import LOG  # 引入 LOG 模块

def main(input_file):
    # 检查文件是否存在
    if not os.path.exists(input_file):
        LOG.error(f"{input_file} 不存在。")
        return
    
    # 读取 markdown 文件
    with open(input_file, 'r', encoding='utf-8') as file:
        input_text = file.read()

    template_file = 'templates/MasterTemplate.pptx'
    prs = load_template(template_file)

    LOG.info("可用的幻灯片布局:")
    print_layouts(prs)

    layout_mapping = get_layout_mapping(prs)

    powerpoint_data, presentation_title = parse_input_text(input_text, layout_mapping)
    LOG.debug(f"解析的 PowerPoint 数据: {powerpoint_data}")

    # 定义输出 PowerPoint 路径
    output_pptx = f"outputs/{presentation_title}.pptx"
    
    # 生成演示文稿
    generate_presentation(powerpoint_data, template_file, output_pptx)

if __name__ == "__main__":
    # 设置参数解析器
    parser = argparse.ArgumentParser(description='从 markdown 文件生成 PowerPoint 演示文稿。')
    parser.add_argument(
        'input_file',
        nargs='?',
        default='inputs/openai_canvas_intro.md',
        help='输入 markdown 文件的路径（默认: inputs/openai_canvas_intro.md）'
    )
    
    # 解析参数
    args = parser.parse_args()

    # 使用输入文件参数运行主函数
    main(args.input_file)
