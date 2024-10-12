from typing import Optional, List
from dataclasses import dataclass, field

@dataclass
class SlideContent:
    title: str
    bullet_points: List[str] = field(default_factory=list)
    image_path: Optional[str] = None

@dataclass
class Slide:
    layout_id: int
    layout_name: str
    content: SlideContent

@dataclass
class PowerPoint:
    title: str
    slides: List[Slide] = field(default_factory=list)

    def __str__(self):
        result = [f"PowerPoint Presentation: {self.title}"]
        for idx, slide in enumerate(self.slides, start=1):
            result.append(f"\nSlide {idx}:")
            result.append(f"  Title: {slide.content.title}")
            result.append(f"  Layout: {slide.layout_name} (ID: {slide.layout_id})")
            if slide.content.bullet_points:
                result.append(f"  Bullet Points: {', '.join(slide.content.bullet_points)}")
            if slide.content.image_path:
                result.append(f"  Image: {slide.content.image_path}")
        return "\n".join(result)
