from abc import ABC, abstractmethod
from typing import Tuple

from data_structures import SlideContent

# TODO: 为每一种布局策略（LayoutStrategy 子类）准备一组候选的布局组（LayoutGroup）。
# TODO：定义布局策略标准，扩充母版库时校验布局名称（LayoutName）和占位符（Placeholder）。
# 抽象布局策略基类，所有布局策略都需要继承该类，并实现 get_layout 方法。
class LayoutStrategy(ABC):
    """
    抽象布局策略基类，所有布局策略都需要继承该类，并实现 `get_layout` 方法。
    `get_layout` 方法根据 SlideContent 内容和布局映射来返回合适的布局ID和名称。
    """
    @abstractmethod
    def get_layout(self, slide_content: SlideContent, layout_mapping: dict) -> Tuple[int, str]:
        pass

# TitleOnlyStrategy 类，表示只包含标题的布局策略。
class TitleOnlyStrategy(LayoutStrategy):
    def get_layout(self, slide_content: SlideContent, layout_mapping: dict) -> Tuple[int, str]:
        layout_name = 'Title Only'  # 布局名称为 "Title Only"
        layout_id = layout_mapping.get(layout_name, 1)  # 获取布局 ID，默认值为 1
        return layout_id, layout_name

# TitleAndContentStrategy 类，表示包含标题和内容的布局策略。
class TitleAndContentStrategy(LayoutStrategy):
    def get_layout(self, slide_content: SlideContent, layout_mapping: dict) -> Tuple[int, str]:
        layout_name = 'Title and Content'  # 布局名称为 "Title and Content"
        layout_id = layout_mapping.get(layout_name, 2)  # 获取布局 ID，默认值为 2
        return layout_id, layout_name

# TitleAndPictureStrategy 类，表示包含标题和图片的布局策略。
class TitleAndPictureStrategy(LayoutStrategy):
    def get_layout(self, slide_content: SlideContent, layout_mapping: dict) -> Tuple[int, str]:
        layout_name = 'Title and Picture'  # 布局名称为 "Title and Picture"
        layout_id = layout_mapping.get(layout_name, 3)  # 获取布局 ID，默认值为 3
        return layout_id, layout_name

# TitleContentAndPictureStrategy 类，表示包含标题、内容和图片的布局策略。
class TitleContentAndPictureStrategy(LayoutStrategy):
    def get_layout(self, slide_content: SlideContent, layout_mapping: dict) -> Tuple[int, str]:
        layout_name = 'Title, Content, and Picture'  # 布局名称为 "Title, Content, and Picture"
        layout_id = layout_mapping.get(layout_name, 4)  # 获取布局 ID，默认值为 4
        return layout_id, layout_name

# 布局管理器类，负责根据 SlideContent 自动选择合适的布局策略。
class LayoutManager:
    """
    布局管理器根据 SlideContent 的内容（如标题、要点和图片）自动选择合适的布局策略。
    """
    def __init__(self, layout_mapping: dict):
        self.layout_mapping = layout_mapping  # 布局映射配置
        # 定义四种不同的布局策略
        self.strategies = {
            'Title Only': TitleOnlyStrategy(),
            'Title and Content': TitleAndContentStrategy(),
            'Title and Picture': TitleAndPictureStrategy(),
            'Title, Content, and Picture': TitleContentAndPictureStrategy()
        }

    def assign_layout(self, slide_content: SlideContent) -> Tuple[int, str]:
        """
        根据 SlideContent 的具体内容（标题、要点和图片）自动选择最合适的布局策略。
        """
        # 如果既有图片又有要点，则使用 "Title, Content, and Picture" 布局
        if slide_content.image_path and slide_content.bullet_points:
            strategy = self.strategies['Title, Content, and Picture']
        # 如果只有图片，则使用 "Title and Picture" 布局
        elif slide_content.image_path:
            strategy = self.strategies['Title and Picture']
        # 如果只有要点，则使用 "Title and Content" 布局
        elif slide_content.bullet_points:
            strategy = self.strategies['Title and Content']
        # 否则使用 "Title Only" 布局
        else:
            strategy = self.strategies['Title Only']
        
        # 返回选择的布局的 ID 和名称
        return strategy.get_layout(slide_content, self.layout_mapping)
