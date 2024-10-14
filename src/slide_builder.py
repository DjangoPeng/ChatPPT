from data_structures import SlideContent, Slide
from layout_manager import LayoutManager

class SlideBuilder:
    def __init__(self, layout_manager: LayoutManager):
        self.layout_manager = layout_manager
        self.title = ""
        self.bullet_points = []
        self.image_path = None
        self.layout_id = None
        self.layout_name = None

    def set_title(self, title: str):
        self.title = title

    def add_bullet_point(self, bullet: str):
        self.bullet_points.append(bullet)

    def set_image(self, image_path: str):
        self.image_path = image_path

    def finalize(self) -> Slide:
        """
        组装并返回最终的 Slide 对象，调用 LayoutManager 自动分配布局。
        """
        content = SlideContent(
            title=self.title,
            bullet_points=self.bullet_points,
            image_path=self.image_path
        )

        # 通过 LayoutManager 自动分配布局
        self.layout_id, self.layout_name = self.layout_manager.assign_layout(content)

        return Slide(layout_id=self.layout_id, layout_name=self.layout_name, content=content)
