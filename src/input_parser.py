import re
from typing import Optional

from data_structures import PowerPoint
from slide_builder import SlideBuilder
from layout_manager import LayoutManager
from logger import LOG  # 引入日志模块

# 解析输入文本，生成 PowerPoint 数据结构
def parse_input_text(input_text: str, layout_manager: LayoutManager) -> PowerPoint:
    """
    解析输入的文本并转换为 PowerPoint 数据结构。自动为每张幻灯片分配适当的布局。
    """
    lines = input_text.split('\n')  # 按行拆分文本
    presentation_title = ""  # PowerPoint 的主标题
    slides = []  # 存储所有幻灯片
    slide_builder: Optional[SlideBuilder] = None  # 当前幻灯片的构建器

    # 正则表达式，用于匹配幻灯片标题、要点和图片
    slide_title_pattern = re.compile(r'^##\s+(.*)')
    bullet_pattern = re.compile(r'^-\s+(.*)')
    image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')

    for line in lines:
        line = line.strip()  # 去除空格

        # 主标题 (用作 PowerPoint 的标题和文件名)
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

                # 如果有当前幻灯片，生成并添加到幻灯片列表中
                if slide_builder:
                    slides.append(slide_builder.finalize())

                # 创建新的 SlideBuilder
                slide_builder = SlideBuilder(layout_manager)
                slide_builder.set_title(title)

        # 项目符号（要点）
        elif line.startswith('- ') and slide_builder:
            match = bullet_pattern.match(line)
            if match:
                bullet = match.group(1).strip()
                slide_builder.add_bullet_point(bullet)

        # 图片插入
        elif line.startswith('![') and slide_builder:
            match = image_pattern.match(line)
            if match:
                image_path = match.group(1).strip()
                slide_builder.set_image(image_path)

    # 为最后一张幻灯片分配布局并添加到列表中
    if slide_builder:
        slides.append(slide_builder.finalize())

    # 返回 PowerPoint 数据结构以及演示文稿标题
    return PowerPoint(title=presentation_title, slides=slides), presentation_title
