import unittest
import os
import sys

# 添加 src 目录到模块搜索路径，以便可以导入 src 目录中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from layout_manager import LayoutManager
from slide_builder import SlideBuilder
from data_structures import SlideContent

class TestSlideBuilder(unittest.TestCase):
    """
    测试 SlideBuilder 类，验证幻灯片生成过程是否符合预期。
    """

    @classmethod
    def setUpClass(cls):
        # 模拟布局映射字典，只初始化一次
        layout_mapping = {"Title 1": 1, "Title, Content 0": 2, "Title, Content, Picture 2": 8}
        cls.layout_manager = LayoutManager(layout_mapping)

    def setUp(self):
        # 使用已创建的 layout_manager 实例
        self.builder = SlideBuilder(self.layout_manager)

    def test_set_title(self):
        self.builder.set_title("Test Title")
        self.assertEqual(self.builder.title, "Test Title")

    def test_add_bullet_point(self):
        self.builder.add_bullet_point("Test Bullet 1", level=0)
        self.builder.add_bullet_point("Test Bullet 2", level=1)
        self.assertEqual(self.builder.bullet_points, [{'text': "Test Bullet 1", 'level': 0}, {'text': "Test Bullet 2", 'level': 1}])

    def test_set_image(self):
        self.builder.set_image("images/test.png")
        self.assertEqual(self.builder.image_path, "images/test.png")

    def test_finalize(self):
        self.builder.set_title("Final Slide")
        self.builder.add_bullet_point("Bullet 1", level=0)
        self.builder.set_image("images/final.png")
        slide = self.builder.finalize()

        self.assertEqual(slide.content.title, "Final Slide")
        self.assertEqual(slide.content.bullet_points, [{'text': "Bullet 1", 'level': 0}])
        self.assertEqual(slide.content.image_path, "images/final.png")

if __name__ == "__main__":
    unittest.main()