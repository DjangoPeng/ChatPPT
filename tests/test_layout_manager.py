import unittest
import os
import sys

# 添加 src 目录到模块搜索路径，以便可以导入 src 目录中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from layout_manager import LayoutManager
from data_structures import SlideContent

class TestLayoutManager(unittest.TestCase):
    """
    测试 LayoutManager 类，验证布局分配逻辑是否正确。
    """

    def setUp(self):
        # 模拟布局映射字典
        layout_mapping = {
            "Title 1": 1,
            "Title, Content 0": 2,
            "Title, Content, Picture 2": 8
        }
        self.layout_manager = LayoutManager(layout_mapping)

    def test_assign_layout_title_only(self):
        content = SlideContent(title="Only Title")
        layout_id, layout_name = self.layout_manager.assign_layout(content)
        self.assertEqual(layout_id, 1)
        self.assertEqual(layout_name, "Title 1")

    def test_assign_layout_title_and_content(self):
        content = SlideContent(title="Title with Content", bullet_points=[{'text': "Content Bullet", 'level': 0}])
        layout_id, layout_name = self.layout_manager.assign_layout(content)
        self.assertEqual(layout_id, 2)
        self.assertEqual(layout_name, "Title, Content 0")

    def test_assign_layout_title_content_and_image(self):
        content = SlideContent(title="Full Slide", bullet_points=[{'text': "Full Content", 'level': 0}], image_path="images/test.png")
        layout_id, layout_name = self.layout_manager.assign_layout(content)
        self.assertEqual(layout_id, 8)
        self.assertEqual(layout_name, "Title, Content, Picture 2")

if __name__ == "__main__":
    unittest.main()
