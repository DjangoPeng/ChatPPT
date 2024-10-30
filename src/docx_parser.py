import os
from docx import Document
from docx.oxml.ns import qn
from PIL import Image
from io import BytesIO

def is_paragraph_list_item(paragraph):
    """
    检查段落是否为列表项。
    判断依据是段落的样式名称是否包含 'list bullet' 或 'list number'，分别对应项目符号列表和编号列表。
    """
    style_name = paragraph.style.name.lower() if paragraph.style else ""
    return 'list bullet' in style_name or 'list number' in style_name

def get_paragraph_list_level(paragraph):
    """
    获取段落的列表级别（缩进层级）。
    首先尝试通过 XML 结构判断，如果无法获取，则通过样式名称中的数字判断。
    """
    p = paragraph._p
    # 检查 XML 中是否存在 'numPr' 标签
    numPr = p.find(qn('w:numPr'))
    if numPr is not None:
        ilvl = numPr.find(qn('w:ilvl'))
        if ilvl is not None:
            val = ilvl.get(qn('w:val'))
            if val is not None:
                return int(val)
    
    # 如果 XML 结构未找到级别，则通过样式名称中的数字推测级别
    style_name = paragraph.style.name.lower() if paragraph.style else ""
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
    docx_basename = os.path.splitext(os.path.basename(docx_filename))[0]
    images_dir = f'images/{docx_basename}/'
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    document = Document(docx_filename)
    markdown_content = ''
    image_counter = 1  # 图像编号计数器

    for para in document.paragraphs:
        # 检查段落样式是否存在
        style = para.style.name if para.style else "Normal"
        text = para.text.strip() if para.text else ""

        if not text and not para.runs:
            continue  # 如果段落为空且没有内容，则跳过

        is_heading = 'Heading' in style
        is_title = style == 'Title'
        is_list = is_paragraph_list_item(para)
        list_level = get_paragraph_list_level(para) if is_list else 0

        # 根据段落类型确定标题级别
        if is_title:
            heading_level = 1
        elif is_heading:
            heading_level = int(style.replace('Heading ', '')) + 1
        else:
            heading_level = None

        # 检查段落中的每个运行，寻找图像
        for run in para.runs:
            drawings = run.element.findall('.//w:drawing', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
            for drawing in drawings:
                blips = drawing.findall('.//a:blip', namespaces={'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'})
                for blip in blips:
                    # 检查 'embed' 属性是否存在
                    rId = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    if rId is not None and rId in document.part.related_parts:
                        image_part = document.part.related_parts[rId]
                        image_bytes = image_part.blob
                        image_filename = f'{image_counter}.png'
                        image_path = os.path.join(images_dir, image_filename)
                        
                        # 使用 PIL 保存图像为 PNG 格式
                        image = Image.open(BytesIO(image_bytes))
                        if image.mode in ('RGBA', 'P', 'LA'):
                            image = image.convert('RGB')
                        image.save(image_path, 'PNG')

                        # 在 Markdown 中添加图像链接
                        markdown_content += f'![图片{image_counter}]({image_path})\n\n'
                        image_counter += 1

        # 根据段落类型格式化文本内容
        if heading_level:
            markdown_content += f'{"#" * heading_level} {text}\n\n'
        elif is_list:
            markdown_content += f'{"  " * list_level}- {text}\n'
        elif text:
            markdown_content += f'{text}\n\n'

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
