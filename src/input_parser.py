import re
from typing import Optional, List
from dataclasses import dataclass, field

@dataclass
class SlideContent:
    title: str
    bullet_points: List[str] = field(default_factory=list)
    image_path: Optional[str] = None

@dataclass
class Slide:
    layout: int
    content: SlideContent

@dataclass
class PowerPoint:
    title: str
    slides: List[Slide] = field(default_factory=list)


def convert_user_input_to_standard_format(user_input: str) -> str:
    """
    将用户输入的原始格式转换为标准的输入文本格式，供 parse_input_text 使用。
    
    参数:
    user_input (str): 用户提供的原始格式文本
    
    返回:
    str: 标准格式文本
    """
    # 用于存储转换后的结果
    converted_text = []
    
    # 正则表达式模式
    slide_pattern = re.compile(r'^- \*\*Slide \d+\*\*:.*$', re.MULTILINE)
    title_pattern = re.compile(r'\*\*Title\*\*: (.*)')
    points_pattern = re.compile(r'\*\*Key Points\*\*:.*$', re.MULTILINE)
    notes_pattern = re.compile(r'\*\*Notes\*\*:.*$', re.MULTILINE)
    
    # 分割出每张幻灯片
    slides = slide_pattern.split(user_input)
    
    # 遍历每张幻灯片
    for slide in slides:
        # 找到标题
        title_match = title_pattern.search(slide)
        if title_match:
            title = title_match.group(1).strip()
            converted_text.append(f"## {title} [Title and Content 3]")
        
        # 找到要点
        points_section = points_pattern.split(slide)
        if len(points_section) > 1:
            points = points_section[1].strip().split('\n')
            for point in points:
                # 检查是否是要点
                if point.strip().startswith('1.') or point.strip().startswith('2.') or point.strip().startswith('3.'):
                    point_cleaned = point.strip()[3:].strip()
                    converted_text.append(f"- {point_cleaned}")
        
        # 处理附加的图片、图表建议
        notes_section = notes_pattern.split(slide)
        if len(notes_section) > 1:
            notes = notes_section[1].strip().split('\n')
            for note in notes:
                # 检查是否是图片或图表的推荐
                if note.lower().startswith('image:') or note.lower().startswith('chart:'):
                    note_cleaned = note.split(':', 1)[1].strip()
                    converted_text.append(f"![{note_cleaned}]({note_cleaned})")

    return '\n'.join(converted_text)


def parse_input_text(input_text: str, layout_mapping: dict) -> PowerPoint:
    lines = input_text.split('\n')
    presentation_title = ""
    slides = []
    current_slide: Optional[Slide] = None

    slide_title_pattern = re.compile(r'^##\s+(.*?)\s+\[(.*?)\]')
    bullet_pattern = re.compile(r'^-\s+(.*)')
    image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')

    for line in lines:
        line = line.strip()
        if line.startswith('# ') and not line.startswith('##'):
            presentation_title = line[2:].strip()
        elif line.startswith('## '):
            match = slide_title_pattern.match(line)
            if match:
                title, layout_name = match.groups()
                layout_index = layout_mapping.get(layout_name.strip(), 1)
                if current_slide:
                    slides.append(current_slide)
                current_slide = Slide(layout=layout_index, content=SlideContent(title=title.strip()))
        elif line.startswith('- ') and current_slide:
            match = bullet_pattern.match(line)
            if match:
                bullet = match.group(1).strip()
                current_slide.content.bullet_points.append(bullet)
        elif line.startswith('![') and current_slide:
            match = image_pattern.match(line)
            if match:
                image_path = match.group(1).strip()
                current_slide.content.image_path = image_path

    if current_slide:
        slides.append(current_slide)

    return PowerPoint(title=presentation_title, slides=slides), presentation_title
