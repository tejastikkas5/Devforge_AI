"""Modern chat view drawn with real HTML/CSS (Qt WebEngine).

It replaces the old QTextBrowser look (square tables, no rounded corners) with chat bubbles,
avatars, rounded code blocks with a Copy button, a live "working" timeline and pipeline chips.
It keeps the same small interface as the old view: messages, progress, live, placeholder,
refresh() and retheme(), so the main window does not change.

The page is loaded once; after that only the message HTML is pushed in with JavaScript, so
streaming answers update smoothly without flicker or losing the scroll position.
"""
import json
import re
import time
from typing import Callable, Dict, List, Optional

from devforge.ui import fmt_duration, reply_durations

import markdown
from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QColor, QDesktopServices
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView

try:                                        # syntax colours for code blocks, if Pygments is installed
    from pygments.formatters import HtmlFormatter
    _HAS_PYGMENTS = True
except ImportError:                         # pragma: no cover
    _HAS_PYGMENTS = False

_MD_EXT = ["fenced_code", "tables", "sane_lists", "nl2br"]
_MD_CFG = {}
if _HAS_PYGMENTS:
    _MD_EXT.append("codehilite")
    _MD_CFG = {"codehilite": {"guess_lang": False, "css_class": "hl"}}


_LIST = re.compile(r"^\s*(?:[-*+]|\d+\.)\s")


def _fix_lists(text: str) -> str:
    """The agents write '**Files**' straight above '- a.html' with no blank line, which Markdown
    reads as one paragraph. Add the missing blank line so lists render as real lists."""
    out, prev_list, in_code = [], True, False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_code = not in_code
        is_list = not in_code and bool(_LIST.match(line))
        if is_list and not prev_list and out and out[-1].strip():
            out.append("")
        out.append(line)
        prev_list = is_list or (prev_list and line.startswith(("  ", "\t")) and line.strip() != "")
    return "\n".join(out)


def md_rich(text: str) -> str:
    return markdown.markdown(_fix_lists(text), extensions=_MD_EXT, extension_configs=_MD_CFG)


def _pygments_css(dark: bool) -> str:
    if not _HAS_PYGMENTS:
        return ""
    for style in (("github-dark", "monokai") if dark else ("friendly", "default")):
        try:
            return HtmlFormatter(style=style).get_style_defs(".hl")
        except Exception:                   # noqa: BLE001 - style missing in this Pygments version
            continue
    return ""


SHELL = r"""<!doctype html><html><head><meta charset="utf-8">
<style id="theme"></style>
<style>
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font: 14px/1.6 'Segoe UI Variable Text', 'Segoe UI', sans-serif;
       -webkit-font-smoothing: antialiased; }
body::before { content: ""; position: fixed; inset: 0; pointer-events: none;
       background: radial-gradient(900px 380px at 70% -120px, var(--glow), transparent 70%); }
#feed { position: relative; padding: 18px 18px 26px; max-width: 980px; margin: 0 auto; }
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: var(--scroll); border-radius: 8px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
::-webkit-scrollbar-track { background: transparent; }
::selection { background: var(--selection); }

/* message rows */
.row { display: flex; gap: 10px; margin: 0 0 18px; animation: rise .25s ease-out both; }
.row.user { flex-direction: row-reverse; }
@keyframes rise { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
.avatar { flex: 0 0 32px; height: 32px; border-radius: 11px; display: grid; place-items: center;
          font-size: 13px; font-weight: 700; color: #fff; box-shadow: 0 4px 12px var(--shadow); }
.avatar.bot { background: linear-gradient(135deg, var(--g1), var(--g2)); font-size: 15px; }
.avatar.me { background: var(--me-av); color: var(--accent-text); box-shadow: none; border: 1px solid var(--border); }
.msg { min-width: 0; max-width: min(86%, 820px); }
.row.bot .msg { flex: 1; max-width: 100%; }
.name { font-size: 12px; font-weight: 600; color: var(--muted); margin: 2px 4px 5px; letter-spacing: .2px; }
.row.user .name { text-align: right; }

.bubble { border-radius: 16px; padding: 12px 16px; overflow-wrap: anywhere; }
.row.user .bubble { background: linear-gradient(135deg, var(--g1), var(--g2)); color: #fff;
          border-top-right-radius: 5px; box-shadow: 0 6px 18px var(--shadow); white-space: pre-wrap; }
.row.bot .bubble { background: var(--card); border: 1px solid var(--border); border-top-left-radius: 5px;
          box-shadow: 0 4px 16px var(--shadow-soft); }

/* markdown inside the assistant card */
.bubble p { margin: 4px 0 8px; }
.bubble p:last-child { margin-bottom: 0; }
.bubble ul, .bubble ol { margin: 4px 0 10px; padding-left: 20px; }
.bubble li { margin: 3px 0; }
.bubble li::marker { color: var(--accent); }
.bubble h1, .bubble h2, .bubble h3 { color: var(--strong); margin: 12px 0 6px; line-height: 1.3; }
.bubble h1 { font-size: 19px; } .bubble h2 { font-size: 17px; } .bubble h3 { font-size: 15px; }
.bubble strong, .bubble b { color: var(--strong); font-weight: 650; }
.bubble p > strong:only-child { display: inline-block; margin-top: 6px; font-size: 13px; letter-spacing: .3px;
          text-transform: uppercase; color: var(--accent-text); }
.bubble a { color: var(--link); text-decoration: none; border-bottom: 1px solid transparent; }
.bubble a:hover { border-bottom-color: var(--link); }
.bubble code { font-family: 'Cascadia Code', Consolas, monospace; font-size: 12.5px; background: var(--chip);
          color: var(--inline-code); padding: 1px 7px; border-radius: 6px; border: 1px solid var(--chip-border); }
.bubble table { border-collapse: separate; border-spacing: 0; margin: 8px 0; border: 1px solid var(--border);
          border-radius: 10px; overflow: hidden; }
.bubble th, .bubble td { padding: 7px 12px; border-bottom: 1px solid var(--border); text-align: left; }
.bubble th { background: var(--chip); color: var(--strong); font-weight: 600; }
.bubble tr:last-child td { border-bottom: none; }
.bubble blockquote { margin: 8px 0; padding: 6px 12px; border-left: 3px solid var(--accent); background: var(--chip);
          border-radius: 0 8px 8px 0; color: var(--muted); }
.bubble hr { border: none; border-top: 1px solid var(--border); margin: 12px 0; }

/* code blocks */
.code { margin: 10px 0; border-radius: 12px; overflow: hidden; border: 1px solid var(--code-border);
        background: var(--code-bg); }
.code-head { display: flex; align-items: center; justify-content: space-between; padding: 6px 8px 6px 12px;
        background: var(--code-head); font-size: 11.5px; color: var(--muted); }
.dots { display: flex; gap: 6px; } .dots i { width: 9px; height: 9px; border-radius: 50%; display: block; }
.dots i:nth-child(1) { background: #ff5f57; } .dots i:nth-child(2) { background: #febc2e; }
.dots i:nth-child(3) { background: #28c840; }
.copy { font: 600 11px 'Segoe UI', sans-serif; color: var(--muted); background: transparent; border: 1px solid var(--border);
        border-radius: 7px; padding: 3px 10px; cursor: pointer; }
.copy:hover { color: var(--strong); border-color: var(--accent); }
.code pre { margin: 0; padding: 12px 14px; overflow-x: auto; font: 12.5px/1.55 'Cascadia Code', Consolas, monospace;
        color: var(--code-text); background: transparent !important; }
.code pre code { background: none; border: none; padding: 0; color: inherit; font-size: inherit; }
.hl { background: transparent !important; }

/* status lines: "- ✅ file - ok" / "- ❌ file - error" */
.bubble li.ok { color: var(--text); }
.bubble li.bad { color: var(--danger-text); }

/* pipeline footer from <sub>: Researcher → Designer → ... */
.pipeline { display: block; margin-top: 12px; padding-top: 8px; border-top: 1px dashed var(--border); line-height: 1; }
.chip { display: inline-block; margin: 4px 6px 0 0; font-size: 11px; line-height: 1.4; padding: 3px 9px; border-radius: 999px; background: var(--chip);
        color: var(--muted); border: 1px solid var(--chip-border); }
.chip b { color: var(--accent-text); font-weight: 600; }

/* live "working" timeline */
.work { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 12px 14px;
        box-shadow: 0 4px 16px var(--shadow-soft); }
.work-title { display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 13px; color: var(--strong);
        margin-bottom: 8px; }
.step { display: flex; align-items: flex-start; gap: 10px; padding: 5px 2px; font-size: 13px; color: var(--muted); }
.step .ic { flex: 0 0 18px; height: 18px; border-radius: 50%; display: grid; place-items: center; font-size: 11px;
        margin-top: 2px; }
.step.done .ic { background: var(--ok-bg); color: var(--ok); }
.step.run { color: var(--text); }
.step.run .ic { border: 2px solid var(--chip-border); border-top-color: var(--accent); animation: spin .8s linear infinite; }
.step b { color: var(--strong); font-weight: 600; }
@keyframes spin { to { transform: rotate(360deg); } }
.spinner { width: 14px; height: 14px; border-radius: 50%; border: 2px solid var(--chip-border);
        border-top-color: var(--accent); animation: spin .8s linear infinite; }
.typing { display: inline-flex; gap: 5px; padding: 4px 0; }
.typing i { width: 7px; height: 7px; border-radius: 50%; background: var(--accent); opacity: .35;
        animation: blink 1.2s infinite; }
.typing i:nth-child(2) { animation-delay: .2s; } .typing i:nth-child(3) { animation-delay: .4s; }
@keyframes blink { 50% { opacity: 1; transform: translateY(-2px); } }

/* time taken / live clock */
.foot { display: flex; justify-content: flex-end; margin-top: 12px; padding-top: 8px; border-top: 1px solid var(--border); }
.took { font-size: 11.5px; color: var(--muted); background: var(--chip); border: 1px solid var(--chip-border);
        padding: 3px 10px; border-radius: 999px; }
.took b { color: var(--accent-text); font-weight: 650; }
.clock { font: 600 11.5px 'Cascadia Code', Consolas, monospace; color: var(--accent-text); background: var(--chip);
        border: 1px solid var(--chip-border); padding: 2px 9px; border-radius: 999px; }
.grow { flex: 1; }

/* empty state */
.empty { text-align: center; margin: 12vh auto 0; max-width: 460px; color: var(--muted); animation: rise .35s ease-out both; }
.empty .logo { width: 64px; height: 64px; margin: 0 auto 16px; border-radius: 20px; display: grid; place-items: center;
        font-size: 30px; color: #fff; background: linear-gradient(135deg, var(--g1), var(--g2));
        box-shadow: 0 12px 30px var(--shadow); }
.empty h2 { color: var(--strong); font-size: 20px; margin: 0 0 8px; }
.empty b { color: var(--accent-text); }
.empty i { display: inline-block; margin-top: 6px; padding: 6px 12px; border-radius: 10px; background: var(--chip);
        border: 1px solid var(--chip-border); font-style: normal; color: var(--text); }
</style></head>
<body><div id="feed"></div>
<script>
function fmt(s) {
  if (s < 10) return s.toFixed(1) + 's';
  s = Math.round(s); if (s < 60) return s + 's';
  var m = Math.floor(s / 60); s = s % 60;
  if (m < 60) return m + 'm ' + (s < 10 ? '0' : '') + s + 's';
  var h = Math.floor(m / 60); m = m % 60; return h + 'h ' + (m < 10 ? '0' : '') + m + 'm';
}
setInterval(function () {        // tick every live clock once a second
  document.querySelectorAll('.clock[data-start]').forEach(function (c) {
    c.textContent = '⏱ ' + fmt((Date.now() - Number(c.dataset.start)) / 1000);
  });
}, 1000);
function setTheme(css) { document.getElementById('theme').textContent = css; }
function decorate(root) {
  // code blocks -> window-style card with a Copy button
  root.querySelectorAll('pre').forEach(function (pre) {
    if (pre.closest('.code')) return;
    var host = pre.parentElement.classList.contains('hl') ? pre.parentElement : pre;
    var box = document.createElement('div'); box.className = 'code';
    var head = document.createElement('div'); head.className = 'code-head';
    head.innerHTML = '<span class="dots"><i></i><i></i><i></i></span><button class="copy">Copy</button>';
    host.parentNode.insertBefore(box, host); box.appendChild(head); box.appendChild(host);
    head.querySelector('.copy').onclick = function () {
      var t = document.createElement('textarea'); t.value = pre.innerText; document.body.appendChild(t);
      t.select(); document.execCommand('copy'); t.remove();
      this.textContent = 'Copied'; var b = this; setTimeout(function () { b.textContent = 'Copy'; }, 1200);
    };
  });
  // ✅ / ❌ list items
  root.querySelectorAll('li').forEach(function (li) {
    var s = li.textContent.trim();
    if (s.indexOf('❌') === 0) li.classList.add('bad'); else if (s.indexOf('✅') === 0) li.classList.add('ok');
  });
  // <sub>a → b → c</sub>  ->  chips
  root.querySelectorAll('sub').forEach(function (sub) {
    var wrap = document.createElement('div'); wrap.className = 'pipeline';
    sub.innerHTML.split(' → ').forEach(function (part) {
      var m = part.match(/^([^(:]+)(.*)$/);
      var c = document.createElement('span'); c.className = 'chip';
      c.innerHTML = m ? '<b>' + m[1] + '</b>' + m[2] : part; wrap.appendChild(c);
    });
    sub.replaceWith(wrap);
  });
}
function render(html) {
  var se = document.scrollingElement;
  var stick = se.scrollTop + window.innerHeight >= se.scrollHeight - 60;
  var feed = document.getElementById('feed');
  var old = feed.childElementCount, keep = se.scrollTop;
  feed.innerHTML = html; decorate(feed);
  // only animate rows that are new since the last render
  Array.prototype.forEach.call(feed.children, function (el, i) { if (i < old) el.style.animation = 'none'; });
  se.scrollTop = stick ? se.scrollHeight : keep;
}
</script></body></html>"""


def _theme_css(p: Dict[str, str], dark: bool) -> str:
    v = {
        "bg": p["bg"], "text": p["text"], "strong": p["strong"], "muted": p["muted"], "border": p["border"],
        "card": p["bubble_bot"], "accent": p["accent"], "accent-text": p["accent_text"], "link": p["link"],
        "g1": p["grad1"], "g2": p["grad2"], "scroll": p["scroll"], "selection": p["selection"],
        "inline-code": p["inline_code"], "code-text": p["code_text"],
        "code-bg": "#0b0c1a" if dark else "#fbfaff", "code-head": "#14152a" if dark else "#f1effc",
        "code-border": p["border"],
        "chip": "rgba(139,125,255,.10)" if dark else "rgba(108,92,231,.07)",
        "chip-border": "rgba(139,125,255,.22)" if dark else "rgba(108,92,231,.18)",
        "me-av": "#1b1d38" if dark else "#efecff",
        "shadow": "rgba(80,60,220,.35)" if dark else "rgba(108,92,231,.25)",
        "shadow-soft": "rgba(0,0,0,.25)" if dark else "rgba(40,40,110,.06)",
        "glow": "rgba(124,108,255,.16)" if dark else "rgba(108,92,231,.10)",
        "ok": "#3ddc97" if dark else "#16a34a", "ok-bg": "rgba(61,220,151,.15)" if dark else "rgba(22,163,74,.12)",
        "danger-text": "#ff8a8f" if dark else "#d93036",
    }
    root = ":root{" + ";".join(f"--{k}:{val}" for k, val in v.items()) + "}"
    return root + _pygments_css(dark)


class _Page(QWebEnginePage):
    """Open clicked links in the normal browser instead of inside the chat."""

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            QDesktopServices.openUrl(url)
            return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)


class WebChatView(QWebEngineView):
    def __init__(self, palette: Callable[[], Dict[str, str]], is_dark: Callable[[], bool]):
        super().__init__()
        self._pal, self._is_dark = palette, is_dark
        self.setPage(_Page(self))
        self.messages: List[Dict] = []
        self.progress: List[str] = []
        self.live: Optional[str] = None
        self.placeholder = ""
        self.started: Optional[float] = None     # when the running prompt was sent (for the live clock)
        self._ready = False
        self._dirty = True
        self._last = None
        self.page().setBackgroundColor(QColor(self._pal()["bg"]))
        self.loadFinished.connect(self._loaded)
        self.setHtml(SHELL, QUrl("about:blank"))
        self._timer = QTimer(self)
        self._timer.setInterval(120)
        self._timer.timeout.connect(self._flush)
        self._timer.start()

    # -- same interface as the old view
    def refresh(self):
        self._dirty = True

    def retheme(self):
        self.page().setBackgroundColor(QColor(self._pal()["bg"]))
        if self._ready:
            self._apply_theme()
        self._last = None
        self._dirty = True
        self._flush()

    # -- internals
    def _loaded(self, ok: bool):
        self._ready = True
        self._apply_theme()
        self._last = None
        self._dirty = True
        self._flush()

    def _apply_theme(self):
        css = _theme_css(self._pal(), self._is_dark())
        self.page().runJavaScript(f"setTheme({json.dumps(css)})")

    def _clock(self) -> str:
        """A live 'elapsed' counter; the page's JavaScript ticks it every second."""
        if not self.started:
            return ""
        return f'<span class="clock" data-start="{self.started * 1000:.0f}">⏱ {fmt_duration(time.time() - self.started)}</span>'

    @staticmethod
    def _row(html_body: str, user: bool, live: str = "", took: Optional[float] = None) -> str:
        if user:
            return ('<div class="row user"><div class="avatar me">◉</div><div class="msg">'
                    f'<div class="name">You</div><div class="bubble">{html_body}</div></div></div>')
        foot = (f'<div class="foot"><span class="took">⏱ Completed in <b>{fmt_duration(took)}</b></span></div>'
                if took is not None else "")
        return ('<div class="row bot"><div class="avatar bot">⚒</div><div class="msg">'
                f'<div class="name">DevForge{" · typing " + live if live else ""}</div>'
                f'<div class="bubble">{html_body}{foot}</div></div></div>')

    def _build(self) -> str:
        import html as _html
        if not self.messages and not self.progress and self.live is None:
            return f'<div class="empty"><div class="logo">⚒</div>{self.placeholder}</div>'
        parts = []
        for m, took in zip(self.messages, reply_durations(self.messages)):
            if m["role"] == "user":
                parts.append(self._row(_html.escape(m["content"]), True))
            else:
                parts.append(self._row(md_rich(m["content"]), False, took=took))
        if self.live is not None:
            body = md_rich(self.live) if self.live else '<span class="typing"><i></i><i></i><i></i></span>'
            parts.append(self._row(body, False, live=self._clock() or " "))
        if self.progress:
            steps = []
            for line in self.progress:
                running = line.startswith("⏳")
                text = line[1:].lstrip() if line[:1] in ("⏳", "✓") else line
                steps.append(f'<div class="step {"run" if running else "done"}"><span class="ic">'
                             f'{"" if running else "✓"}</span><span>{text}</span></div>')
            busy = any(s.startswith("⏳") for s in self.progress)
            title = (f'<span class="spinner"></span> Working on it… <span class="grow"></span>{self._clock()}'
                     if busy else '✓ Steps')
            parts.append('<div class="row bot"><div class="avatar bot">⚒</div><div class="msg">'
                         f'<div class="name">DevForge</div><div class="work"><div class="work-title">{title}</div>'
                         f'{"".join(steps)}</div></div></div>')
        return "".join(parts)

    def _flush(self):
        if not (self._dirty and self._ready):
            return
        self._dirty = False
        html_doc = self._build()
        if html_doc == self._last:
            return
        self._last = html_doc
        self.page().runJavaScript(f"render({json.dumps(html_doc)})")
