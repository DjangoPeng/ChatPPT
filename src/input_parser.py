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
