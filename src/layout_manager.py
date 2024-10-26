import random
from typing import List, Tuple
from data_structures import SlideContent
from logger import LOG

# 定义 content_type 对应的权重
CONTENT_TYPE_WEIGHTS = {
    'Title': 1,
    'Content': 2,
    'Picture': 4
}

def calculate_layout_encoding(layout_name: str) -> int:
    """
    根据 layout_name 计算其编码值。
    移除编号部分，只对类型进行编码，顺序无关。
    """
    # 移除 layout_name 中的编号部分，并按 ',' 分割
    parts = layout_name.split(', ')
    base_name = ' '.join(part.split()[0] for part in parts)  # 只保留类型部分，移除编号

    # 计算权重和
    weight_sum = sum(CONTENT_TYPE_WEIGHTS.get(part, 0) for part in base_name.split())

    return weight_sum


def calculate_content_encoding(slide_content: SlideContent) -> int:
    """
    根据 SlideContent 的成员情况计算其编码值。
    如果有 title、bullet_points 和 image_path，则根据这些成员生成编码。
    """
    encoding = 0
    if slide_content.title:
        encoding += CONTENT_TYPE_WEIGHTS['Title']
    if slide_content.bullet_points:
        encoding += CONTENT_TYPE_WEIGHTS['Content']
    if slide_content.image_path:
        encoding += CONTENT_TYPE_WEIGHTS['Picture']
    
    return encoding


# 通用的布局策略类，使用参数化的方式实现不同布局策略的功能。
class LayoutStrategy:
    """
    通用布局策略类，通过参数化方式来选择适合的布局组。
    `get_layout` 方法根据 SlideContent 内容和布局映射来返回合适的布局ID和名称。
    """
    def __init__(self, layout_group: List[Tuple[int, str]]):
        self.layout_group = layout_group  # 布局组成员，存储可选布局

    def get_layout(self, slide_content: SlideContent) -> Tuple[int, str]:
        """
        根据 SlideContent 内容随机选择一个合适的布局。
        """
        return random.choice(self.layout_group)  # 随机选择布局

# 布局管理器类，负责根据 SlideContent 自动选择合适的布局策略。
class LayoutManager:
    """
    布局管理器根据 SlideContent 的内容（如标题、要点和图片）自动选择合适的布局策略，并随机选择一个布局。
    """
    def __init__(self, layout_mapping: dict):
        self.layout_mapping = layout_mapping  # 布局映射配置
        
        # 初始化布局策略，提前为所有布局创建策略并存储在字典中
        self.strategies = {
            1: self._create_strategy(1),  # 仅 Title
            3: self._create_strategy(3),  # Title + Content
            5: self._create_strategy(5),  # Title + Picture
            7: self._create_strategy(7)   # Title + Content + Picture
        }

        # 打印调试信息
        LOG.debug(f"LayoutManager 初始化完成:\n {self}")

    def __str__(self):
        """
        打印 LayoutManager 的调试信息，包括所有布局策略及其对应的布局组。
        """
        output = []
        output.append("LayoutManager 状态:")
        for encoding, strategy in self.strategies.items():
            layout_group = strategy.layout_group
            output.append(f"  编码 {encoding}: {len(layout_group)} 个布局")
            for layout_id, layout_name in layout_group:
                output.append(f"    - Layout ID: {layout_id}, Layout Name: {layout_name}")
        return "\n".join(output)

    def assign_layout(self, slide_content: SlideContent) -> Tuple[int, str]:
        """
        根据 SlideContent 的成员情况计算编码，并选择对应的布局策略。
        """
        # 计算 SlideContent 的编码
        encoding = calculate_content_encoding(slide_content)

        # 根据编码获取对应的布局策略
        strategy = self.strategies.get(encoding)
        if not strategy:
            raise ValueError(f"没有找到对应的布局策略，编码: {encoding}")

        # 使用对应的策略获取合适的布局
        return strategy.get_layout(slide_content)

    def _create_strategy(self, layout_type: int) -> LayoutStrategy:
        """
        根据布局类型创建通用的布局策略，并生成布局组，记录布局组的 debug 信息。
        """
        layout_group = [
            (layout_id, layout_name) for layout_name, layout_id in self.layout_mapping.items() 
            if calculate_layout_encoding(layout_name) == layout_type
        ]

        # Debug 级别日志输出，查看各个布局组的详细情况
        # LOG.debug(f"创建 {layout_type} 编码对应的布局组，共 {len(layout_group)} 个布局: {layout_group}")

        return LayoutStrategy(layout_group)