import unittest
import os
import sys

# 添加 src 目录到模块搜索路径，以便可以导入 src 目录中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from docx_parser import generate_markdown_from_docx

class TestGenerateMarkdownFromDocx(unittest.TestCase):
    """
    测试从 docx 文件生成 Markdown 格式内容的功能。
    """

    def setUp(self):
        """
        在每个测试方法执行前运行。用于准备测试所需的文件和目录。
        """
        # 定义测试 docx 文件的路径
        self.test_docx_filename = 'inputs/docx/multimodal_llm_overview.docx'

        # 生成 Markdown 内容
        self.generated_markdown = generate_markdown_from_docx(self.test_docx_filename)

    def test_generated_markdown_content(self):
        """
        测试生成的 Markdown 内容是否符合预期。
        """
        # 期望的 Markdown 输出内容
        expected_markdown = """
# 多模态大模型概述

多模态大模型是指能够处理多种数据模态（如文本、图像、音频等）的人工智能模型。它们在自然语言处理、计算机视觉等领域有广泛的应用。

## 1. 多模态大模型的特点

- 支持多种数据类型：
- 跨模态学习能力：
- 广泛的应用场景：
### 1.1 支持多种数据类型

多模态大模型能够同时处理文本、图像、音频等多种类型的数据，实现数据的融合。

## 2. 多模态模型架构

以下是多模态模型的典型架构示意图：

![图片1](images/multimodal_llm_overview/1.png)

TransFormer 架构图：

![图片2](images/multimodal_llm_overview/2.png)

### 2.1 模态融合技术

通过模态融合，可以提升模型对复杂数据的理解能力。

关键技术：注意力机制、Transformer架构等。

- 应用领域：
  - 自然语言处理：
    - 机器翻译、文本生成等。
  - 计算机视觉：
    - 图像识别、目标检测等。
## 3. 未来展望

多模态大模型将在人工智能领域持续发挥重要作用，推动技术创新。
"""

        # 比较生成的 Markdown 内容与预期内容
        self.assertEqual(self.generated_markdown.strip(), expected_markdown.strip(), "生成的 Markdown 内容与预期不匹配")

    def tearDown(self):
        """
        在每个测试方法执行后运行。用于清理测试产生的文件和目录。
        """
        # 获取图像目录路径
        images_dir = 'images/multimodal_llm_overview'
        # 删除生成的图像文件和目录
        if os.path.exists(images_dir):
            for filename in os.listdir(images_dir):
                file_path = os.path.join(images_dir, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)  # 删除文件
            os.rmdir(images_dir)  # 删除目录

if __name__ == '__main__':
    unittest.main()
