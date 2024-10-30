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


def parse_input_text(input_text: str, layout_mapping: dict) -> PowerPoint:
    lines = input_text.split('\n')
    presentation_title = ""
    slides = []
    current_slide: Optional[Slide] = None

    slide_title_pattern = re.compile(r'^##\s+(.*?)\s+\[(.*?)\]')
    bullet_pattern = re.compile(r'^-\s+(.*)')
    image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')

    print("开始解析输入文本...")
    
    for line_num, line in enumerate(lines, start=1):
        line = line.strip()
        print(f"解析第 {line_num} 行: '{line}'")
        
        if line.startswith('# ') and not line.startswith('##'):
            presentation_title = line[2:].strip()
            print(f"设置演示文稿标题: {presentation_title}")
            
        elif line.startswith('## '):
            match = slide_title_pattern.match(line)
            if match:
                title, layout_name = match.groups()
                layout_index = layout_mapping.get(layout_name.strip(), 1)
                print(f"检测到幻灯片标题: {title}, 布局: {layout_name}, 布局索引: {layout_index}")
                
                if current_slide:
                    slides.append(current_slide)
                    print(f"保存当前幻灯片: {current_slide}")
                
                current_slide = Slide(layout=layout_index, content=SlideContent(title=title.strip()))
                print(f"创建新幻灯片: {current_slide}")
                
        elif line.startswith('- ') and current_slide:
            match = bullet_pattern.match(line)
            if match:
                bullet = match.group(1).strip()
                current_slide.content.bullet_points.append(bullet)
                print(f"添加项目符号: {bullet}")
                
        elif line.startswith('![') and current_slide:
            match = image_pattern.match(line)
            if match:
                image_path = match.group(1).strip()
                current_slide.content.image_path = image_path
                print(f"添加图片路径: {image_path}")

    if current_slide:
        slides.append(current_slide)
        print(f"保存最后一张幻灯片: {current_slide}")

    print(f"解析完成。演示文稿标题: {presentation_title}, 幻灯片数: {len(slides)}")
    return PowerPoint(title=presentation_title, slides=slides), presentation_title
