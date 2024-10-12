import re
from typing import Optional, List
from data_structures import PowerPoint, Slide, SlideContent
from logger import LOG  # 引入 LOG 模块

def assign_layout_based_on_content(slide_content: SlideContent, layout_mapping: dict) -> (int, str):
    """
    根据幻灯片内容分配布局，并返回布局 ID 和名称。
    """
    if slide_content.image_path and slide_content.bullet_points:
        layout_name = 'Title, Content, and Picture'
        layout_id = layout_mapping.get(layout_name, 4)
    elif slide_content.image_path:
        layout_name = 'Title and Picture'
        layout_id = layout_mapping.get(layout_name, 3)
    elif slide_content.bullet_points:
        layout_name = 'Title and Content'
        layout_id = layout_mapping.get(layout_name, 2)
    else:
        layout_name = 'Title Only'
        layout_id = layout_mapping.get(layout_name, 1)
    
    return layout_id, layout_name


def parse_input_text(input_text: str, layout_mapping: dict) -> PowerPoint:
    """
    解析输入的文本，并将其转换为 PowerPoint 数据结构。自动为每张幻灯片分配适当的布局。
    """
    lines = input_text.split('\n')
    presentation_title = ""
    slides = []
    current_slide: Optional[Slide] = None

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
            first_slide = Slide(
                layout_id=layout_mapping.get('Title Only', 1),
                layout_name='Title Only',
                content=SlideContent(title=presentation_title)
            )
            slides.append(first_slide)  # 将第一张幻灯片添加到列表中

        # 幻灯片标题
        elif line.startswith('## '):
            match = slide_title_pattern.match(line)
            if match:
                title = match.group(1).strip()

                # 如果当前幻灯片存在，将其添加到幻灯片列表中
                if current_slide:
                    layout_id, layout_name = assign_layout_based_on_content(current_slide.content, layout_mapping)
                    current_slide.layout_id = layout_id
                    current_slide.layout_name = layout_name
                    slides.append(current_slide)

                # 创建新幻灯片，初始使用 "Title Only" 布局
                current_slide = Slide(layout_id=1, layout_name='Title Only', content=SlideContent(title=title))

        # 项目符号
        elif line.startswith('- ') and current_slide:
            match = bullet_pattern.match(line)
            if match:
                bullet = match.group(1).strip()
                current_slide.content.bullet_points.append(bullet)

        # 图片路径
        elif line.startswith('![') and current_slide:
            match = image_pattern.match(line)
            if match:
                image_path = match.group(1).strip()
                current_slide.content.image_path = image_path

    # 为最后一张幻灯片分配布局，并将其添加到幻灯片列表中
    if current_slide:
        layout_id, layout_name = assign_layout_based_on_content(current_slide.content, layout_mapping)
        current_slide.layout_id = layout_id
        current_slide.layout_name = layout_name
        slides.append(current_slide)

    # 返回 PowerPoint 数据结构以及演示文稿标题 (作为文件名)
    return PowerPoint(title=presentation_title, slides=slides), presentation_title
