from pptx import Presentation

# 加载 PowerPoint 模板
def load_template(template_path: str) -> Presentation:
    prs = Presentation(template_path)
    return prs

# 获取布局映射，返回模板中的布局名称与其索引的字典
def get_layout_mapping(prs: Presentation) -> dict:
    layout_mapping = {}
    for idx, layout in enumerate(prs.slide_layouts):
        layout_mapping[layout.name] = idx
    return layout_mapping

# 打印模板中的所有布局名称及其索引
def print_layouts(prs: Presentation):
    for idx, layout in enumerate(prs.slide_layouts):
        print(f"Layout {idx}: {layout.name}")
