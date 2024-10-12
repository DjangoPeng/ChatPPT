from pptx import Presentation

from logger import LOG

def remove_all_slides(prs: Presentation):
    xml_slides = prs.slides._sldIdLst
    slides = list(xml_slides)
    for slide in slides:
        xml_slides.remove(slide)
    LOG.debug("模板中的幻灯片已被移除。")
