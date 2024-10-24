from typing import Optional, List
from dataclasses import dataclass, field

# 定义 SlideContent 数据类，表示幻灯片的内容，包括标题、要点列表（支持多级），图片路径
@dataclass
class SlideContent:
    title: str  # 幻灯片的标题
    bullet_points: List[dict] = field(default_factory=list)  # 要点列表，包含每个要点的文本和层级
    image_path: Optional[str] = None  # 图片路径，默认为 None
# 定义 Slide 数据类，表示每张幻灯片，包括布局 ID、布局名称以及幻灯片内容。
@dataclass
class Slide:
    layout_id: int  # 布局 ID，对应 PowerPoint 模板中的布局
    layout_name: str  # 布局名称
    content: SlideContent  # 幻灯片的内容，类型为 SlideContent

# 定义 PowerPoint 数据类，表示整个 PowerPoint 演示文稿，包括标题和幻灯片列表。
@dataclass
class PowerPoint:
    title: str  # PowerPoint 演示文稿的标题
    slides: List[Slide] = field(default_factory=list)  # 幻灯片列表，默认为空列表

    # 定义 __str__ 方法，用于打印演示文稿的详细信息
    def __str__(self):
        result = [f"PowerPoint Presentation: {self.title}"]  # 打印 PowerPoint 的标题
        for idx, slide in enumerate(self.slides, start=1):
            result.append(f"\nSlide {idx}:")
            result.append(f"  Title: {slide.content.title}")  # 打印每张幻灯片的标题
            result.append(f"  Layout: {slide.layout_name} (ID: {slide.layout_id})")  # 打印布局名称和 ID

            # 打印项目符号列表
            if slide.content.bullet_points:
                bullet_point_strs = []
                for bullet_point in slide.content.bullet_points:
                    text = bullet_point['text']  # 要点文本
                    level = bullet_point['level']  # 要点层级
                    indent = '  ' * level  # 根据层级设置缩进
                    bullet_point_strs.append(f"{indent}- {text}")
                result.append("  Bullet Points:\n" + "\n".join(bullet_point_strs))  # 打印格式化后的项目符号

            # 打印图片路径
            if slide.content.image_path:
                result.append(f"  Image: {slide.content.image_path}")
        return "\n".join(result)
