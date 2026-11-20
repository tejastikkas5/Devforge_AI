"""Ready-made modern UI themes. The Designer agent only *chooses* one; the CSS itself is
hand-written here, so generated sites look polished even with a small local model.

render_css() produces theme.css: CSS variables (per theme) + a shared component library
(navbar, hero, cards, buttons, forms, grid, footer...) that also styles bare HTML elements.
"""
import re
from typing import Dict, Optional

FONT = "'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Roboto, Arial, sans-serif"

THEMES: Dict[str, Dict] = {
    "modern-dark": {
        "about": "dark tech look with indigo glow (SaaS, dashboards, developer tools, games, AI, startups)",
        "keywords": "dashboard saas tech startup developer game gaming crypto ai admin software app code cyber",
        "vars": {
            "bg": "#0b0f19", "bg-alt": "#0f1524", "surface": "#141b2d", "text": "#e9eef8", "muted": "#9aa7bf",
            "primary": "#6366f1", "primary-contrast": "#ffffff", "border": "rgba(255,255,255,.08)",
            "border-strong": "rgba(255,255,255,.18)", "radius": "16px", "radius-sm": "10px",
            "shadow": "0 10px 30px -12px rgba(0,0,0,.6)", "shadow-lg": "0 24px 50px -16px rgba(99,102,241,.35)",
            "font": FONT, "heading-font": FONT,
            "hero-bg": "radial-gradient(1100px 480px at 80% -10%, rgba(99,102,241,.38), transparent), linear-gradient(180deg,#0b0f19,#0d1424)",
            "hero-text": "#ffffff", "hero-muted": "#b6c1d8", "nav-bg": "rgba(11,15,25,.75)",
            "img-bg": "linear-gradient(135deg,#1e2a4a,#2b2f6b)", "badge-bg": "rgba(99,102,241,.18)",
            "badge-text": "#a5b4fc", "footer-bg": "#080b13", "footer-text": "#8794ad",
        },
        "extra": "",
    },
    "clean-light": {
        "about": "bright, minimal and professional with blue accents (business, school, clinic, company, news)",
        "keywords": "school university college hospital clinic business company corporate news education bank agency service consulting",
        "vars": {
            "bg": "#ffffff", "bg-alt": "#f5f7fb", "surface": "#ffffff", "text": "#0f172a", "muted": "#5b6678",
            "primary": "#2563eb", "primary-contrast": "#ffffff", "border": "#e5e9f0", "border-strong": "#cfd6e2",
            "radius": "14px", "radius-sm": "10px", "shadow": "0 8px 24px -14px rgba(15,23,42,.25)",
            "shadow-lg": "0 22px 44px -18px rgba(37,99,235,.35)", "font": FONT, "heading-font": FONT,
            "hero-bg": "linear-gradient(135deg,#eff4ff 0%,#dbe8ff 100%)", "hero-text": "#0f172a",
            "hero-muted": "#475569", "nav-bg": "rgba(255,255,255,.85)",
            "img-bg": "linear-gradient(135deg,#e0ebff,#c7d9ff)", "badge-bg": "#e0ebff", "badge-text": "#1d4ed8",
            "footer-bg": "#0f172a", "footer-text": "#9aa7bf",
        },
        "extra": "",
    },
    "vibrant": {
        "about": "bold, warm and energetic with a coral-to-purple gradient (shoes, fashion, shops, food, toys, sports, fitness)",
        "keywords": "shoe shoes sneaker sneakers fashion clothing apparel store shop toy toys kids food pizza burger sport sports fitness gym bakery cake",
        "vars": {
            "bg": "#fffaf5", "bg-alt": "#fff1e6", "surface": "#ffffff", "text": "#1c1917", "muted": "#6b6460",
            "primary": "#f43f5e", "primary-contrast": "#ffffff", "border": "#f3e3d6", "border-strong": "#e8cdb9",
            "radius": "22px", "radius-sm": "14px", "shadow": "0 10px 28px -14px rgba(244,63,94,.35)",
            "shadow-lg": "0 26px 50px -18px rgba(244,63,94,.5)", "font": FONT,
            "heading-font": "'Trebuchet MS', 'Segoe UI', sans-serif",
            "hero-bg": "linear-gradient(135deg,#ff7a45 0%,#f43f5e 55%,#a855f7 100%)", "hero-text": "#ffffff",
            "hero-muted": "rgba(255,255,255,.9)", "nav-bg": "rgba(255,250,245,.88)",
            "img-bg": "linear-gradient(135deg,#ffe4d1,#ffd1dc)", "badge-bg": "#ffe0e6", "badge-text": "#be123c",
            "footer-bg": "#1c1917", "footer-text": "#d6cfc9",
        },
        "extra": "",
    },
    "glass": {
        "about": "frosted-glass cards over a purple-pink gradient (music, travel, weather, gallery, photography, landing pages)",
        "keywords": "music weather travel gallery photography photo landing event podcast movie film",
        "vars": {
            "bg": "#0b1020", "bg-alt": "rgba(255,255,255,.03)", "surface": "rgba(255,255,255,.07)", "text": "#f5f7ff",
            "muted": "#c3c9e4", "primary": "#8b5cf6", "primary-contrast": "#ffffff", "border": "rgba(255,255,255,.14)",
            "border-strong": "rgba(255,255,255,.28)", "radius": "20px", "radius-sm": "12px",
            "shadow": "0 12px 36px -16px rgba(0,0,0,.6)", "shadow-lg": "0 28px 56px -20px rgba(139,92,246,.55)",
            "font": FONT, "heading-font": FONT, "hero-bg": "transparent", "hero-text": "#ffffff",
            "hero-muted": "#d5daf0", "nav-bg": "rgba(15,23,42,.45)",
            "img-bg": "linear-gradient(135deg,rgba(139,92,246,.4),rgba(236,72,153,.32))",
            "badge-bg": "rgba(255,255,255,.14)", "badge-text": "#ffffff", "footer-bg": "rgba(0,0,0,.35)",
            "footer-text": "#b6bdd9",
        },
        "extra": (
            "body{background:radial-gradient(900px 600px at 10% -10%,#4f46e5 0%,transparent 60%),"
            "radial-gradient(800px 600px at 100% 10%,#db2777 0%,transparent 55%),#0b1020;background-attachment:fixed}\n"
            ".card,.cta,form,.navbar{backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px)}\n"
        ),
    },
    "elegant": {
        "about": "warm cream and serif headings, refined and calm (restaurant, cafe, hotel, wedding, jewellery, boutique, spa, resume)",
        "keywords": "luxury restaurant cafe coffee hotel wedding jewelry jewellery boutique spa resume cv salon furniture interior",
        "vars": {
            "bg": "#faf7f2", "bg-alt": "#f2ece2", "surface": "#fffdf9", "text": "#231f1b", "muted": "#6d645b",
            "primary": "#8a5a2b", "primary-contrast": "#ffffff", "border": "#e7dccb", "border-strong": "#d4c4ab",
            "radius": "6px", "radius-sm": "4px", "shadow": "0 8px 24px -16px rgba(60,40,20,.4)",
            "shadow-lg": "0 20px 40px -20px rgba(60,40,20,.5)", "font": FONT,
            "heading-font": "Georgia, 'Times New Roman', serif",
            "hero-bg": "linear-gradient(180deg,#f2ece2,#e8dccb)", "hero-text": "#231f1b", "hero-muted": "#5d5349",
            "nav-bg": "rgba(250,247,242,.9)", "img-bg": "linear-gradient(135deg,#eadfce,#d9c7ad)",
            "badge-bg": "#efe3d1", "badge-text": "#6b4423", "footer-bg": "#231f1b", "footer-text": "#cfc4b6",
        },
        "extra": "h1,h2,h3{font-weight:600;letter-spacing:0}\n",
    },
    "fresh": {
        "about": "light, airy and green (health, eco, organic, garden, yoga, nature, medical, wellness)",
        "keywords": "eco organic health garden plant yoga nature green medical wellness farm vegan herbal",
        "vars": {
            "bg": "#f6fbf7", "bg-alt": "#e9f6ec", "surface": "#ffffff", "text": "#10261a", "muted": "#4f6b5a",
            "primary": "#16a34a", "primary-contrast": "#ffffff", "border": "#dbeede", "border-strong": "#bfdcc8",
            "radius": "18px", "radius-sm": "12px", "shadow": "0 10px 26px -16px rgba(22,101,52,.35)",
            "shadow-lg": "0 24px 46px -20px rgba(22,163,74,.45)", "font": FONT, "heading-font": FONT,
            "hero-bg": "linear-gradient(135deg,#d9f5e1,#b8ebc7)", "hero-text": "#10261a", "hero-muted": "#3f5d4b",
            "nav-bg": "rgba(246,251,247,.9)", "img-bg": "linear-gradient(135deg,#d9f5e1,#a7e3bb)",
            "badge-bg": "#d9f5e1", "badge-text": "#166534", "footer-bg": "#0f2a1b", "footer-text": "#a8c7b3",
        },
        "extra": "",
    },
}

DEFAULT_THEME = "clean-light"

BASE_CSS = """
*,*::before,*::after{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.6;-webkit-font-smoothing:antialiased}
img,svg,video{max-width:100%;display:block}
h1,h2,h3,h4{font-family:var(--heading-font);line-height:1.2;margin:0 0 .6em;letter-spacing:-.02em;color:var(--text)}
h1{font-size:clamp(2.2rem,5vw,3.6rem);font-weight:800}
h2{font-size:clamp(1.6rem,3vw,2.3rem);font-weight:700}
h3{font-size:1.2rem;font-weight:650}
p{margin:0 0 1em;color:var(--muted)}
a{color:var(--primary);text-decoration:none}
a:hover{text-decoration:underline}
ul,ol{padding-left:1.2rem;color:var(--muted)}
hr{border:0;border-top:1px solid var(--border);margin:2rem 0}

.container{width:min(1120px,92%);margin-inline:auto}
.section{padding:clamp(3rem,7vw,5.5rem) 0}
.alt{background:var(--bg-alt)}
.section-title{text-align:center;margin-bottom:2.2rem}
.muted{color:var(--muted)}
.lead{font-size:1.2rem;max-width:56ch}
.center{text-align:center}
.stack>*+*{margin-top:1rem}

.navbar{position:sticky;top:0;z-index:50;background:var(--nav-bg);backdrop-filter:saturate(1.4) blur(12px);-webkit-backdrop-filter:saturate(1.4) blur(12px);border-bottom:1px solid var(--border)}
.nav-inner{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.9rem 0;flex-wrap:wrap}
.brand{font-weight:800;font-size:1.25rem;color:var(--text);letter-spacing:-.02em}
.brand:hover{text-decoration:none}
.nav-links{display:flex;gap:1.4rem;flex-wrap:wrap;align-items:center}
.nav-links a{color:var(--muted);font-weight:500;transition:color .2s}
.nav-links a:hover,.nav-links a.active{color:var(--text);text-decoration:none}

.hero{padding:clamp(4rem,10vw,8rem) 0;background:var(--hero-bg);position:relative;overflow:hidden}
.hero h1{color:var(--hero-text)}
.hero p,.hero .lead{color:var(--hero-muted)}
.hero .btn-outline{color:var(--hero-text);border-color:currentColor}
.hero .btn-outline:hover{background:rgba(255,255,255,.12)}

.btn,button,input[type=submit]{display:inline-flex;align-items:center;justify-content:center;gap:.5rem;padding:.8rem 1.5rem;border:0;border-radius:var(--radius-sm);background:var(--primary);color:var(--primary-contrast);font:inherit;font-weight:600;cursor:pointer;transition:transform .15s,box-shadow .2s,filter .2s;box-shadow:0 8px 20px -8px var(--primary)}
.btn:hover,button:hover,input[type=submit]:hover{transform:translateY(-2px);filter:brightness(1.08);text-decoration:none}
.btn:active,button:active{transform:translateY(0)}
.btn-outline{background:transparent;color:var(--text);border:1.5px solid var(--border-strong);box-shadow:none}
.btn-outline:hover{background:var(--bg-alt)}
.btn-sm{padding:.5rem 1rem;font-size:.9rem}
.btn-row{display:flex;gap:.8rem;flex-wrap:wrap;margin-top:1.6rem}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:1.5rem}
.grid-2{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:2rem;align-items:center}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow);transition:transform .25s,box-shadow .25s;display:flex;flex-direction:column}
.card:hover{transform:translateY(-6px);box-shadow:var(--shadow-lg)}
.card-img{aspect-ratio:4/3;display:grid;place-items:center;font-size:4rem;background:var(--img-bg)}
.card-body{padding:1.2rem 1.3rem 1.4rem;display:flex;flex-direction:column;gap:.3rem;flex:1}
.card-body p{margin:0;font-size:.95rem}
.card-foot{display:flex;align-items:center;justify-content:space-between;gap:.6rem;margin-top:auto;padding-top:.9rem}
.price{font-weight:800;font-size:1.2rem;color:var(--text)}
.badge,.tag{display:inline-block;padding:.2rem .7rem;border-radius:999px;font-size:.75rem;font-weight:700;background:var(--badge-bg);color:var(--badge-text);width:fit-content}
.pill{display:inline-grid;place-items:center;min-width:1.4rem;height:1.4rem;padding:0 .4rem;border-radius:999px;background:var(--primary);color:var(--primary-contrast);font-size:.75rem;font-weight:700}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1.5rem;text-align:center}
.stats strong{display:block;font-size:2.2rem;color:var(--primary)}
.cta{background:var(--hero-bg);color:var(--hero-text);border-radius:var(--radius);padding:3rem;text-align:center;border:1px solid var(--border)}
.cta h2{color:var(--hero-text)}
.cta p{color:var(--hero-muted)}

form{display:grid;gap:1rem;max-width:560px}
.form-row{display:grid;gap:.4rem}
label{font-weight:600;font-size:.9rem;color:var(--text)}
input,textarea,select{width:100%;padding:.75rem 1rem;border-radius:var(--radius-sm);border:1px solid var(--border-strong);background:var(--surface);color:var(--text);font:inherit}
input:focus,textarea:focus,select:focus{outline:2px solid var(--primary);outline-offset:1px}
table{width:100%;border-collapse:collapse}
th,td{padding:.75rem 1rem;text-align:left;border-bottom:1px solid var(--border)}
th{color:var(--muted);font-size:.8rem;text-transform:uppercase;letter-spacing:.05em}

.footer,footer{background:var(--footer-bg);color:var(--footer-text);padding:2.5rem 0;text-align:center;font-size:.95rem}
.footer p,footer p{color:inherit;margin:0}
.footer a,footer a{color:inherit;text-decoration:underline}

@media (max-width:640px){.nav-inner{justify-content:center}.hero{text-align:center}.btn-row{justify-content:center}.hero .lead{margin-inline:auto}}
"""

# What the Coder is told about the stylesheet (kept short for small models).
DESIGN_SYSTEM = """A ready-made modern stylesheet `theme.css` (theme: {theme}) is already in the project. Link it in every
HTML page with <link rel="stylesheet" href="theme.css"> BEFORE any other stylesheet, and build the page from its classes:
- Page: <header class="navbar"><div class="container nav-inner"><a class="brand" href="index.html">Name</a><nav class="nav-links"><a href="index.html" class="active">Home</a><a href="#products">Products</a></nav></div></header>
- Hero: <section class="hero"><div class="container"><h1>Headline</h1><p class="lead">Subtitle</p><div class="btn-row"><a class="btn" href="#products">Shop now</a><a class="btn btn-outline" href="#about">Learn more</a></div></div></section>
- Section: <section class="section" id="products"><div class="container"><h2 class="section-title">Title</h2><div class="grid"> ...cards... </div></div></section> (add class "alt" for a tinted band)
- Card: <article class="card"><div class="card-img">👟</div><div class="card-body"><span class="badge">New</span><h3>Name</h3><p>Short text</p><div class="card-foot"><span class="price">$99</span><button class="btn btn-sm">Add to cart</button></div></div></article>
- Also available: .grid-2 (two columns), .stats (<div><strong>10k</strong>label</div>), .cta, .pill (counter bubble), .form-row with label+input, table, .footer.
- Use an emoji inside .card-img as the picture (no external images). Do NOT restyle body, navbar, cards or buttons yourself;
  put only small page-specific extras in styles.css (e.g. cart panel, special layouts)."""


def describe() -> str:
    return "\n".join(f"- {name}: {t['about']}" for name, t in THEMES.items())


def suggest(request: str) -> str:
    """Keyword-based theme guess (also the Designer's fallback)."""
    words = set(re.findall(r"[a-z]+", request.lower()))
    best, best_score = DEFAULT_THEME, 0
    for name, t in THEMES.items():
        score = len(words & set(t["keywords"].split()))
        if score > best_score:
            best, best_score = name, score
    return best


def explicit_theme(request: str) -> Optional[str]:
    """If the user names a look ("dark theme", "glass style", "elegant"), that choice always wins."""
    low = request.lower()
    for name in THEMES:                                   # theme named directly
        if name in low or name.replace("-", " ") in low:
            return name
    if re.search(r"\b(dark|black|night)\s*(theme|mode|ui|design|style|look|background)?\b", low) and "dark" in low:
        return "glass" if "glass" in low else "modern-dark"
    if re.search(r"\b(light|white|bright|minimal|clean)\s+(theme|mode|ui|design|style|look)\b", low):
        return "clean-light"
    return None


def _luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def render_css(theme: str, accent: Optional[str] = None) -> str:
    t = THEMES.get(theme) or THEMES[DEFAULT_THEME]
    v = dict(t["vars"])
    if accent and re.fullmatch(r"#[0-9a-fA-F]{6}", accent):
        v["primary"] = accent
        v["primary-contrast"] = "#111111" if _luminance(accent) > 0.6 else "#ffffff"
        v["shadow-lg"] = f"0 24px 50px -18px {accent}88"
    root = ":root{" + ";".join(f"--{k}:{val}" for k, val in v.items()) + "}"
    return f"/* DevForge theme: {theme if theme in THEMES else DEFAULT_THEME} */\n{root}\n{BASE_CSS}\n{t['extra']}"


DARK_THEMES = {"modern-dark", "glass"}
DUAL_TAIL = """
:root[data-theme="dark"]{color-scheme:dark}
:root[data-theme="light"]{color-scheme:light}
body,.navbar,.card,.btn,input,textarea,select,.footer,footer,.section{transition:background-color .25s,color .25s,border-color .25s}
.theme-toggle-float{position:fixed;right:1.2rem;bottom:1.2rem;z-index:100;width:3rem;height:3rem;padding:0;border-radius:50%;font-size:1.3rem;line-height:1;background:var(--surface);color:var(--text);border:1px solid var(--border-strong);box-shadow:var(--shadow-lg)}
"""

TOGGLE_JS = """/* DevForge light/dark theme switch. Works with the dark and light palettes in theme.css. */
(function () {
  var KEY = 'devforge-theme';
  var root = document.documentElement;
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  root.setAttribute('data-theme', saved === 'light' || saved === 'dark' ? saved : '__DEFAULT__');

  function setTheme(t, ours, btn) {
    root.setAttribute('data-theme', t);
    try { localStorage.setItem(KEY, t); } catch (e) {}
    if (btn) {
      btn.setAttribute('aria-label', 'Switch to ' + (t === 'dark' ? 'light' : 'dark') + ' theme');
      if (ours) btn.textContent = t === 'dark' ? '\\u2600\\uFE0F' : '\\uD83C\\uDF19';
    }
  }

  function init() {
    var btn = document.getElementById('theme-toggle') ||
      document.querySelector('.theme-toggle, [data-theme-toggle], button[id*="theme" i], button[class*="theme" i]');
    var ours = false;
    if (btn) {
      var clean = btn.cloneNode(true);          // drop any older, broken click handlers
      btn.parentNode.replaceChild(clean, btn);
      btn = clean;
    } else {
      btn = document.createElement('button');
      btn.id = 'theme-toggle';
      btn.type = 'button';
      btn.className = 'theme-toggle theme-toggle-float';
      document.body.appendChild(btn);
      ours = true;
    }
    setTheme(root.getAttribute('data-theme'), ours, btn);
    btn.addEventListener('click', function () {
      setTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark', ours, btn);
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
"""


def is_dark(theme: str) -> bool:
    return theme in DARK_THEMES


def read_current(css_text: str) -> Dict[str, Optional[str]]:
    """What theme.css currently is: {'theme': name|None, 'accent': '#rrggbb'|None, 'dual': bool}."""
    m = re.match(r"\s*/\* DevForge theme: ([\w-]+)", css_text or "")
    prim = re.search(r"--primary:(#[0-9a-fA-F]{6})", css_text or "")
    return {"theme": m.group(1) if m else None, "accent": prim.group(1) if prim else None,
            "dual": bool(css_text) and 'data-theme="light"' in css_text}


def dual_pair(current: Optional[str]) -> Dict[str, str]:
    """Pick the dark/light palettes for a switch: the site's own theme stays, the other side is added."""
    if current in THEMES and not is_dark(current):
        return {"dark": "modern-dark", "light": current}
    return {"dark": "modern-dark", "light": "clean-light"}


def render_dual_css(dark: str, light: str, accent: Optional[str] = None, default: str = "dark") -> str:
    """theme.css with BOTH palettes, switched by <html data-theme="dark|light">."""
    def vars_for(name: str) -> Dict[str, str]:
        v = dict(THEMES[name]["vars"])
        if accent and re.fullmatch(r"#[0-9a-fA-F]{6}", accent):
            v["primary"] = accent
            v["primary-contrast"] = "#111111" if _luminance(accent) > 0.6 else "#ffffff"
            v["shadow-lg"] = f"0 24px 50px -18px {accent}88"
        return v

    def block(sel: str, name: str) -> str:
        return sel + "{" + ";".join(f"--{k}:{val}" for k, val in vars_for(name).items()) + "}"

    first = dark if default == "dark" else light
    return (f"/* DevForge theme: {first} (dual: dark={dark}, light={light}) */\n"
            + block(":root", first) + "\n" + block(':root[data-theme="dark"]', dark) + "\n"
            + block(':root[data-theme="light"]', light) + f"\n{BASE_CSS}\n{DUAL_TAIL}")


def toggle_js(default: str = "dark") -> str:
    return TOGGLE_JS.replace("__DEFAULT__", "light" if default == "light" else "dark")


def design_system_text(theme: str) -> str:
    return DESIGN_SYSTEM.replace("{theme}", theme)


def parse_design(raw: str, fallback: str) -> Dict[str, str]:
    """Parse the Designer's reply; anything invalid falls back to the keyword suggestion."""
    spec = {"theme": fallback, "accent": "", "style": "", "sections": ""}
    m = re.search(r"THEME\s*:\s*([A-Za-z\- _]+)", raw, re.I)
    if m:
        guess = re.sub(r"[ _]+", "-", m.group(1).strip().lower())
        for name in THEMES:
            if guess == name or guess.startswith(name) or name in guess:
                spec["theme"] = name
                break
    m = re.search(r"ACCENT\s*:\s*(#[0-9a-fA-F]{6})", raw, re.I)
    if m:
        spec["accent"] = m.group(1)
    m = re.search(r"STYLE\s*:\s*(.+)", raw, re.I)
    if m:
        spec["style"] = m.group(1).strip()[:200]
    m = re.search(r"SECTIONS\s*:\s*(.+)", raw, re.I)
    if m:
        spec["sections"] = m.group(1).strip()[:200]
    return spec
