import unittest
import os
import sys

# 添加 src 目录到模块搜索路径，以便可以导入 src 目录中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from data_structures import PowerPoint, Slide, SlideContent

class TestDataStructures(unittest.TestCase):
    """
    测试 PowerPoint、Slide、SlideContent 数据类，验证数据结构的正确性。
    """

    def test_slide_content(self):
        slide_content = SlideContent(title="Test Slide", bullet_points=[{'text': "Bullet 1", 'level': 0}], image_path="images/test.png")
        self.assertEqual(slide_content.title, "Test Slide")
        self.assertEqual(slide_content.bullet_points, [{'text': "Bullet 1", 'level': 0}])
        self.assertEqual(slide_content.image_path, "images/test.png")

    def test_slide(self):
        slide_content = SlideContent(title="Slide with Layout")
        slide = Slide(layout_id=2, layout_name="Title, Content 0", content=slide_content)
        self.assertEqual(slide.layout_id, 2)
        self.assertEqual(slide.layout_name, "Title, Content 0")
        self.assertEqual(slide.content.title, "Slide with Layout")

    def test_powerpoint(self):
        slide_content1 = SlideContent(title="Slide 1")
        slide_content2 = SlideContent(title="Slide 2")
        slide1 = Slide(layout_id=1, layout_name="Title 1", content=slide_content1)
        slide2 = Slide(layout_id=2, layout_name="Title, Content 0", content=slide_content2)
        ppt = PowerPoint(title="Test Presentation", slides=[slide1, slide2])

        self.assertEqual(ppt.title, "Test Presentation")
        self.assertEqual(len(ppt.slides), 2)
        self.assertEqual(ppt.slides[0].content.title, "Slide 1")
        self.assertEqual(ppt.slides[1].content.title, "Slide 2")

if __name__ == "__main__":
    unittest.main()
