import os
from docx import Document
from docx.oxml.ns import qn
from PIL import Image
from io import BytesIO

from logger import LOG  # 引入日志模块，用于记录调试信息

def is_paragraph_list_item(paragraph):
    """
    检查段落是否为列表项。
    判断依据是段落的样式名称是否包含 'list bullet' 或 'list number'，
    分别对应项目符号列表和编号列表。
    """
    style_name = paragraph.style.name.lower()
    return 'list bullet' in style_name or 'list number' in style_name

def get_paragraph_list_level(paragraph):
    """
    获取段落的列表级别（缩进层级）。
    首先尝试通过 XML 结构判断，如果无法获取，则通过样式名称中的数字判断。
    """
    p = paragraph._p
    numPr = p.find(qn('w:numPr'))
    if numPr is not None:
        ilvl = numPr.find(qn('w:ilvl'))
        if ilvl is not None:
            return int(ilvl.get(qn('w:val')))
    
    style_name = paragraph.style.name.lower()
    if 'list bullet' in style_name or 'list number' in style_name:
        for word in style_name.split():
            if word.isdigit():
                return int(word) - 1
    return 0

def generate_markdown_from_docx(docx_filename):
    """
    从指定的 docx 文件生成 Markdown 格式的内容，并将所有图像另存为文件并插入 Markdown 内容中。
    支持标题、列表项、图像和普通段落的转换。
    """
    # 获取 docx 文件的基本名称，用于创建图像文件夹
    docx_basename = os.path.splitext(os.path.basename(docx_filename))[0]
    images_dir = f'images/{docx_basename}/'
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)  # 如果目录不存在，则创建

    document = Document(docx_filename)  # 打开 docx 文件
    markdown_content = ''
    image_counter = 1  # 图像编号计数器

    for para in document.paragraphs:
        style = para.style.name  # 获取段落样式名称
        text = para.text.strip()  # 获取段落文本并去除首尾空格

        # 如果段落为空且没有任何运行对象，则跳过
        if not text and not para.runs:
            continue

        # 检查段落类型：标题、列表项、普通段落
        is_heading = 'Heading' in style
        is_title = style == 'Title'
        is_list = is_paragraph_list_item(para)
        list_level = get_paragraph_list_level(para) if is_list else 0

        # 确定标题级别
        if is_title:
            heading_level = 1
        elif is_heading:
            heading_level = int(style.replace('Heading ', '')) + 1
        else:
            heading_level = None

        # 检查段落中的每个运行，寻找并保存图像
        for run in para.runs:
            # 查找 w:drawing 标签中的图像
            drawings = run.element.findall('.//w:drawing', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
            for drawing in drawings:
                # 查找图像的关系 ID
                blips = drawing.findall('.//a:blip', namespaces={'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'})
                for blip in blips:
                    rId = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    image_part = document.part.related_parts[rId]
                    image_bytes = image_part.blob  # 获取图像数据
                    image_filename = f'{image_counter}.png'
                    image_path = os.path.join(images_dir, image_filename)
                    
                    # 使用 PIL 保存图像为 PNG 格式
                    image = Image.open(BytesIO(image_bytes))
                    if image.mode in ('RGBA', 'P', 'LA'):
                        image = image.convert('RGB')  # 将图像转换为 RGB 模式，以兼容 PNG 格式
                    image.save(image_path, 'PNG')

                    # 在 Markdown 中添加图像链接
                    markdown_content += f'![图片{image_counter}]({image_path})\n\n'
                    image_counter += 1

        # 根据段落类型格式化文本内容
        if heading_level:
            markdown_content += f'{"#" * heading_level} {text}\n\n'  # 使用 Markdown 语法表示标题
        elif is_list:
            markdown_content += f'{"  " * list_level}- {text}\n'  # 使用缩进和 “-” 表示列表项
        elif text:
            markdown_content += f'{text}\n\n'  # 普通段落直接添加文本

     # 记录调试信息
    LOG.debug(f"从 docx 文件解析的 markdown 内容:\n{markdown_content}")

    return markdown_content

if __name__ == "__main__":
    # 指定输入的 docx 文件路径
    docx_filename = 'inputs/docx/multimodal_llm_overview.docx'
    docx_basename = os.path.splitext(os.path.basename(docx_filename))[0]

    # 生成 Markdown 内容
    markdown_content = generate_markdown_from_docx(docx_filename)

    # 保存 Markdown 内容到文件
    with open(f'{docx_basename}.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)
