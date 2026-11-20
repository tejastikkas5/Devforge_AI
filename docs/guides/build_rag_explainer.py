from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem, KeepTogether

OUT = "docs/guides/DevForge_AI_RAG_Explained.pdf"
ACC = colors.HexColor("#2F4EA2")

ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["BodyText"], fontName="Helvetica", fontSize=10.5, leading=15, spaceAfter=5)
h1 = ParagraphStyle("h1", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=22, textColor=ACC, alignment=0, spaceAfter=2)
sub = ParagraphStyle("sub", parent=body, textColor=colors.grey, spaceAfter=12)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=14, textColor=ACC, spaceBefore=12, spaceAfter=5)
h3 = ParagraphStyle("h3", parent=ss["Heading3"], fontName="Helvetica-Bold", fontSize=11.5, spaceBefore=8, spaceAfter=3)
quote = ParagraphStyle("q", parent=body, leftIndent=10, borderColor=ACC, borderWidth=0, backColor=colors.HexColor("#EEF2FB"),
                       borderPadding=7, spaceBefore=4, spaceAfter=10)
cell = ParagraphStyle("c", parent=body, fontSize=9.5, leading=13, spaceAfter=0)
cellb = ParagraphStyle("cb", parent=cell, fontName="Helvetica-Bold")


def P(t, s=body): return Paragraph(t, s)
def bullets(items):
    return ListFlowable([ListItem(P(i), leftIndent=12) for i in items], bulletType="bullet", start="•", leftIndent=14)


def table(rows, widths):
    data = [[P(r[0], cellb if i == 0 else cellb), P(r[1], cellb if i == 0 else cell)] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDE5F7")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8C2DC")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FD")]),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return t


s = []
s += [P("How RAG Works in DevForge AI", h1),
      P("Viva / final review explanation, in simple terms", sub)]

s += [P("1. What is RAG?", h2),
      P("RAG stands for <b>Retrieval-Augmented Generation</b>. A language model only knows what it was trained on. "
        "It has never seen <i>our user's project</i>, so if we only ask it to \"fix the login button\" it would guess."),
      P("So <b>before</b> the AI answers, we <b>search the user's project for the relevant code</b>. Then we give that code "
        "to the AI together with the question. The AI now answers from the real files. "
        "That is RAG: <b>Retrieve first, then Generate.</b>"),
      P("<b>Analogy:</b> it is an open-book exam. The AI does not memorise the project. It looks up the right pages first, then answers.", quote)]

s += [P("2. The flow at a glance", h2)]
flow = Table([[P(t, cellb) for t in ["1. Scan project", "2. Chunk code", "3. Hybrid search", "4. Build context", "5. LLM answers"]]],
             colWidths=[33*mm]*5)
flow.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#DDE5F7")),
                          ("BOX", (0, 0), (-1, -1), 0.5, ACC), ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white),
                          ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
s += [flow, Spacer(1, 6)]

s += [P("3. Step by step", h2),
      P("Step 1: Reading the project (indexing)", h3),
      bullets(["DevForge scans the project folder. It skips junk like <font face='Courier'>.venv</font>, "
               "<font face='Courier'>node_modules</font> and <font face='Courier'>__pycache__</font>, and reads only code and text files.",
               "It re-reads only files that have <b>changed</b> (it checks modified time and size), so it stays fast."]),
      P("Step 2: Smart chunking (cutting code into pieces)", h3),
      bullets(["We do not feed whole files to the AI. That is too big and noisy.",
               "<b>Python files:</b> we use Python's <font face='Courier'>ast</font> module to cut along natural boundaries, "
               "one chunk per function, class or method. Each chunk keeps its file name and line numbers.",
               "<b>Other files</b> (HTML, JS, CSS): sliding windows of 40 lines with overlap.",
               "<i>Why it matters:</i> a complete function helps the AI far more than a random cut in the middle of one."]),
      P("Step 3: Searching (hybrid search)", h3),
      P("When the user asks something, we find the best chunks with <b>two methods together</b>:")]

s += [table([
    ["Method", "How it works"],
    ["<b>BM25</b> (keyword search)",
     "The classic search-engine method. It scores chunks by how many of the user's words they contain. Rare words count for more than common ones, "
     "and function and file names get extra weight. Fast, needs no AI model."],
    ["<b>Embeddings</b> (meaning search, optional)",
     "An embedding model turns each chunk and the question into numbers that represent <i>meaning</i>. We compare them with cosine similarity. "
     "This finds code that matches in meaning even when the words differ, e.g. \"sign in\" finds <font face='Courier'>login()</font>. "
     "Vectors are cached in <font face='Courier'>.devforge/embeddings.json</font>, so each chunk is embedded only once."],
], [48*mm, 117*mm]), Spacer(1, 6),
    P("The two rankings are merged with <b>Reciprocal Rank Fusion</b>. A chunk that ranks high in <i>both</i> lists wins. We keep the top 6.")]

s += [P("Step 4: Building the context", h3),
      bullets(["A <b>repo map</b>: a short list of every file and its functions.",
               "The <b>top relevant code chunks</b>, with file name and line numbers.",
               "All trimmed to a size limit (about 6000 characters) so it fits in the model's window."]),
      P("Step 5: Generating the answer", h3),
      P("The context and the user's question go to the local LLM through Ollama. The AI answers from the user's real code. "
        "For build requests, the same context helps it edit existing files instead of inventing new ones."),
      P("Step 6: Staying up to date", h3),
      P("After code is generated, the index is refreshed, so follow-up prompts see the new files.")]

s += [P("4. Likely viva questions and answers", h2),
      table([
          ["Question", "Answer"],
          ["Why not send the whole project to the AI?", "Local models have small context windows. Sending everything would be slow, would overflow the window, and would confuse the model."],
          ["Why hybrid, not only embeddings?", "Keyword search is excellent for exact names like <font face='Courier'>calculateTotal</font>. Embeddings are good at meaning. Together they cover each other's weak spots."],
          ["What if no embedding model is installed?", "It <b>falls back to BM25 only</b> automatically. The project still works."],
          ["Why no vector database?", "The index is small and lives in memory, with a simple JSON cache. It stays lightweight, offline and free of extra dependencies."],
          ["Does it need the internet?", "No. Everything runs locally with Ollama, so the user's code never leaves their machine."],
          ["How does it reduce hallucination?", "The AI is told to answer from the retrieved project code. We also pass in the real file listing, and off-topic requests are rejected."],
          ["What does \"AST-aware\" mean?", "We parse the code's structure (functions and classes) instead of cutting by line count."],
      ], [55*mm, 110*mm])]

s += [P("5. 30-second closing summary", h2),
      P("DevForge <b>scans the project, splits code into function-level pieces, searches them with keyword and meaning-based search combined, "
        "and gives the best matches to the AI</b>. That makes answers specific to the user's project and not generic. "
        "It runs fully offline, and it still works if the embedding model is missing.", quote),
      P("<b>Note for prep:</b> the embedding part is <i>optional</i>. It activates only if an embedding model (a model with \"embed\" in its name) "
        "is installed in Ollama. Keyword search alone is the fallback. Say this clearly if asked.")]

s += [Spacer(1, 6), P("Source: <font face='Courier'>devforge/rag.py</font> (indexing and search) and "
                       "<font face='Courier'>devforge/engine.py</font> (where the context is used).", sub)]

SimpleDocTemplate(OUT, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=18*mm, bottomMargin=18*mm,
                  title="How RAG Works in DevForge AI").build(s)
print("ok", OUT)
