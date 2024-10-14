import re
from typing import Optional

from data_structures import PowerPoint
from slide_builder import SlideBuilder
from layout_manager import LayoutManager
from logger import LOG  # 引入 LOG 模块

def parse_input_text(input_text: str, layout_manager: LayoutManager) -> PowerPoint:
    """
    解析输入的文本，并将其转换为 PowerPoint 数据结构。自动为每张幻灯片分配适当的布局。
    """
    lines = input_text.split('\n')
    presentation_title = ""
    slides = []
    slide_builder: Optional[SlideBuilder] = None  # 使用 SlideBuilder

    # 正则表达式，用于匹配幻灯片标题、项目符号和图片路径
    slide_title_pattern = re.compile(r'^##\s+(.*)')
    bullet_pattern = re.compile(r'^-\s+(.*)')
    image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')

    for line in lines:
        line = line.strip()

        # 主标题 (用作 PowerPoint 的标题以及第一页的标题)
        if line.startswith('# ') and not line.startswith('##'):
            presentation_title = line[2:].strip()

            # 创建第一张幻灯片，使用 "Title Only" 布局
            first_slide_builder = SlideBuilder(layout_manager)
            first_slide_builder.set_title(presentation_title)
            slides.append(first_slide_builder.finalize())

        # 幻灯片标题
        elif line.startswith('## '):
            match = slide_title_pattern.match(line)
            if match:
                title = match.group(1).strip()

                # 如果当前 SlideBuilder 存在，生成当前幻灯片并添加到列表中
                if slide_builder:
                    slides.append(slide_builder.finalize())

                # 创建新幻灯片的构建器
                slide_builder = SlideBuilder(layout_manager)
                slide_builder.set_title(title)

        # 项目符号
        elif line.startswith('- ') and slide_builder:
            match = bullet_pattern.match(line)
            if match:
                bullet = match.group(1).strip()
                slide_builder.add_bullet_point(bullet)

        # 图片路径
        elif line.startswith('![') and slide_builder:
            match = image_pattern.match(line)
            if match:
                image_path = match.group(1).strip()
                slide_builder.set_image(image_path)

    # 为最后一张幻灯片分配布局并添加到列表中
    if slide_builder:
        slides.append(slide_builder.finalize())

    # 返回 PowerPoint 数据结构以及演示文稿标题 (作为文件名)
    return PowerPoint(title=presentation_title, slides=slides), presentation_title
