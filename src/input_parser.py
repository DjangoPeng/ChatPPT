import re
from typing import Optional

from data_structures import PowerPoint
from slide_builder import SlideBuilder
from layout_manager import LayoutManager
from logger import LOG  # 引入日志模块

def parse_bullet_point_level(line: str) -> (int, str):
    """
    根据项目符号行解析其缩进层级，并返回项目符号的文本内容。
    """
    # 计算前导空格或 Tab 的数量
    indent_length = len(line) - len(line.lstrip())

    # 每 2 个空格算作一个缩进级别，或者根据实际的缩进规则
    indent_level = indent_length // 2

    LOG.debug(indent_level)
    LOG.debug(line)

    bullet_text = line.strip().lstrip('- ').strip()  # 去除 '-' 并处理前后空格，得到项目符号内容
    return indent_level, bullet_text


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
    bullet_pattern = re.compile(r'^(\s*)-\s+(.*)')
    image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')

    for line in lines:
        if line.strip() == "":
            continue  # 跳过空行

        # 主标题 (用作 PowerPoint 的标题和文件名)
        if line.startswith('# ') and not line.startswith('##'):
            presentation_title = line[2:].strip()

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
        elif bullet_pattern.match(line) and slide_builder:
            match = bullet_pattern.match(line)
            if match:
                indent_spaces, bullet = match.groups()  # 获取缩进空格和项目符号内容
                indent_level = len(indent_spaces) // 2  # 计算缩进层级，每 2 个空格为一级
                bullet_text = bullet.strip()  # 获取项目符号的文本内容

                # 根据层级添加要点
                slide_builder.add_bullet_point(bullet_text, level=indent_level)

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
