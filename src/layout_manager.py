from abc import ABC, abstractmethod
from typing import Tuple

from data_structures import SlideContent

class LayoutStrategy(ABC):
    """
    抽象布局策略基类，所有布局策略都需要继承该类，并实现 `get_layout` 方法。
    """
    @abstractmethod
    def get_layout(self, slide_content: SlideContent, layout_mapping: dict) -> Tuple[int, str]:
        pass


class TitleOnlyStrategy(LayoutStrategy):
    def get_layout(self, slide_content: SlideContent, layout_mapping: dict) -> Tuple[int, str]:
        layout_name = 'Title Only'
        layout_id = layout_mapping.get(layout_name, 1)
        return layout_id, layout_name


class TitleAndContentStrategy(LayoutStrategy):
    def get_layout(self, slide_content: SlideContent, layout_mapping: dict) -> Tuple[int, str]:
        layout_name = 'Title and Content'
        layout_id = layout_mapping.get(layout_name, 2)
        return layout_id, layout_name


class TitleAndPictureStrategy(LayoutStrategy):
    def get_layout(self, slide_content: SlideContent, layout_mapping: dict) -> Tuple[int, str]:
        layout_name = 'Title and Picture'
        layout_id = layout_mapping.get(layout_name, 3)
        return layout_id, layout_name


class TitleContentAndPictureStrategy(LayoutStrategy):
    def get_layout(self, slide_content: SlideContent, layout_mapping: dict) -> Tuple[int, str]:
        layout_name = 'Title, Content, and Picture'
        layout_id = layout_mapping.get(layout_name, 4)
        return layout_id, layout_name

class LayoutManager:
    """
    布局管理器，根据 SlideContent 的内容自动选择合适的布局策略。
    """
    def __init__(self, layout_mapping: dict):
        self.layout_mapping = layout_mapping
        self.strategies = {
            'Title Only': TitleOnlyStrategy(),
            'Title and Content': TitleAndContentStrategy(),
            'Title and Picture': TitleAndPictureStrategy(),
            'Title, Content, and Picture': TitleContentAndPictureStrategy()
        }

    def assign_layout(self, slide_content: SlideContent) -> Tuple[int, str]:
        """
        根据内容自动选择适当的布局策略。
        """
        if slide_content.image_path and slide_content.bullet_points:
            strategy = self.strategies['Title, Content, and Picture']
        elif slide_content.image_path:
            strategy = self.strategies['Title and Picture']
        elif slide_content.bullet_points:
            strategy = self.strategies['Title and Content']
        else:
            strategy = self.strategies['Title Only']
        
        return strategy.get_layout(slide_content, self.layout_mapping)
