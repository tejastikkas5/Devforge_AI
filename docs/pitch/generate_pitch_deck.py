import sys
import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # Set 16:9 widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6] # Blank layout

    # Theme Colors
    COLOR_BG_DARK = RGBColor(15, 23, 42)       # #0F172A Navy
    COLOR_BG_LIGHT = RGBColor(248, 250, 252)   # #F8FAFC Soft Light Grey
    COLOR_PRIMARY = RGBColor(30, 41, 59)       # #1E293B Slate Dark Text
    COLOR_ACCENT = RGBColor(37, 99, 235)       # #2563EB Electric Blue
    COLOR_ACCENT_ALT = RGBColor(16, 185, 129)  # #10B981 Emerald Green
    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_CARD_BG = RGBColor(255, 255, 255)
    COLOR_BORDER = RGBColor(226, 232, 240)    # #E2E8F0
    COLOR_TEXT_MUTED = RGBColor(100, 116, 139) # #64748B

    def add_header(slide, title_text, category_text="DEVFORGE AI | STARTUP PITCH"):
        # Header category
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_ACCENT
        p_cat.font.name = "Calibri"

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.7))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_PRIMARY
        p_title.font.name = "Calibri"

    def add_card(slide, left, top, width, height, bg_color=COLOR_CARD_BG, border_color=COLOR_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(1.5)
        else:
            shape.line.fill.background()
        return shape

    # ==========================================
    # SLIDE 1: Title Slide (Dark Theme)
    # ==========================================
    slide1 = prs.slides.add_slide(blank_slide_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_BG_DARK
    bg1.line.fill.background()

    # Title Card Accent Line
    accent_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(2.2), Inches(0.15), Inches(3.2))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = COLOR_ACCENT
    accent_bar.line.fill.background()

    # Title Text
    t_box = slide1.shapes.add_textbox(Inches(1.4), Inches(2.0), Inches(10.5), Inches(3.5))
    tf = t_box.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "DEVFORGE AI"
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.font.name = "Calibri"

    p2 = tf.add_paragraph()
    p2.text = "Autonomous, Enterprise-Grade Multi-Agent Software Development Engine"
    p2.font.size = Pt(22)
    p2.font.color.rgb = RGBColor(148, 163, 184) # Light Slate
    p2.font.name = "Calibri"
    p2.space_before = Pt(10)

    p3 = tf.add_paragraph()
    p3.text = "🚀 Pitch & Prototype Grant Deck | Seed Funding Ask: ₹20,000"
    p3.font.size = Pt(16)
    p3.font.bold = True
    p3.font.color.rgb = COLOR_ACCENT_ALT
    p3.font.name = "Calibri"
    p3.space_before = Pt(24)

    p4 = tf.add_paragraph()
    p4.text = "Presented by: Tejas Tikkas | Rohan Umbarkar | Hrutik Sawant | Vivek Ingole"
    p4.font.size = Pt(13)
    p4.font.color.rgb = COLOR_TEXT_MUTED
    p4.font.name = "Calibri"
    p4.space_before = Pt(15)

    # ==========================================
    # SLIDE 2: The Problem
    # ==========================================
    slide2 = prs.slides.add_slide(blank_slide_layout)
    bg2 = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg2.fill.solid()
    bg2.fill.fore_color.rgb = COLOR_BG_LIGHT
    bg2.line.fill.background()
    add_header(slide2, "The Problem: Cloud AI Coding Tools Are Expensive & Insecure")

    problems = [
        ("💸 High API & License Costs", "Tools like Devin & Copilot rely on expensive cloud LLM APIs. Subscriptions and token costs scale rapidly, making them unaffordable for small teams & budget-conscious startups."),
        ("🔒 Data Privacy & Source Code Security Risks", "Enterprises & software houses CANNOT risk uploading proprietary codebase files to third-party cloud LLM servers due to IP leakage concerns."),
        ("⚠️ One-Size-Fits-All Inefficiency", "Single LLMs are overkill for simple code edits yet context-blind on large codebases, leading to high hallucinations and wasted compute cycles.")
    ]

    for i, (title, desc) in enumerate(problems):
        top_pos = Inches(1.6 + i * 1.8)
        add_card(slide2, Inches(0.8), top_pos, Inches(11.7), Inches(1.55))
        
        box = slide2.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.15), Inches(11.3), Inches(1.25))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = COLOR_PRIMARY
        
        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(13)
        p_desc.font.color.rgb = COLOR_TEXT_MUTED
        p_desc.space_before = Pt(6)

    # ==========================================
    # SLIDE 3: The Solution (DevForge AI)
    # ==========================================
    slide3 = prs.slides.add_slide(blank_slide_layout)
    bg3 = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg3.fill.solid()
    bg3.fill.fore_color.rgb = COLOR_BG_LIGHT
    bg3.line.fill.background()
    add_header(slide3, "The Solution: DevForge AI — Private, Multi-Agent Local AI Engine")

    features = [
        ("🤖 Hierarchical Multi-Agent Engine", "Specialized AI agents (Supervisor, Planner, Researcher, Coder, Tester, Reviewer, Debugger) collaborate seamlessly to build software end-to-end."),
        ("🛡️ 100% Private & Air-Gapped (Ollama)", "Runs entirely on-premise or local GPU infrastructure via Ollama. Zero code data leaves your system."),
        ("⚡ AST + Vector Hybrid RAG", "Combines Abstract Syntax Tree structure analysis with vector search to give agents instant, deep context of multi-file repositories."),
        ("💡 90% Cost Reduction", "Replaces expensive cloud APIs with optimized local open-weight LLMs (Qwen, DeepSeek, Codestral), drastically lowering costs.")
    ]

    for i, (title, desc) in enumerate(features):
        row = i // 2
        col = i % 2
        left_pos = Inches(0.8 + col * 5.95)
        top_pos = Inches(1.6 + row * 2.7)

        add_card(slide3, left_pos, top_pos, Inches(5.75), Inches(2.4))

        box = slide3.shapes.add_textbox(left_pos + Inches(0.2), top_pos + Inches(0.2), Inches(5.35), Inches(2.0))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = COLOR_ACCENT

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(13)
        p_desc.font.color.rgb = COLOR_PRIMARY
        p_desc.space_before = Pt(8)

    # ==========================================
    # SLIDE 4: Novelty & Competitive Differentiation
    # ==========================================
    slide4 = prs.slides.add_slide(blank_slide_layout)
    bg4 = slide4.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg4.fill.solid()
    bg4.fill.fore_color.rgb = COLOR_BG_LIGHT
    bg4.line.fill.background()
    add_header(slide4, "Why Invest? Unmatched Competitive Differentiation & Novelty")

    # Add Comparison Table
    table_shape = slide4.shapes.add_table(5, 5, Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    table = table_shape.table

    # Column widths
    table.columns[0].width = Inches(2.7)
    table.columns[1].width = Inches(2.25)
    table.columns[2].width = Inches(2.25)
    table.columns[3].width = Inches(2.25)
    table.columns[4].width = Inches(2.25)

    headers = ["Key Capability / Metric", "GitHub Copilot", "Cursor AI", "Devin / OpenHands", "DevForge AI (Us)"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_BG_DARK if j < 4 else COLOR_ACCENT
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER

    data = [
        ["Data Privacy / On-Premise", "❌ Cloud Only", "❌ Cloud Only", "⚠️ Cloud / Complex", "✅ 100% Local / On-Prem"],
        ["Multi-Agent Specialization", "❌ Single Assistant", "❌ Autocomplete/Chat", "✅ High (Cloud LLMs)", "✅ High (Local LLMs)"],
        ["Dynamic Model Routing", "❌ Fixed Model", "❌ Fixed Model", "❌ Single LLM", "✅ Heterogeneous LLM Router"],
        ["API Cost per Task", "High Cloud Bill", "Moderate Cloud Bill", "Very High Cloud Bill", "📉 ₹0 (Local Compute)"]
    ]

    for i, row in enumerate(data):
        for j, val in enumerate(row):
            cell = table.cell(i+1, j)
            cell.text = val
            cell.fill.solid()
            if j == 4:
                cell.fill.fore_color.rgb = RGBColor(236, 253, 245)
            else:
                cell.fill.fore_color.rgb = COLOR_WHITE
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(12)
            if j == 4:
                p.font.bold = True
                p.font.color.rgb = COLOR_ACCENT_ALT
            else:
                p.font.color.rgb = COLOR_PRIMARY
            p.alignment = PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT

    # ==========================================
    # SLIDE 5: Architecture & Secret Sauce
    # ==========================================
    slide5 = prs.slides.add_slide(blank_slide_layout)
    bg5 = slide5.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg5.fill.solid()
    bg5.fill.fore_color.rgb = COLOR_BG_LIGHT
    bg5.line.fill.background()
    add_header(slide5, "The Secret Sauce: Dynamic Heterogeneous LLM Orchestrator")

    sauce = [
        ("🎯 Specialized Local Model Mapping", "Assigns optimal model sizes based on task difficulty:\n• Qwen3-Coder / DeepSeek-Coder-V2 for core architecture & code generation.\n• CodeGemma / Codestral for rapid unit testing & documentation.\n• Devstral for codebase-wide refactoring & debugging."),
        ("🔄 Smart Context Windowing & RAG", "Reduces prompt overhead by feeding agents pruned AST syntax graphs and indexed embeddings, eliminating token bottlenecks on local hardware."),
        ("⚙️ Automated Self-Correction Loop", "Testing and Debugging agents execute code in local sandboxes, catching runtime bugs and auto-fixing syntax errors before human review.")
    ]

    for i, (title, desc) in enumerate(sauce):
        top_pos = Inches(1.6 + i * 1.8)
        add_card(slide5, Inches(0.8), top_pos, Inches(11.7), Inches(1.55))

        box = slide5.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.15), Inches(11.3), Inches(1.25))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = COLOR_ACCENT

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(12)
        p_desc.font.color.rgb = COLOR_PRIMARY
        p_desc.space_before = Pt(4)

    # ==========================================
    # SLIDE 6: Business Model & Revenue Potential
    # ==========================================
    slide6 = prs.slides.add_slide(blank_slide_layout)
    bg6 = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg6.fill.solid()
    bg6.fill.fore_color.rgb = COLOR_BG_LIGHT
    bg6.line.fill.background()
    add_header(slide6, "Business Model & Revenue Potential")

    models = [
        ("🏢 Enterprise On-Prem License", "₹1,500 / dev / month", "Self-hosted deployment on corporate servers or private cloud. Includes dedicated RAG connector & local agent updates."),
        ("💻 Agency & Startup Package", "₹5,000 / team / month", "Plug-and-play local containerized solution for software agencies wanting zero cloud API costs."),
        ("🛠️ Custom RAG & Setup Services", "₹15,000 - ₹30,000 / client", "One-time setup, codebase indexing, and custom agent workflow tuning for corporate IT departments.")
    ]

    for i, (title, price, desc) in enumerate(models):
        left_pos = Inches(0.8 + i * 3.95)
        add_card(slide6, left_pos, Inches(1.6), Inches(3.8), Inches(5.2))

        box = slide6.shapes.add_textbox(left_pos + Inches(0.2), Inches(1.8), Inches(3.4), Inches(4.8))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = COLOR_PRIMARY

        p_price = tf.add_paragraph()
        p_price.text = price
        p_price.font.size = Pt(18)
        p_price.font.bold = True
        p_price.font.color.rgb = COLOR_ACCENT_ALT
        p_price.space_before = Pt(8)

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(13)
        p_desc.font.color.rgb = COLOR_TEXT_MUTED
        p_desc.space_before = Pt(12)

    # ==========================================
    # SLIDE 7: Funding Ask & Budget Allocation (₹20,000 INR)
    # ==========================================
    slide7 = prs.slides.add_slide(blank_slide_layout)
    bg7 = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg7.fill.solid()
    bg7.fill.fore_color.rgb = COLOR_BG_LIGHT
    bg7.line.fill.background()
    add_header(slide7, "Funding Ask & Detailed Budget Breakdown (₹20,000 Max)")

    # Left Box: Investment Summary
    add_card(slide7, Inches(0.8), Inches(1.6), Inches(4.5), Inches(5.2), bg_color=COLOR_BG_DARK)
    b_ask = slide7.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(4.1), Inches(4.8))
    tf_ask = b_ask.text_frame
    tf_ask.word_wrap = True

    p = tf_ask.paragraphs[0]
    p.text = "PROTOTYPE GRANT FUNDING ASK"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_ALT

    p_amt = tf_ask.add_paragraph()
    p_amt.text = "₹20,000"
    p_amt.font.size = Pt(38)
    p_amt.font.bold = True
    p_amt.font.color.rgb = COLOR_WHITE
    p_amt.space_before = Pt(4)

    p_sub = tf_ask.add_paragraph()
    p_sub.text = "Target Milestone: Build & Benchmarking of Production MVP Engine"
    p_sub.font.size = Pt(13)
    p_sub.font.color.rgb = RGBColor(148, 163, 184)
    p_sub.space_before = Pt(10)

    p_mil = tf_ask.add_paragraph()
    p_mil.text = "Deliverables with ₹20K:\n• Functional AST + Vector RAG MVP\n• Ollama Multi-Agent Local Router\n• Empirical Benchmark Report\n• Live Working Demo Platform"
    p_mil.font.size = Pt(13)
    p_mil.font.color.rgb = COLOR_WHITE
    p_mil.space_before = Pt(18)

    # Right Side: Budget Breakdown Cards (INR)
    budget_items = [
        ("⚡ Cloud GPU Credits (RunPod / Vast.ai)", "₹8,000 (40%)", "Renting GPU cloud compute to run benchmark tests, evaluate 16B/32B local LLMs, and stress-test multi-agent workflows."),
        ("🌐 Web Hosting, Vector DB & Domain Infra", "₹4,000 (20%)", "Domain registration, cloud server hosting for web UI demo, and vector database testing tier."),
        ("📊 Dataset Curation & Benchmark Repository", "₹5,000 (25%)", "Indexing test repos, software engineering task datasets, and code evaluation suite tools."),
        ("📑 Presentation Material, Demo & Travel", "₹3,000 (15%)", "Event participation, pitch presentation materials, demo hardware accessories, and contingency buffer.")
    ]

    for i, (title, cost, desc) in enumerate(budget_items):
        top_pos = Inches(1.6 + i * 1.3)
        add_card(slide7, Inches(5.5), top_pos, Inches(7.0), Inches(1.15))

        box = slide7.shapes.add_textbox(Inches(5.65), top_pos + Inches(0.1), Inches(6.7), Inches(0.95))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = f"{title}  —  {cost}"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLOR_ACCENT

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = COLOR_PRIMARY
        p_desc.space_before = Pt(3)

    # ==========================================
    # SLIDE 8: Execution Roadmap
    # ==========================================
    slide8 = prs.slides.add_slide(blank_slide_layout)
    bg8 = slide8.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg8.fill.solid()
    bg8.fill.fore_color.rgb = COLOR_BG_LIGHT
    bg8.line.fill.background()
    add_header(slide8, "Project Milestones & Execution Roadmap")

    phases = [
        ("Phase 1 (Completed)", "Architecture & Research", "• Finalized Multi-Agent system design.\n• Integrated Ollama local runtime.\n• Candidate local models selected."),
        ("Phase 2 (Immediate)", "MVP & Hybrid RAG Engine", "• Build AST + Vector Code RAG.\n• Implement local LLM router.\n• Deploy web demo platform."),
        ("Phase 3 (Next 2 Mos)", "Empirical Benchmarking", "• Run evaluation across LLMs.\n• Measure latency, VRAM & pass rate.\n• Publish research benchmark paper."),
        ("Phase 4 (Future)", "Pilot Launch & Expansion", "• Offer containerized deployment.\n• Pilot with 3 developer teams.\n• Explore commercialization.")
    ]

    for i, (quarter, title, details) in enumerate(phases):
        left_pos = Inches(0.8 + i * 2.95)
        add_card(slide8, left_pos, Inches(1.6), Inches(2.8), Inches(5.2))

        box = slide8.shapes.add_textbox(left_pos + Inches(0.15), Inches(1.8), Inches(2.5), Inches(4.8))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = quarter
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLOR_ACCENT

        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.size = Pt(15)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_PRIMARY
        p_t.space_before = Pt(6)

        p_d = tf.add_paragraph()
        p_d.text = details
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = COLOR_TEXT_MUTED
        p_d.space_before = Pt(12)

    # ==========================================
    # SLIDE 9: Pitch Closing / Call to Action
    # ==========================================
    slide9 = prs.slides.add_slide(blank_slide_layout)
    bg9 = slide9.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg9.fill.solid()
    bg9.fill.fore_color.rgb = COLOR_BG_DARK
    bg9.line.fill.background()

    b_close = slide9.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.333), Inches(4.5))
    tf_close = b_close.text_frame
    tf_close.word_wrap = True

    p = tf_close.paragraphs[0]
    p.text = "REVOLUTIONIZING PRIVATE AI SOFTWARE DEVELOPMENT"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_ALT
    p.alignment = PP_ALIGN.CENTER

    p2 = tf_close.add_paragraph()
    p2.text = "DevForge AI delivers private, high-performance, cost-effective multi-agent AI for software development teams."
    p2.font.size = Pt(18)
    p2.font.color.rgb = COLOR_WHITE
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(20)

    p3 = tf_close.add_paragraph()
    p3.text = "🤝 We are requesting ₹20,000 in Funding to complete our RAG engine MVP and benchmarking compute."
    p3.font.size = Pt(16)
    p3.font.bold = True
    p3.font.color.rgb = RGBColor(148, 163, 184)
    p3.alignment = PP_ALIGN.CENTER
    p3.space_before = Pt(24)

    p4 = tf_close.add_paragraph()
    p4.text = "Presented by: Tejas Tikkas | Rohan Umbarkar | Hrutik Sawant | Vivek Ingole\nDevForge AI — Private Multi-Agent Platform"
    p4.font.size = Pt(14)
    p4.font.color.rgb = COLOR_ACCENT
    p4.alignment = PP_ALIGN.CENTER
    p4.space_before = Pt(30)

    # Save presentation
    output_path = r"e:\Capstone_MITCORER\docs\pitch\DevForge_AI_Startup_Pitch_v2.pptx"
    prs.save(output_path)
    print(f"Updated presentation saved successfully to {output_path}")

if __name__ == "__main__":
    create_deck()
