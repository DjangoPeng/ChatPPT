from pptx import Presentation
from logger import LOG

# 删除 PowerPoint 模板中的所有幻灯片
def remove_all_slides(prs: Presentation):
    xml_slides = prs.slides._sldIdLst  # 获取幻灯片列表
    slides = list(xml_slides)  # 转换为列表
    for slide in slides:
        xml_slides.remove(slide)  # 从幻灯片列表中移除每一张幻灯片
    LOG.debug("模板中的幻灯片已被移除。")
