import unittest
import os
import sys

# 添加 src 目录到模块搜索路径，以便可以导入 src 目录中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from layout_manager import LayoutManager
from data_structures import PowerPoint
from input_parser import parse_input_text

class TestInputParser(unittest.TestCase):
    """
    测试 input_parser 模块，检查解析输入文本生成 PowerPoint 数据结构的功能。
    """

    def setUp(self):
        """
        初始化测试设置，读取输入文件并创建 LayoutManager 实例。
        """
        # 模拟布局映射字典
        self.layout_mapping = {
            "Title 1": 1,
            "Title, Content 0": 2,
            "Title, Content, Picture 2": 8,
        }
        self.layout_manager = LayoutManager(self.layout_mapping)

        # 读取测试输入文件
        input_file_path = 'inputs/markdown/test_input.md'
        with open(input_file_path, 'r', encoding='utf-8') as f:
            self.input_text = f.read()

    def test_parse_input_text(self):
        """
        测试 parse_input_text 函数生成的 PowerPoint 数据结构是否符合预期。
        """
        # 解析输入文本
        presentation, presentation_title = parse_input_text(self.input_text, self.layout_manager)

        # 期望的 PowerPoint 数据结构
        expected_presentation_title = "ChatPPT Demo"
        expected_slides = [
            {
                "title": "ChatPPT Demo",
                "layout_id": 1,
                "layout_name": "Title 1",
                "bullet_points": [],
                "image_path": None,
            },
            {
                "title": "2024 业绩概述",
                "layout_id": 2,
                "layout_name": "Title, Content 0",
                "bullet_points": [
                    {"text": "总收入增长15%", "level": 0},
                    {"text": "市场份额扩大至30%", "level": 0},
                ],
                "image_path": None,
            },
            {
                "title": "业绩图表",
                "layout_id": 8,
                "layout_name": "Title, Content, Picture 2",
                "bullet_points": [
                    {"text": "OpenAI 利润不断增加", "level": 0},
                ],
                "image_path": "images/performance_chart.png",
            },
            {
                "title": "新产品发布",
                "layout_id": 8,
                "layout_name": "Title, Content, Picture 2",
                "bullet_points": [
                    {"text": "产品A: **特色功能介绍**", "level": 0},
                    {"text": "增长潜力巨大", "level": 1},
                    {"text": "新兴市场", "level": 1},
                    {"text": "**非洲**市场", "level": 2},
                    {"text": "**东南亚**市场", "level": 2},
                    {"text": "产品B: 市场定位", "level": 0},
                ],
                "image_path": "images/forecast.png",
            },
        ]

        # 检查演示文稿标题是否匹配
        self.assertEqual(presentation_title, expected_presentation_title)

        # 检查幻灯片数量是否匹配
        self.assertEqual(len(presentation.slides), len(expected_slides))

        # 检查每张幻灯片的内容是否符合预期
        for slide, expected in zip(presentation.slides, expected_slides):
            self.assertEqual(slide.content.title, expected["title"])
            self.assertEqual(slide.layout_id, expected["layout_id"])
            self.assertEqual(slide.layout_name, expected["layout_name"])

            # 检查每个要点是否符合预期
            bullet_points = slide.content.bullet_points
            expected_bullet_points = expected["bullet_points"]
            self.assertEqual(len(bullet_points), len(expected_bullet_points))
            for bullet, expected_bullet in zip(bullet_points, expected_bullet_points):
                self.assertEqual(bullet["text"], expected_bullet["text"])
                self.assertEqual(bullet["level"], expected_bullet["level"])

            # 检查图片路径是否符合预期
            self.assertEqual(slide.content.image_path, expected["image_path"])

if __name__ == '__main__':
    unittest.main()