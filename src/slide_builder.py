from data_structures import SlideContent, Slide
from layout_manager import LayoutManager

# SlideBuilder 类用于构建单张幻灯片并通过 LayoutManager 自动分配布局
class SlideBuilder:
    def __init__(self, layout_manager: LayoutManager):
        self.layout_manager = layout_manager  # 布局管理器实例
        self.title = ""  # 幻灯片标题
        self.bullet_points = []  # 幻灯片要点列表，支持多级结构
        self.image_path = None  # 幻灯片图片路径
        self.layout_id = None  # 布局ID
        self.layout_name = None  # 布局名称

    def set_title(self, title: str):
        self.title = title  # 设置幻灯片的标题

    def add_bullet_point(self, bullet: str, level: int = 0):
        """
        添加项目符号及其级别到 bullet_points 列表中。
        :param bullet: 要点文本
        :param level: 项目符号的层级，默认为 0（一级）
        """
        self.bullet_points.append({'text': bullet, 'level': level})  # 添加要点和层级

    def set_image(self, image_path: str):
        self.image_path = image_path  # 设置图片路径

    def finalize(self) -> Slide:
        """
        组装并返回最终的 Slide 对象，调用 LayoutManager 自动分配布局。
        """
        # 创建 SlideContent 对象，注意 bullet_points 现在是字典列表，包含 text 和 level 信息
        content = SlideContent(
            title=self.title,
            bullet_points=self.bullet_points,
            image_path=self.image_path
        )

        # 调用 LayoutManager 分配布局
        self.layout_id, self.layout_name = self.layout_manager.assign_layout(content)

        # 返回最终的 Slide 对象
        return Slide(layout_id=self.layout_id, layout_name=self.layout_name, content=content)
