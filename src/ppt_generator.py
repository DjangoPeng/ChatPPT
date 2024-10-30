import os
from pptx import Presentation
from utils import remove_all_slides

def generate_presentation(powerpoint_data, template_path: str, output_path: str):
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file '{template_path}' does not exist.")
    
    print(f"使用模板 '{template_path}' 创建演示文稿...")
    prs = Presentation(template_path)
    remove_all_slides(prs)
    prs.core_properties.title = powerpoint_data.title
    print(f"设置演示文稿标题: {powerpoint_data.title}")

    for i, slide in enumerate(powerpoint_data.slides, start=1):
        # 检查并选择布局
        if slide.layout >= len(prs.slide_layouts):
            slide_layout = prs.slide_layouts[0]
            print(f"幻灯片 {i}：布局超出范围，使用默认布局 0")
        else:
            slide_layout = prs.slide_layouts[slide.layout]
            print(f"幻灯片 {i}：使用布局 {slide.layout}")

        # 创建新幻灯片
        new_slide = prs.slides.add_slide(slide_layout)
        print(f"创建幻灯片 {i}，标题: {slide.content.title}")

        # 设置幻灯片标题
        if new_slide.shapes.title:
            new_slide.shapes.title.text = slide.content.title
            print(f"幻灯片 {i} 标题设置为: {slide.content.title}")

        # 添加项目符号
        bullet_points_added = False
        for shape in new_slide.shapes:
            if shape.has_text_frame and shape != new_slide.shapes.title:
                text_frame = shape.text_frame
                text_frame.clear()
                print(f"幻灯片 {i} 清空文本框，开始添加项目符号...")
                for point in slide.content.bullet_points:
                    p = text_frame.add_paragraph()
                    p.text = point
                    p.level = 0
                    print(f"  添加项目符号: {point}")
                bullet_points_added = True
                break
        if not bullet_points_added:
            print(f"幻灯片 {i} 没有找到可添加项目符号的文本框")

        # 插入图片
        if slide.content.image_path:
            image_full_path = os.path.join(os.getcwd(), slide.content.image_path)
            if os.path.exists(image_full_path):
                image_added = False
                for shape in new_slide.placeholders:
                    if shape.placeholder_format.type == 18:  # 18 表示图片占位符
                        shape.insert_picture(image_full_path)
                        print(f"幻灯片 {i} 插入图片: {image_full_path}")
                        image_added = True
                        break
                if not image_added:
                    print(f"幻灯片 {i} 没有找到图片占位符，无法插入图片")
            else:
                print(f"图片路径 '{image_full_path}' 不存在，跳过插入")

    prs.save(output_path)
    print(f"演示文稿已保存至 '{output_path}'")
