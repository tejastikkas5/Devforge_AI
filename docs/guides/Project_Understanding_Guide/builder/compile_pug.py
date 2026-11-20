import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, PageBreak
from .common import PugNumberedCanvas, get_pug_styles, PAGE_W, PAGE_H, MARGIN
from .part1 import build_pug_part1_pages
from .part2 import build_pug_part2_pages
from .part3 import build_pug_part3_pages
from .part4 import build_pug_part4_pages
from .part5 import build_pug_part5_pages
from .part6 import build_pug_part6_pages
from .part7 import build_pug_part7_pages
from .part8 import build_pug_part8_pages
from .part9 import build_pug_part9_pages

def compile_project_understanding_guide(output_pdf_path):
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN
    )

    styles = get_pug_styles()
    
    # Gather all 26 structured pages
    all_pages = []
    all_pages.extend(build_pug_part1_pages(styles)) # p1-p3
    all_pages.extend(build_pug_part2_pages(styles)) # p4-p6
    all_pages.extend(build_pug_part3_pages(styles)) # p7-p9
    all_pages.extend(build_pug_part4_pages(styles)) # p10-p12
    all_pages.extend(build_pug_part5_pages(styles)) # p13-p15
    all_pages.extend(build_pug_part6_pages(styles)) # p16-p18
    all_pages.extend(build_pug_part7_pages(styles)) # p19-p21
    all_pages.extend(build_pug_part8_pages(styles)) # p22-p24
    all_pages.extend(build_pug_part9_pages(styles)) # p25-p26

    story = []
    total_sections = len(all_pages)
    for idx, page_elements in enumerate(all_pages):
        story.extend(page_elements)
        if idx < total_sections - 1:
            story.append(PageBreak())

    print(f"Building Project Understanding Guide with {len(all_pages)} designated pages...")
    doc.build(story, canvasmaker=PugNumberedCanvas)
    print(f"Successfully generated: {output_pdf_path}")

if __name__ == "__main__":
    out_pdf = r"E:\Capstone_MITCORER\docs\guides\Project_Understanding_Guide\DevForge_AI_Project_Understanding_Guide.pdf"
    compile_project_understanding_guide(out_pdf)
