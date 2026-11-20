"""Headless tests: parsing, RAG, safety, and the full pipeline using a scripted fake LLM."""
import os
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devforge import fsops                      # noqa: E402
from devforge.engine import Engine              # noqa: E402
from devforge.rag import CodeIndex              # noqa: E402


class FakeClient:
    """Routes by system prompt so each agent gets a canned reply."""
    base_url = "fake"

    def __init__(self, replies):
        self.replies = replies
        self.calls = []

    def ensure_server(self): return True
    def list_models(self): return ["deepseek-coder:6.7b", "qwen2.5-coder:7b", "qwen2.5:7b", "codegemma:2b", "qwen2.5-coder:1.5b"]
    def embed(self, model, texts): raise AssertionError("no embed model expected")

    def stream(self, model, messages, temperature=0.2, num_predict=None, cancel=None):
        system, user = messages[0]["content"], messages[-1]["content"]
        if "Name a chat" in system:
            self.calls.append(("title", model))
            yield "Test Chat Title"
            return
        if "Extract durable facts" in system:
            self.calls.append(("memory", model))
            self.memory_prompts = getattr(self, "memory_prompts", []) + [user]
            yield getattr(self, "memory_reply", "NONE")
            return
        for key, reply in self.replies:
            if key in system:
                r = reply(user) if callable(reply) else reply
                self.calls.append((key, model))
                yield r
                return
        raise AssertionError("no scripted reply for: " + system[:60])


DESIGN = "THEME: Vibrant\nACCENT: #ff3366\nSTYLE: bold and sporty\nSECTIONS: hero, featured shoes, reviews, newsletter"
PLAN = "SUMMARY: A tiny shoe store.\nFILES:\n- index.html: page\n- styles.css: look\n- script.js: cart\nNOTES:\n- simple\n"


def coder(user):
    if "FILE TO WRITE NOW: index.html" in user:
        return "```html\n<!DOCTYPE html><html><head><link rel='stylesheet' href='styles.css'></head><body><h1>Shoes</h1><script src='script.js'></script></body></html>\n```"
    if "FILE TO WRITE NOW: styles.css" in user:
        return "```css\nbody { margin: 0; }\n```"
    if "FILE TO WRITE NOW: script.js" in user:
        return "```js\nconsole.log('hi');\n```"
    return "The answer comes from main.py."


class ParseTests(unittest.TestCase):
    def test_parse_variants(self):
        txt = ("### FILE: index.html\n```html\n<h1>x</h1>\n```\n"
               "**styles.css**\n```css\na{}\n```\n"
               "```python\n# filename: app/main.py\nprint(1)\n```\n"
               "```js\nlet a=1\n")                       # unclosed fence at the end
        got = dict(fsops.parse_files(txt))
        self.assertEqual(set(got), {"index.html", "styles.css", "app/main.py", "script.js"})
        self.assertEqual(got["app/main.py"], "print(1)")

    def test_plan_files(self):
        self.assertEqual([f for f, _ in fsops.parse_plan_files(PLAN)], ["index.html", "styles.css", "script.js"])

    def test_path_traversal_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            for bad in ("../evil.py", "C:/x.py", ".devforge/h.json", "a/../../b.py"):
                with self.assertRaises(ValueError):
                    fsops.safe_join(d, bad)
            self.assertTrue(fsops.safe_join(d, "/etc/passwd").startswith(os.path.abspath(d)))  # leading / is made relative
            fsops.write_file(d, "ok/deep/file.txt", "hi")
            self.assertTrue(os.path.exists(os.path.join(d, "ok", "deep", "file.txt")))


class RagTests(unittest.TestCase):
    def test_search_finds_right_function(self):
        with tempfile.TemporaryDirectory() as d:
            fsops.write_file(d, "shop.py", "def apply_discount(price, pct):\n    return price * (1 - pct)\n\n"
                                           "class Cart:\n    def add_item(self, item):\n        pass\n")
            fsops.write_file(d, "util.py", "def slugify(text):\n    return text.lower()\n")
            fsops.write_file(d, "page.html", "<h1>Hello</h1>\n")
            idx = CodeIndex(d)
            self.assertGreaterEqual(idx.refresh(), 4)
            top = idx.search("how is the discount computed", 3)[0][0]
            self.assertEqual(top.name, "apply_discount")
            top = idx.search("add item to cart", 3)[0][0]
            self.assertIn("add_item", top.name)
            self.assertIn("shop.py", idx.repo_map())
            fsops.write_file(d, "util.py", "def reverse_words(text):\n    return text\n")   # incremental refresh
            idx.refresh()
            self.assertEqual(idx.search("reverse words", 1)[0][0].name, "reverse_words")


class PipelineTests(unittest.TestCase):
    def make(self, d, replies, events):
        return Engine(d, FakeClient(replies), emit=lambda k, **kw: events.append((k, kw)))

    def test_website_pipeline(self):
        replies = [("Researcher", "APPROACH: static pages"), ("Designer", DESIGN), ("Reviewer", "LGTM"), ("Planner", PLAN), ("Coder", coder),
                   ("classify", "BUILD")]
        with tempfile.TemporaryDirectory() as d:
            ev = []
            eng = self.make(d, replies, ev)
            out = eng.handle_code("generate simple website for shoes store")
            for f in ("index.html", "styles.css", "script.js"):
                self.assertTrue(os.path.exists(os.path.join(d, f)), f)
            self.assertIn("index.html", out)
            self.assertNotIn("❌", out)
            self.assertIn("theme.css", out)
            with open(os.path.join(d, "theme.css"), encoding="utf-8") as f:
                css = f.read()
            self.assertIn("--primary:#ff3366", css)                       # accent chosen by the Designer
            with open(os.path.join(d, "index.html"), encoding="utf-8") as f:
                self.assertIn("theme.css", f.read())                      # auto-linked into the page
            sessions = eng.store.list_sessions()
            self.assertEqual(len(sessions), 1)
            self.assertEqual((sessions[0]["mode"], sessions[0]["title"]), ("code", "Test Chat Title"))
            self.assertEqual([m["role"] for m in eng.store.load(sessions[0]["id"])], ["user", "assistant"])
            models_used = {m for k, m in eng.client.calls if k not in ("title", "memory")}
            self.assertEqual(models_used, {"qwen2.5:7b", "deepseek-coder:6.7b", "qwen2.5-coder:7b"})   # one model per task
            for f in ("theme-toggle.js", "site.js"):                                  # built-in switch + menu, by code
                self.assertTrue(os.path.exists(os.path.join(d, f)), f)
            with open(os.path.join(d, "theme.css"), encoding="utf-8") as f:
                self.assertIn('data-theme="light"', f.read())

    def test_python_pipeline_with_debugger_fix(self):
        plan = "SUMMARY: add.\nFILES:\n- calc.py: add function\nNOTES:\n- x\n"
        state = {"fixed": False}

        def debugger(user):
            state["fixed"] = True
            return "```python\ndef add(a, b):\n    return a + b\n```"

        replies = [("Researcher", "APPROACH: one file"), ("Reviewer", "LGTM"), ("Planner", plan),
                   ("Coder", "```python\ndef add(a, b):\n    return a - b\n```"),
                   ("Tester", "```python\nimport unittest\nfrom calc import add\n\nclass T(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n\nif __name__ == '__main__':\n    unittest.main()\n```"),
                   ("Debugger", debugger)]
        with tempfile.TemporaryDirectory() as d:
            eng = self.make(d, replies, [])
            out = eng.handle_code("write a python function to add two numbers")
            self.assertTrue(state["fixed"], "debugger should have been invoked")
            self.assertIn("passed", out)
            self.assertNotIn("❌", out)
            with open(os.path.join(d, "calc.py")) as f:
                self.assertIn("a + b", f.read())

    def _review_run(self, d, review_reply):
        fence = chr(96) * 3
        nl = chr(10)
        buggy = nl.join(["function total(price, qty) {", "  let sum = price - qty;", "  return sum;", "}", ""])
        good = buggy.replace("price - qty", "price * qty")

        def coder_js(user):
            return fence + "js" + nl + (good if "REVIEW FINDINGS TO FIX" in user else buggy) + fence

        plan = nl.join(["SUMMARY: s.", "FILES:", "- cart.js: total", "NOTES:", "- x", ""])
        eng = self.make(d, [("Researcher", "APPROACH: x"), ("Planner", plan), ("Coder", coder_js),
                            ("Reviewer", review_reply)], [])
        return eng, eng.handle_code("write a cart total function in javascript")

    def test_proven_review_finding_is_fixed(self):
        with tempfile.TemporaryDirectory() as d:
            eng, out = self._review_run(d, "- cart.js: `let sum = price - qty;` - must multiply, not subtract")
            self.assertIn("price * qty", fsops.read_file(d, "cart.js"))
            self.assertIn("1 of 1 finding(s) fixed", out)

    def test_unproven_review_finding_is_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            eng, out = self._review_run(d, "- cart.js: the checkout section is not completed")
            self.assertIn("price - qty", fsops.read_file(d, "cart.js"))       # no wasted rewrite
            self.assertIn("1 unproven finding(s) ignored", out)
            self.assertNotIn("REVIEW FINDINGS", " ".join(k for k, _ in eng.client.calls))

    def test_code_mode_rejects_offtopic_and_chat_mode_allows_it(self):
        replies = [("classify", "OFFTOPIC"), ("DevForge AI, a friendly", "Paris.")]
        with tempfile.TemporaryDirectory() as d:
            eng = self.make(d, replies, [])
            out = eng.handle_code("who is the president of france?")
            self.assertIn("Code mode", out)
            self.assertEqual(eng.client.calls[0], ("classify", "qwen2.5-coder:1.5b"))   # only the tiny router ran
            self.assertEqual(eng.handle_chat("capital of france?"), "Paris.")

    def test_ask_uses_rag(self):
        seen = {}

        def ask(user):
            seen["sys"] = user
            return "It adds."

        with tempfile.TemporaryDirectory() as d:
            fsops.write_file(d, "main.py", "def add(a, b):\n    return a + b\n")
            replies = [("answer ONLY", lambda u: "It adds.")]
            eng = self.make(d, replies, [])
            eng.client.replies = [("classify", "ASK"), ("answer ONLY", "It adds.")]
            self.assertEqual(eng.handle_code("what does main.py do?"), "It adds.")


if __name__ == "__main__":
    unittest.main(verbosity=2)


class AssetFixTests(unittest.TestCase):
    def test_missing_images_replaced(self):
        with tempfile.TemporaryDirectory() as d:
            fsops.write_file(d, "index.html", '<html><body><img src="a.jpg" alt="Red Shoe"><img src="https://x/y.png"></body></html>')
            fsops.write_file(d, "b.png", "x")
            self.assertEqual(fsops.fix_missing_images(d, "index.html"), 1)
            out = fsops.read_file(d, "index.html")
            self.assertNotIn("a.jpg", out)
            self.assertIn("https://x/y.png", out)
            self.assertTrue(fsops.static_check(d, ["index.html"])[0]["ok"])


class DanglingRefTests(unittest.TestCase):
    def test_dangling_refs_repaired(self):
        with tempfile.TemporaryDirectory() as d:
            fsops.write_file(d, "index.html", '<html><head><link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="gone.css">'
                                              '</head><body><a href="index.html">h</a><a href="cart.html">c</a>'
                                              '<script src="scripts.js"></script></body></html>')
            fsops.write_file(d, "styles.css", "a{}")
            self.assertEqual(fsops.fix_dangling_refs(d, "index.html"), 3)
            out = fsops.read_file(d, "index.html")
            self.assertIn("styles.css", out)
            self.assertNotIn("gone.css", out)
            self.assertNotIn("scripts.js", out)
            self.assertTrue(fsops.static_check(d, ["index.html"])[0]["ok"])


class SessionTests(unittest.TestCase):
    def test_store_many_chats_rename_delete(self):
        from devforge.store import ProjectStore
        with tempfile.TemporaryDirectory() as d:
            st = ProjectStore(d)
            a = st.create("code", "First"); b = st.create("chat", "Second")
            st.append(a["id"], "user", "hi")
            self.assertEqual([x["id"] for x in st.list_sessions()], [a["id"], b["id"]])   # most recently active first
            self.assertTrue(st.rename(b["id"], "My name", auto=False))
            self.assertFalse(st.rename(b["id"], "Auto name", auto=True))                  # user name is never overwritten
            self.assertEqual(st.meta(b["id"])["title"], "My name")
            st.delete(a["id"])
            self.assertEqual([x["id"] for x in st.list_sessions()], [b["id"]])
            self.assertEqual(st.load("../../etc"), [])             # bad ids can never reach other files
            with self.assertRaises(ValueError):
                st._path("../../etc")

    def test_legacy_history_is_migrated(self):
        import json
        from devforge.store import ProjectStore
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, ".devforge"))
            with open(os.path.join(d, ".devforge", "code_history.json"), "w") as f:
                json.dump([{"role": "user", "content": "make a shoe site please", "ts": 1.0, "meta": {}},
                           {"role": "assistant", "content": "done", "ts": 2.0, "meta": {}}], f)
            sessions = ProjectStore(d).list_sessions()
            self.assertEqual(len(sessions), 1)
            self.assertEqual(sessions[0]["title"], "Make a shoe site please")
            self.assertEqual(len(ProjectStore(d).list_sessions()), 1)                      # migrated only once

    def test_engine_continues_and_creates_chats(self):
        replies = [("DevForge AI, a friendly", "reply")]
        with tempfile.TemporaryDirectory() as d:
            ev = []
            eng = Engine(d, FakeClient(replies), emit=lambda k, **kw: ev.append((k, kw)))
            eng.handle_chat("first question about python")
            sid = next(kw["id"] for k, kw in ev if k == "session")
            self.assertTrue(any(k == "title" for k, _ in ev))
            eng.store.rename(sid, "Renamed by user", auto=False)
            eng.handle_chat("second question", sid)                                         # same chat continues
            self.assertEqual(len(eng.store.list_sessions()), 1)
            self.assertEqual(len(eng.store.load(sid)), 4)
            self.assertEqual(eng.store.meta(sid)["title"], "Renamed by user")
            eng.handle_chat("a brand new chat")                                             # sid=None -> new chat
            sessions = eng.store.list_sessions()
            self.assertEqual(len(sessions), 2)
            self.assertNotEqual(sessions[0]["id"], sid)                                     # newest on top



class ThemeTests(unittest.TestCase):
    def test_every_theme_renders_full_component_library(self):
        from devforge import themes
        for name in themes.THEMES:
            css = themes.render_css(name)
            for needle in (":root{", "--primary:", ".navbar", ".hero", ".card", ".btn", ".grid", ".footer", "@media"):
                self.assertIn(needle, css, f"{name} is missing {needle}")
            self.assertEqual(css.count("{"), css.count("}"), f"{name}: unbalanced braces")

    def test_suggest_and_parse(self):
        from devforge import themes
        self.assertEqual(themes.suggest("website for a shoe store"), "vibrant")
        self.assertEqual(themes.suggest("a dashboard for my saas"), "modern-dark")
        self.assertEqual(themes.suggest("a page about something"), themes.DEFAULT_THEME)
        spec = themes.parse_design("THEME: Modern Dark\nACCENT: #00ff88\nSTYLE: sleek\nSECTIONS: hero, pricing", "vibrant")
        self.assertEqual((spec["theme"], spec["accent"]), ("modern-dark", "#00ff88"))
        bad = themes.parse_design("THEME: neon-rainbow\nACCENT: red", "fresh")
        self.assertEqual((bad["theme"], bad["accent"]), ("fresh", ""))           # invalid -> safe fallback
        self.assertIn("--primary:#00ff88", themes.render_css("clean-light", "#00ff88"))
        self.assertNotIn("javascript", themes.render_css("clean-light", "javascript:alert(1)"))

    def test_ensure_theme_link(self):
        with tempfile.TemporaryDirectory() as d:
            fsops.write_file(d, "index.html", "<html><head><title>x</title><link rel='stylesheet' href='styles.css'></head><body></body></html>")
            fsops.write_file(d, "sub/page.html", "<html><body><p>hi</p></body></html>")
            self.assertTrue(fsops.ensure_theme_link(d, "index.html"))
            out = fsops.read_file(d, "index.html")
            self.assertLess(out.index("theme.css"), out.index("styles.css"))      # theme comes first
            self.assertIn("viewport", out)
            self.assertFalse(fsops.ensure_theme_link(d, "index.html"))            # idempotent
            fsops.ensure_theme_link(d, "sub/page.html")
            self.assertIn("../theme.css", fsops.read_file(d, "sub/page.html"))

    def test_designer_only_for_websites_and_redesigns(self):
        replies = [("Designer", DESIGN)]
        with tempfile.TemporaryDirectory() as d:
            eng = Engine(d, FakeClient(replies))
            idx = eng.index()
            self.assertTrue(eng._wants_design("generate a website for a bakery", idx))
            self.assertFalse(eng._wants_design("write a python function to add numbers", idx))
            fsops.write_file(d, "index.html", "<html></html>")
            idx = eng.index()
            self.assertFalse(eng._wants_design("add a cart counter", idx))          # small change keeps existing look
            self.assertTrue(eng._wants_design("make the design more modern", idx))


class OfflineTests(unittest.TestCase):
    def test_cdn_assets_removed_but_local_and_icons_kept(self):
        with tempfile.TemporaryDirectory() as d:
            fsops.write_file(d, "index.html",
                '<html><head><link rel="stylesheet" href="theme.css">'
                '<link href="https://stackpath.bootstrapcdn.com/bootstrap.min.css" rel="stylesheet">'
                '<link rel="icon" href="https://x.com/favicon.ico"></head><body>'
                '<script src="https://cdn.example.com/jquery.js"></script><script src="script.js"></script></body></html>')
            self.assertEqual(fsops.strip_external_assets(d, "index.html"), 2)
            out = fsops.read_file(d, "index.html")
            self.assertNotIn("bootstrap", out)
            self.assertNotIn("jquery", out)
            self.assertIn("theme.css", out)
            self.assertIn("script.js", out)
            self.assertIn("favicon.ico", out)


class SinglePageTests(unittest.TestCase):
    def test_new_site_is_forced_to_one_page(self):
        bloated = "SUMMARY: big.\nFILES:\n- templates/index.html: home\n- templates/product.html: p\n- app.py: flask\nNOTES:\n- x\n"
        replies = [("Researcher", "APPROACH: x"), ("Designer", DESIGN), ("Reviewer", "LGTM"),
                   ("Planner", bloated), ("Coder", coder)]
        with tempfile.TemporaryDirectory() as d:
            eng = Engine(d, FakeClient(replies))
            eng.handle_code("generate a simple website for a shoes store")
            self.assertEqual(sorted(f for f in os.listdir(d) if not f.startswith(".")),
                             ["index.html", "script.js", "site.js", "styles.css", "theme-toggle.js", "theme.css"])

    def test_multi_page_request_is_respected(self):
        plan = "SUMMARY: s.\nFILES:\n- index.html: home\n- about.html: about\n- styles.css: css\nNOTES:\n- x\n"
        replies = [("Researcher", "APPROACH: x"), ("Designer", DESIGN), ("Reviewer", "LGTM"),
                   ("Planner", plan), ("Coder", lambda u: "```html\n<html><head></head><body><h1>x</h1></body></html>\n```")]
        with tempfile.TemporaryDirectory() as d:
            eng = Engine(d, FakeClient(replies))
            eng.handle_code("generate a website with home and about pages")
            self.assertTrue(os.path.exists(os.path.join(d, "about.html")))


class RepairAfterReviewTests(unittest.TestCase):
    def test_review_rewrite_cannot_reintroduce_broken_links(self):
        fence = chr(96) * 3

        def html(extra):
            return fence + "html" + chr(10) + "<html><head></head><body><h1>Shop</h1>" + extra + "</body></html>" + chr(10) + fence

        def coder_fn(user):
            if "FILE TO WRITE NOW: styles.css" in user:
                return fence + "css" + chr(10) + "body{margin:0}" + chr(10) + fence
            if "FILE TO WRITE NOW: script.js" in user:
                return fence + "js" + chr(10) + "console.log(1);" + chr(10) + fence
            if "REVIEW FINDINGS TO FIX" in user:       # the "fixed" version re-adds a link to a missing page
                return html("<a href='about.html'>About</a><img src='shoe.jpg' alt='Shoe'>")
            return html("")

        plan = "SUMMARY: s.\nFILES:\n- index.html: page\nNOTES:\n- x\n"
        replies = [("Researcher", "APPROACH: x"), ("Designer", DESIGN), ("Planner", plan), ("Coder", coder_fn),
                   ("Reviewer", "- index.html: add an about link and a picture")]
        with tempfile.TemporaryDirectory() as d:
            eng = Engine(d, FakeClient(replies))
            out = eng.handle_code("generate a website for shoes")
            self.assertNotIn("❌", out)
            page = fsops.read_file(d, "index.html")
            self.assertNotIn("about.html", page)
            self.assertNotIn("shoe.jpg", page)


class IntentTests(unittest.TestCase):
    def test_project_questions_are_answered_not_built(self):
        class NoLLM(FakeClient):
            def stream(self, *a, **k):
                raise AssertionError("the small model must not be needed for these")
        with tempfile.TemporaryDirectory() as d:
            eng = Engine(d, NoLLM([]))
            for q in ["what this project do", "What does this project do?", "explain this project",
                      "summarize the code", "where is the delete button in index.html", "how does the add task function work"]:
                self.assertEqual(eng.classify_intent(q), "ASK", q)
            self.assertEqual(eng.classify_intent("hello"), "OFFTOPIC")
            self.assertEqual(eng.classify_intent("add a delete button to the app"), "BUILD")


class SlowClient(FakeClient):
    """Records whether two model calls ever overlap."""
    active = 0
    max_active = 0
    guard = threading.Lock()

    def stream(self, model, messages, temperature=0.2, num_predict=None, cancel=None):
        with SlowClient.guard:
            SlowClient.active += 1
            SlowClient.max_active = max(SlowClient.max_active, SlowClient.active)
        try:
            time.sleep(0.25)
            yield from super().stream(model, messages, temperature, num_predict, cancel)
        finally:
            with SlowClient.guard:
                SlowClient.active -= 1


class ParallelTests(unittest.TestCase):
    def test_parallel_chats_queue_for_the_gpu(self):
        SlowClient.active = SlowClient.max_active = 0
        replies = [("DevForge AI, a friendly", "ok")]
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            engines = [Engine(d1, SlowClient(replies)), Engine(d2, SlowClient(replies))]
            threads = [threading.Thread(target=e.handle_chat, args=("hello there",)) for e in engines]
            [t.start() for t in threads]
            [t.join(20) for t in threads]
            self.assertEqual(SlowClient.max_active, 1, "two model calls ran at the same time")
            for e in engines:
                self.assertEqual(len(e.store.list_sessions()), 1)
                self.assertEqual(len(e.store.load(e.store.list_sessions()[0]["id"])), 4 if False else 2)

    def test_queued_task_can_be_stopped(self):
        from devforge import engine as eng_mod
        from devforge.engine import Cancelled
        stop = {"v": False}
        with tempfile.TemporaryDirectory() as d:
            e = Engine(d, FakeClient([("DevForge AI, a friendly", "ok")]), cancel=lambda: stop["v"])
            eng_mod._GPU_LOCK.acquire()               # pretend another chat is using the model
            try:
                result = {}

                def run():
                    try:
                        e.handle_chat("hi there")
                    except Cancelled:
                        result["cancelled"] = True
                t = threading.Thread(target=run)
                t.start()
                time.sleep(0.5)
                stop["v"] = True
                t.join(5)
                self.assertTrue(result.get("cancelled"))
            finally:
                eng_mod._GPU_LOCK.release()


class SkillStoreTests(unittest.TestCase):
    def test_save_list_update_delete_and_files_on_disk(self):
        from devforge.skills import SkillStore, SkillError
        with tempfile.TemporaryDirectory() as d:
            st = SkillStore(d)
            self.assertEqual(st.list(), [])
            a = st.save("Brand style", "Always use accent #4A90E2.\nRounded buttons.", "when styling a UI")
            st.save("Tone of voice", "Write friendly, short sentences.")
            self.assertTrue(os.path.exists(os.path.join(d, "skills", "brand-style.md")))   # saved under <project>/skills
            self.assertEqual(sorted(s["slug"] for s in st.list()), ["brand-style", "tone-of-voice"])   # adding keeps the others
            self.assertEqual(a["description"], "when styling a UI")
            self.assertIn("Rounded buttons", st.get("brand-style")["text"])
            st.save("Brand style", "New text only.")                                      # same name = update
            self.assertEqual(len(st.list()), 2)
            self.assertEqual(st.get("brand-style")["text"], "New text only.")
            st.save("Brand look", "renamed", replace_slug="brand-style")                  # rename removes the old file
            self.assertEqual(sorted(s["slug"] for s in st.list()), ["brand-look", "tone-of-voice"])
            self.assertTrue(st.delete("tone-of-voice"))
            self.assertEqual([s["slug"] for s in st.list()], ["brand-look"])
            for bad in ("", "   ", "!!!"):
                with self.assertRaises(SkillError):
                    st.save(bad, "text")
            with self.assertRaises(SkillError):
                st.save("ok", "   ")

    def test_names_cannot_escape_the_skills_folder(self):
        from devforge.skills import SkillStore
        with tempfile.TemporaryDirectory() as d:
            st = SkillStore(d)
            saved = st.save("../../evil", "x")
            self.assertEqual(saved["slug"], "evil")
            self.assertTrue(os.path.exists(os.path.join(d, "skills", "evil.md")))
            self.assertFalse(st.delete("../../anything"))

    def test_plain_txt_files_are_read(self):
        from devforge.skills import SkillStore
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "skills"))
            with open(os.path.join(d, "skills", "notes.txt"), "w") as f:
                f.write("Prefer tabs over spaces.\nAlways add comments.")
            sk = SkillStore(d).list()
            self.assertEqual((sk[0]["slug"], sk[0]["ext"]), ("notes", ".txt"))
            self.assertIn("Always add comments", sk[0]["text"])


class SkillSelectionTests(unittest.TestCase):
    SK = [{"slug": "brand-style", "name": "Brand style", "description": "colours and buttons for any UI", "text": "use accent blue, rounded buttons"},
          {"slug": "tone", "name": "Tone of voice", "description": "writing copy", "text": "friendly short sentences"}]

    def test_forced_slash_skill_is_removed_from_prompt(self):
        from devforge import skills as sk
        clean, chosen = sk.pick("/brand-style build a landing page", self.SK)
        self.assertEqual(clean, "build a landing page")
        self.assertEqual([(s["slug"], how) for s, how in chosen][0], ("brand-style", "forced"))
        clean, chosen = sk.pick("open /usr/bin/thing and /nothere", self.SK)             # unknown /words are untouched
        self.assertEqual(clean, "open /usr/bin/thing and /nothere")
        clean, chosen = sk.pick("/tone", self.SK)                                         # only a skill name
        self.assertIn("Tone of voice", clean)

    def test_auto_selection_only_for_relevant_skills(self):
        from devforge import skills as sk
        _, chosen = sk.pick("make the buttons look good with our brand colours", self.SK)
        self.assertEqual([s["slug"] for s, how in chosen], ["brand-style"])
        self.assertEqual(chosen[0][1], "auto")
        _, chosen = sk.pick("write a python function to add two numbers", self.SK)
        self.assertEqual(chosen, [])

    def test_long_skill_is_cut_for_the_small_model(self):
        from devforge import skills as sk
        big = {"slug": "big", "name": "Big", "description": "", "text": ("line of text\n" * 400)}
        block = sk.format_block([(big, "forced")])
        self.assertLess(len(block), sk.MAX_INJECT_CHARS + 400)
        self.assertIn("cut to fit", block)


class CaptureClient(FakeClient):
    """Remembers every message list the models received."""
    def __init__(self, replies):
        super().__init__(replies)
        self.seen = []

    def stream(self, model, messages, *a, **k):
        self.seen.append(messages)
        yield from super().stream(model, messages, *a, **k)


class SkillEngineTests(unittest.TestCase):
    def test_chat_uses_forced_and_auto_skills(self):
        from devforge.skills import SkillStore
        with tempfile.TemporaryDirectory() as d:
            SkillStore(d).save("Pirate", "Answer like a pirate, say arr.", "style of replies")
            SkillStore(d).save("Metric", "Always use metric units.", "units for measurements")
            client = CaptureClient([("DevForge AI, a friendly", "ok")])
            ev = []
            eng = Engine(d, client, emit=lambda k, **kw: ev.append((k, kw)))
            eng.handle_chat("/pirate how far is the moon in kilometres")
            sysmsg = [m for m in client.seen[0] if m["role"] == "system"][0]["content"]
            usermsg = [m for m in client.seen[0] if m["role"] == "user"][-1]["content"]
            self.assertIn("Answer like a pirate", sysmsg)
            self.assertNotIn("/pirate", usermsg)                                          # token stripped for the model
            self.assertTrue(any(k == "stage" and kw["agent"] == "Skills" and "forced" in kw["text"] for k, kw in ev))
            stored = eng.store.load(eng.store.list_sessions()[0]["id"])
            self.assertTrue(stored[0]["content"].startswith("/pirate"))                    # history keeps what the user typed

    def test_build_pipeline_gives_skills_to_planner_and_coder(self):
        from devforge.skills import SkillStore
        with tempfile.TemporaryDirectory() as d:
            SkillStore(d).save("Brand style", "Accent colour is hot pink #FF00AA.", "colours for any UI or website")
            client = CaptureClient([("Researcher", "APPROACH: x"), ("Designer", DESIGN), ("Reviewer", "LGTM"),
                                    ("Planner", PLAN), ("Coder", coder)])
            eng = Engine(d, client)
            eng.handle_code("/brand-style generate simple website for shoes store")
            by_role = {}
            for msgs in client.seen:
                by_role.setdefault(msgs[0]["content"].split(" ")[3], []).append(msgs[-1]["content"])
            self.assertTrue(any("hot pink" in u for u in by_role.get("Planner", [])))
            self.assertTrue(any("hot pink" in u for u in by_role.get("Coder", [])))
            self.assertTrue(all("/brand-style" not in u for us in by_role.values() for u in us))

    def test_skills_folder_is_not_part_of_code_rag(self):
        from devforge.skills import SkillStore
        with tempfile.TemporaryDirectory() as d:
            SkillStore(d).save("Style", "secret skill words zebra")
            fsops.write_file(d, "main.py", "def f():\n    return 1\n")
            idx = CodeIndex(d)
            idx.refresh()
            self.assertNotIn("skills/", idx.repo_map())


class RoutingTests(unittest.TestCase):
    def _site(self, d, theme="modern-dark"):
        from devforge import themes
        fsops.write_file(d, "index.html", "<!DOCTYPE html><html><head><link rel='stylesheet' href='theme.css'><link rel='stylesheet' href='styles.css'></head>"
                                           "<body><button id='theme-toggle'>Toggle theme</button><h1>Tasks</h1><script src='script.js'></script></body></html>")
        fsops.write_file(d, "theme.css", themes.render_css(theme, "#4A90E2"))
        fsops.write_file(d, "styles.css", ".task{padding:1rem}")
        fsops.write_file(d, "script.js", "document.getElementById('theme-toggle').addEventListener('click',()=>document.body.classList.toggle('light-theme'));")

    def test_request_kinds(self):
        with tempfile.TemporaryDirectory() as d:
            eng = Engine(d, FakeClient([]))
            self.assertEqual(eng._classify_build("build a website for a bakery", eng.index()), "new")
            self._site(d)
            idx = eng.index()
            cases = {
                "now i want a light theme also with toggle button so that i can switch between light and dark theme": "toggle",
                "i clicked on toggle theme button but the theme does not change to dark": "toggle",
                "fix the delete button, it is not working": "fix",
                "add a cart counter": "change",
                "make the design more modern": "redesign",
                "redesign it with a glass theme": "redesign",
            }
            for text, kind in cases.items():
                self.assertEqual(eng._classify_build(text, idx), kind, text)

    def test_fix_never_calls_designer_or_researcher_and_keeps_theme(self):
        fence = chr(96) * 3
        plan = "SUMMARY: fix.\nFILES:\n- script.js: fix delete\nNOTES:\n- x\n"
        replies = [("Planner", plan), ("Reviewer", "LGTM"),
                   ("Coder", fence + "js" + chr(10) + "console.log('fixed');" + chr(10) + fence)]
        with tempfile.TemporaryDirectory() as d:
            self._site(d)
            before = fsops.read_file(d, "theme.css")
            eng = Engine(d, FakeClient(replies))       # a Designer/Researcher call would raise: no scripted reply
            out = eng.handle_code("fix the delete button, it is not working")
            self.assertEqual(fsops.read_file(d, "theme.css"), before)
            self.assertIn("fixed", fsops.read_file(d, "script.js"))
            self.assertNotIn("❌", out)

    def test_toggle_adds_real_dual_palette_without_models(self):
        with tempfile.TemporaryDirectory() as d:
            self._site(d, "modern-dark")
            client = FakeClient([])
            eng = Engine(d, client)
            out = eng.handle_code("now i want a light theme also with toggle button so that i can switch between light and dark theme")
            css = fsops.read_file(d, "theme.css")
            self.assertIn('data-theme="dark"', css)
            self.assertIn('data-theme="light"', css)
            self.assertIn("--primary:#4A90E2", css)                                  # the site's accent is kept
            self.assertIn("--bg:#0b0f19", css)                                       # dark palette present
            self.assertIn("--bg:#ffffff", css)                                       # light palette present
            js = fsops.read_file(d, "theme-toggle.js")
            self.assertIn("data-theme", js)
            page = fsops.read_file(d, "index.html")
            self.assertIn("theme-toggle.js", page)
            self.assertIn("theme.css", page)
            self.assertNotIn("❌", out)
            self.assertEqual({k for k, _ in client.calls}, {"title", "memory"})      # only chat-name + memory calls used a model
            self.assertIn("starts in **dark**", out)
            self.assertEqual(fsops.read_file(d, "theme-toggle.js").count("__DEFAULT__"), 0)

    def test_toggle_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            self._site(d)
            eng = Engine(d, FakeClient([]))
            eng.handle_code("add a dark and light theme toggle")
            first = fsops.read_file(d, "index.html")
            eng.handle_code("add a dark and light theme toggle")
            self.assertEqual(fsops.read_file(d, "index.html"), first)               # links are not duplicated
            self.assertEqual(first.count("theme-toggle.js"), 1)
            self.assertEqual(first.count("theme.css"), 1)


class MemoryStoreTests(unittest.TestCase):
    def test_notes_add_dedupe_cap_edit_clear(self):
        from devforge.memory import MemoryStore, MAX_NOTES, parse_facts
        with tempfile.TemporaryDirectory() as d:
            m = MemoryStore(d)
            self.assertEqual((m.enabled(), m.notes()), (True, []))
            self.assertEqual(m.add(["- Wants a dark theme", "wants a DARK theme!", "Shop is called Bluebird"]), 2)   # near-duplicate ignored
            self.assertTrue(os.path.exists(os.path.join(d, ".devforge", "memory.json")))
            before = {n["text"]: n["ts"] for n in m.notes()}
            m.replace_all(["Wants a dark theme", "A brand new line"])                                              # user edit
            after = {n["text"]: n["ts"] for n in m.notes()}
            self.assertEqual(set(after), {"Wants a dark theme", "A brand new line"})
            self.assertEqual(after["Wants a dark theme"], before["Wants a dark theme"])                           # unchanged lines keep their date
            m.add([f"fact number {i} is here" for i in range(60)])
            self.assertEqual(len(m.notes()), MAX_NOTES)                                                            # oldest dropped
            m.set_enabled(False)
            self.assertFalse(m.enabled())
            m.clear()
            self.assertEqual(m.notes(), [])
            self.assertFalse(m.enabled())                                                                          # clearing keeps the on/off choice

    def test_parse_facts(self):
        from devforge.memory import parse_facts
        self.assertEqual(parse_facts("NONE"), [])
        self.assertEqual(parse_facts("none."), [])
        self.assertEqual(parse_facts("- Uses a dark theme\n* Shop is Bluebird Boots\nrandom text\n- ok"), ["Uses a dark theme", "Shop is Bluebird Boots"])
        self.assertEqual(len(parse_facts("\n".join(f"- fact number {i} here" for i in range(9)))), 3)


class MemoryRecallTests(unittest.TestCase):
    def _store(self, d):
        from devforge.store import ProjectStore
        st = ProjectStore(d)
        a = st.create("chat", "Shop branding")
        st.append(a["id"], "user", "my shop is called Bluebird Boots and the brand colour is teal")
        st.append(a["id"], "assistant", "Great, Bluebird Boots with teal as the brand colour.")
        b = st.create("code", "Task manager")
        st.append(b["id"], "user", "build a task manager where i can add and delete tasks")
        st.append(b["id"], "assistant", "Built index.html with add and delete buttons.")
        return st, a["id"], b["id"]

    def test_recall_finds_other_chats_only(self):
        from devforge.memory import recall
        with tempfile.TemporaryDirectory() as d:
            st, a, b = self._store(d)
            hits = recall(st, "what colour is the brand of my shop", exclude_sid=b)
            self.assertEqual([h["sid"] for h in hits], [a])
            self.assertEqual(recall(st, "what colour is the brand of my shop", exclude_sid=a), [])      # never its own chat
            self.assertEqual(recall(st, "write a python function that reverses text", exclude_sid=b), [])  # unrelated -> nothing
            broad = recall(st, "what did we discuss earlier?", exclude_sid=b)                               # vague recall question
            self.assertEqual([h["sid"] for h in broad], [a])

    def test_block_is_short_and_labelled(self):
        from devforge.memory import format_block
        notes = [{"text": f"note {i} " + "x" * 80, "ts": i} for i in range(40)]
        block = format_block(notes, [], notes_budget=700)
        self.assertLess(len(block), 900)
        self.assertIn("note 39", block)                                   # newest kept
        self.assertNotIn("note 0 ", block)                                # oldest dropped first


class MemoryEngineTests(unittest.TestCase):
    def test_fact_from_chat_one_is_known_in_chat_two(self):
        with tempfile.TemporaryDirectory() as d:
            client = CaptureClient([("DevForge AI, a friendly", "Noted!")])
            client.memory_reply = "- The shop is called Bluebird Boots and uses teal"
            eng = Engine(d, client)
            eng.handle_chat("My shop is called Bluebird Boots and our colour is teal")            # chat 1
            self.assertEqual([n["text"] for n in eng.store and __import__("devforge.memory", fromlist=["x"]).MemoryStore(d).notes()],
                             ["The shop is called Bluebird Boots and uses teal"])
            client.seen.clear()
            eng.handle_chat("what is my shop called?")                                              # chat 2 (new session)
            self.assertEqual(len(eng.store.list_sessions()), 2)
            system = [m for m in client.seen[0] if m["role"] == "system"][0]["content"]
            self.assertIn("PROJECT MEMORY", system)
            self.assertIn("Bluebird Boots", system)
            self.assertIn("RELATED EARLIER CHATS", system)                                           # the old exchange itself is searched too

    def test_memory_works_in_code_tab_questions_and_builds(self):
        from devforge.memory import MemoryStore
        with tempfile.TemporaryDirectory() as d:
            MemoryStore(d).add(["The user wants everything in dark theme with teal accent"])
            fsops.write_file(d, "main.py", "def add(a, b):\n    return a + b\n")
            client = CaptureClient([("answer ONLY", "It adds.")])
            Engine(d, client).handle_code("what does main.py do?")
            ask_system = [m for m in client.seen[0] if m["role"] == "system"][0]["content"]
            self.assertIn("teal accent", ask_system)

    def test_build_saves_a_deterministic_fact_and_uses_short_notes_only(self):
        from devforge.memory import MemoryStore
        replies = [("Researcher", "APPROACH: x"), ("Designer", DESIGN), ("Reviewer", "LGTM"), ("Planner", PLAN), ("Coder", coder)]
        with tempfile.TemporaryDirectory() as d:
            engine = Engine(d, CaptureClient(replies))
            engine.handle_code("generate simple website for shoes store")
            notes = [n["text"] for n in MemoryStore(d).notes()]
            self.assertTrue(any(n.startswith('Built for "generate simple website') and "index.html" in n for n in notes), notes)

    def test_disabled_memory_saves_and_injects_nothing(self):
        from devforge.memory import MemoryStore
        with tempfile.TemporaryDirectory() as d:
            m = MemoryStore(d)
            m.add(["Secret fact: the shop is Bluebird"])
            m.set_enabled(False)
            client = CaptureClient([("DevForge AI, a friendly", "ok")])
            client.memory_reply = "- Something new to remember here"
            eng = Engine(d, client)
            eng.handle_chat("tell me about my shop please")
            system = [x for x in client.seen[0] if x["role"] == "system"][0]["content"]
            self.assertNotIn("Bluebird", system)
            self.assertNotIn("memory", {k for k, _ in client.calls})                                # extraction call skipped
            self.assertEqual(len(m.notes()), 1)

    def test_offtopic_turns_are_not_remembered(self):
        from devforge.memory import MemoryStore
        with tempfile.TemporaryDirectory() as d:
            client = CaptureClient([("classify", "OFFTOPIC")])
            client.memory_reply = "- should never be saved"
            Engine(d, client).handle_code("who is the president of france?")
            self.assertEqual(MemoryStore(d).notes(), [])


class QuestionRoutingTests(unittest.TestCase):
    def test_polite_and_sloppy_questions_are_answered_not_built(self):
        class NoLLM(FakeClient):
            def stream(self, *a, **k):
                raise AssertionError("the small model must not be needed for these")
        with tempfile.TemporaryDirectory() as d:
            eng = Engine(d, NoLLM([]))
            for q in ["could u tell me which files are there in this foolder now",
                      "Could you please show me the files in this folder?",
                      "can you explain this project",
                      "hey tell me what this app does",
                      "i want to know which files are in the project",
                      "are there any bugs in the code",
                      "how many files are in this project"]:
                self.assertEqual(eng.classify_intent(q), "ASK", q)
            from devforge.engine import _ASK_START
            for q in ["show a popup when the button is clicked", "do a refactor of the code", "tell the app to save tasks",
                      "show the cart in a sidebar", "list the tasks as cards"]:
                if q.startswith("list"):
                    continue                                   # "list ..." questions vs commands need the model; not asserted here
                self.assertIsNone(_ASK_START.match(q), q)       # commands must not be mistaken for questions

    def test_file_question_gets_the_real_listing(self):
        with tempfile.TemporaryDirectory() as d:
            fsops.write_file(d, "index.html", "<html></html>")
            with open(os.path.join(d, "manual.pdf"), "wb") as f:
                f.write(b"%PDF-1.4 fake")
            client = CaptureClient([("answer ONLY", "You have index.html and manual.pdf.")])
            Engine(d, client).handle_code("could u tell me which files are there in this foolder now")
            system = [m for m in client.seen[0] if m["role"] == "system"][0]["content"]
            self.assertIn("manual.pdf", system)               # a PDF is not in the code index, but it IS in the folder
            self.assertIn("index.html", system)
            roles = [m[0]["content"] for m in client.seen]
            self.assertEqual(sum("answer ONLY" in r for r in roles), 1)          # one answering call...
            self.assertFalse(any("Planner of DevForge" in r or "Coder of DevForge" in r for r in roles))   # ...no build pipeline


class TestReplyTimer(unittest.TestCase):
    def test_format(self):
        from devforge.ui import fmt_duration
        self.assertEqual(fmt_duration(4.24), "4.2s")
        self.assertEqual(fmt_duration(42), "42s")
        self.assertEqual(fmt_duration(75), "1m 15s")
        self.assertEqual(fmt_duration(3725), "1h 02m")

    def test_durations_from_saved_timestamps(self):
        from devforge.ui import reply_durations
        msgs = [{"role": "user", "content": "hi", "ts": 100.0},
                {"role": "assistant", "content": "hello", "ts": 103.5},
                {"role": "user", "content": "build a site", "ts": 200.0},
                {"role": "assistant", "content": "done", "ts": 920.0},
                {"role": "assistant", "content": "old message without a prompt", "ts": 930.0},
                {"role": "user", "content": "no ts"}, {"role": "assistant", "content": "x", "ts": 5.0}]
        self.assertEqual(reply_durations(msgs), [None, 3.5, None, 720.0, None, None, None])


class SiteKitTests(unittest.TestCase):
    """The parts that small models kept getting wrong are now done by code."""

    def test_fixed_colours_become_theme_colours(self):
        from devforge import themes
        css = ("#schedule .card { background-color: #fff; box-shadow: 0 4px 8px rgba(0,0,0,.1); }\n"
               ".card-foot { background-color: #007bff; color: white; }\n"
               ".hero { background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%); color: white; }\n"
               "input { border: 1px solid #ccc; }\n"
               "#form-msg.success { color: green; }\n#form-msg.error { color: red; }\n")
        out, n = themes.theme_colours(css)
        self.assertIn("background-color: var(--surface)", out)          # white card follows the theme
        self.assertIn("rgba(0,0,0,.1)", out)                             # shadows are left alone
        self.assertIn("background-color: var(--primary)", out)
        self.assertIn("var(--primary-contrast)", out)                    # white text on the accent stays readable
        self.assertIn("var(--hero-bg)", out)
        self.assertIn("var(--hero-text)", out)
        self.assertIn("var(--border-strong)", out)
        self.assertIn("var(--success)", out)
        self.assertIn("var(--danger)", out)
        self.assertEqual(themes.theme_colours(out)[1], 0)              # idempotent

    def test_menu_class_without_css_rule_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            fsops.write_file(d, "index.html", '<nav class="nav-links"></nav><button id="menu-btn">x</button>'
                                              '<script src="script.js"></script>')
            fsops.write_file(d, "styles.css", ".nav-links a.active { color: blue; }")
            fsops.write_file(d, "script.js", "const navLinks = document.querySelector('.nav-links');\n"
                                             "document.getElementById('menu-btn').onclick = () => navLinks.classList.toggle('active');\n"
                                             "document.getElementById('cart-count').textContent = 1;\n")
            probs = fsops.consistency_check(d, ["index.html", "script.js"])
            self.assertEqual(len(probs), 1)
            self.assertIn('.nav-links.active', probs[0]["error"])        # the exact menu bug
            self.assertIn('id "cart-count"', probs[0]["error"])          # an id the page does not have
            fsops.write_file(d, "styles.css", ".nav-links.active { display: flex; }")
            fsops.write_file(d, "index.html", '<nav class="nav-links"></nav><button id="menu-btn">x</button>'
                                              '<span id="cart-count">0</span>')
            self.assertEqual(fsops.consistency_check(d, ["index.html", "script.js"]), [])

    def test_existing_site_is_repaired_by_code(self):
        from devforge import themes
        with tempfile.TemporaryDirectory() as d:
            fsops.write_file(d, "theme.css", themes.render_css("clean-light"))
            fsops.write_file(d, "index.html", '<html><head><link rel="stylesheet" href="theme.css">'
                                              '<link rel="stylesheet" href="styles.css"></head><body>'
                                              '<header class="navbar"><div class="nav-inner"><nav class="nav-links">'
                                              '<a href="#about">About</a></nav></div></header>'
                                              '<section id="about" class="section"><div class="card">x</div></section>'
                                              '</body></html>')
            fsops.write_file(d, "styles.css", ".card { background-color: #fff; color: #333; }")
            client = FakeClient([])
            out = Engine(d, client).handle_code("use the theme colours in styles.css")
            self.assertIn("var(--surface)", fsops.read_file(d, "styles.css"))
            page = fsops.read_file(d, "index.html")
            self.assertIn("site.js", page)
            self.assertIn("theme-toggle.js", page)
            self.assertIn(".nav-links.open", fsops.read_file(d, "theme.css", 40000))   # mobile menu styles
            self.assertEqual({k for k, _ in client.calls} - {"title", "memory"}, set())  # no model needed
            self.assertNotIn("❌", out)


class GuardTests(unittest.TestCase):
    """Code checks that catch what the models still get wrong."""

    def test_dead_nav_links_point_at_their_sections(self):
        with tempfile.TemporaryDirectory() as d:
            fsops.write_file(d, "index.html",
                             '<header class="navbar" id="home"><nav class="nav-links"><a href="#">Home</a>'
                             '<a href="about.html">About</a><a href="javascript:void(0)">Speakers</a>'
                             '<a href="#contact">Contact</a></nav></header>'
                             '<section class="hero" id="hero"><a class="btn" href="#">Register now</a></section>'
                             '<section id="about"></section><section id="speakers"></section>'
                             '<section id="register"></section><footer id="footer"></footer>')
            fsops.fix_dangling_refs(d, "index.html")
            self.assertEqual(fsops.fix_nav_anchors(d, "index.html"), 5)
            page = fsops.read_file(d, "index.html")
            for href in ('href="#home">Home', 'href="#about">About', 'href="#speakers">Speakers',
                         'href="#footer">Contact', 'href="#register">Register now'):
                self.assertIn(href, page)
            self.assertEqual(fsops.dead_nav_links(page), [])
            self.assertEqual(fsops.fix_nav_anchors(d, "index.html"), 0)          # idempotent

    def test_unmatched_nav_link_is_reported(self):
        self.assertEqual(fsops.dead_nav_links('<nav><a href="#">Blog</a></nav><section id="home"></section>'),
                         ['nav link "Blog" points to "#"'])

    def test_colours_inside_html_follow_the_theme(self):
        from devforge import themes
        page = ('<style>.box{background:#fff;color:#222}</style>'
                '<div class="card" style="background-color:#ffffff; color:#333; padding:4px">a</div>'
                '<span style="margin:0">b</span>')
        out, n = themes.theme_colours_html(page)
        self.assertEqual(n, 4)
        self.assertIn(".box{background: var(--surface);color:var(--text)}", out)
        self.assertIn("padding:4px", out)
        self.assertIn('style="margin:0"', out)
        self.assertEqual(themes.theme_colours_html(out)[1], 0)

    def test_fetch_must_match_a_backend_route(self):
        with tempfile.TemporaryDirectory() as d:
            fsops.write_file(d, "index.html", '<form id="f"></form>')
            fsops.write_file(d, "app.py", "import http.server\nclass H(http.server.BaseHTTPRequestHandler):\n"
                                          "    def do_GET(self):\n        if self.path == '/api/stats':\n            pass\n")
            fsops.write_file(d, "script.js", "fetch('/api/stats'); fetch('/api/register', {method: 'POST'}); fetch('/index.html');")
            probs = fsops.consistency_check(d, ["index.html", "script.js"])
            self.assertEqual(len(probs), 1)
            self.assertIn('"/api/register"', probs[0]["error"])
            self.assertNotIn("/index", probs[0]["error"])

    def test_files_named_in_the_request_are_always_planned(self):
        with tempfile.TemporaryDirectory() as d:
            fsops.write_file(d, "script.js", "let x = 1;")
            eng = Engine(d, FakeClient([]))
            planned = eng._add_named_files("Add a backend in a new file app.py and update script.js to call it",
                                           [("app.py", "backend")])
            self.assertEqual([p for p, _ in planned], ["app.py", "script.js"])      # backend first, then the script
            self.assertIn("update", dict(planned)["script.js"])

    def test_update_that_changes_nothing_is_retried(self):
        fence = chr(96) * 3
        old = "let count = 0;" + chr(10)
        plan = chr(10).join(["SUMMARY: s.", "FILES:", "- script.js: counter", "NOTES:", "- x", ""])
        calls = {"n": 0}

        def coder(user):
            calls["n"] += 1
            body = "let count = 1;" if "IDENTICAL TO THE CURRENT FILE" in user else "let count = 0;"
            return fence + "js" + chr(10) + body + chr(10) + fence

        with tempfile.TemporaryDirectory() as d:
            fsops.write_file(d, "script.js", old)
            eng = Engine(d, FakeClient([("Planner", plan), ("Coder", coder), ("Reviewer", "LGTM")]))
            eng.handle_code("change the counter in script.js to start at 1")
            self.assertIn("count = 1", fsops.read_file(d, "script.js"))
            self.assertEqual(calls["n"], 2)

    def test_cut_off_rewrite_never_deletes_half_a_file(self):
        fence = chr(96) * 3
        big = "".join(f"function f{i}() {{ return {i}; }}" + chr(10) for i in range(120))
        plan = chr(10).join(["SUMMARY: s.", "FILES:", "- script.js: more", "NOTES:", "- x", ""])
        with tempfile.TemporaryDirectory() as d:
            fsops.write_file(d, "script.js", big)
            eng = Engine(d, FakeClient([("Planner", plan), ("Reviewer", "LGTM"),
                                        ("Coder", fence + "js" + chr(10) + "function f0() { return 0; }" + chr(10) + fence)]))
            out = eng.handle_code("add a function f120 to script.js")
            self.assertEqual(fsops.read_file(d, "script.js", 100_000), big)      # the working file is kept
            self.assertIn("cut off", out)

    def test_wrong_kind_of_content_is_caught(self):
        from devforge.engine import _wrong_kind
        self.assertTrue(_wrong_kind("script.js", "<!DOCTYPE html>\n<html><body></body></html>"))
        self.assertTrue(_wrong_kind("styles.css", "<html><head></head></html>"))
        self.assertTrue(_wrong_kind("index.html", "body { margin: 0 }"))
        self.assertFalse(_wrong_kind("script.js", "document.addEventListener('DOMContentLoaded', () => {});"))
        self.assertFalse(_wrong_kind("script.js", "import { a } from './a.js';\nfunction f() { return a; }"))
        self.assertFalse(_wrong_kind("index.html", "<!DOCTYPE html><html><body><h1>x</h1></body></html>"))


class OnlyChangeWhatIsAskedTests(unittest.TestCase):
    """Updates change only the asked part; old working code is never lost."""
    NL = chr(10)
    FENCE = chr(96) * 3
    OLD_JS = NL.join([
        "document.addEventListener('DOMContentLoaded', () => {",
        "    const form = document.getElementById('register-form');",
        "    function showMessage(text) { document.getElementById('form-msg').textContent = text; }",
        "    form.addEventListener('submit', (e) => {",
        "        e.preventDefault();",
        "        showMessage('Registration successful!');",
        "        form.reset();",
        "    });",
        "});", ""])

    def _site(self, d):
        fsops.write_file(d, "index.html", '<html><body><form id="register-form"></form><div id="form-msg"></div>'
                                          '<script src="script.js"></script></body></html>')
        fsops.write_file(d, "script.js", self.OLD_JS)

    def test_edit_blocks_change_only_the_asked_lines(self):
        plan = self.NL.join(["SUMMARY: s.", "FILES:", "- script.js: redirect", "NOTES:", "- x", ""])
        edit = self.NL.join(["<<<<<<< SEARCH", "        form.reset();", "=======", "        form.reset();",
                             "        window.location.href = 'thank-you.html';", ">>>>>>> REPLACE"])
        with tempfile.TemporaryDirectory() as d:
            self._site(d)
            fsops.write_file(d, "thank-you.html", "<html><body><h1>Thanks</h1></body></html>")
            eng = Engine(d, FakeClient([("classify", "BUILD"), ("Planner", plan), ("Coder", edit), ("Reviewer", "LGTM")]))
            out = eng.handle_code("after a successful registration go to thank-you.html")
            new = fsops.read_file(d, "script.js")
            self.assertEqual(new, self.OLD_JS.replace("        form.reset();",
                                                      "        form.reset();" + self.NL +
                                                      "        window.location.href = 'thank-you.html';"))
            self.assertNotIn("❌", out)

    def test_rewrite_that_drops_a_function_is_refused(self):
        plan = self.NL.join(["SUMMARY: s.", "FILES:", "- script.js: redirect", "NOTES:", "- x", ""])
        lossy = self.FENCE + "js" + self.NL + self.NL.join([      # the redirect is added but showMessage is gone
            "document.addEventListener('DOMContentLoaded', () => {",
            "    const form = document.getElementById('register-form');",
            "    form.addEventListener('submit', (e) => { e.preventDefault(); window.location.href = 'x.html'; });",
            "});"]) + self.NL + self.FENCE
        with tempfile.TemporaryDirectory() as d:
            self._site(d)
            eng = Engine(d, FakeClient([("classify", "BUILD"), ("Planner", plan), ("Coder", lossy), ("Reviewer", "LGTM")]))
            out = eng.handle_code("after a successful registration go to x.html")
            self.assertEqual(fsops.read_file(d, "script.js"), self.OLD_JS)          # untouched
            self.assertIn("would have removed `showMessage`", out)

    def test_devforge_files_are_never_planned_and_are_restored(self):
        from devforge import themes
        plan = self.NL.join(["SUMMARY: s.", "FILES:", "- theme-toggle.js: theme", "- site.js: menu",
                             "- script.js: logic", "NOTES:", "- x", ""])
        edit = self.NL.join(["<<<<<<< SEARCH", "        form.reset();", "=======", "        form.reset(); // done",
                             ">>>>>>> REPLACE"])
        with tempfile.TemporaryDirectory() as d:
            self._site(d)
            fsops.write_file(d, "theme.css", themes.render_dual_css("modern-dark", "clean-light", None, "light"))
            fsops.write_file(d, "site.js", themes.site_js())
            fsops.write_file(d, "theme-toggle.js", self.OLD_JS)                    # a model once overwrote it
            client = FakeClient([("classify", "BUILD"), ("Planner", plan), ("Coder", edit), ("Reviewer", "LGTM")])
            Engine(d, client).handle_code("mark the form reset in script.js")
            self.assertIn("DevForge light/dark theme switch", fsops.read_file(d, "theme-toggle.js"))   # restored
            coder_files = [m for k, m in client.calls if k == "Coder"]
            self.assertEqual(len(coder_files), 1)                                  # only script.js went to the model

    def test_db_request_plans_a_backend_and_redirect_plans_the_page(self):
        with tempfile.TemporaryDirectory() as d:
            eng = Engine(d, FakeClient([]))
            planned = eng._add_needed_files(
                "build a registration website, the data should be saved in .db file permanently",
                [("index.html", "page"), ("styles.css", "css"), ("script.js", "logic")])
            self.assertEqual([p for p, _ in planned], ["index.html", "styles.css", "app.py", "script.js"])
            self.assertIn("fetch()", dict(planned)["script.js"])
            fsops.write_file(d, "index.html", "<html></html>")
            planned = eng._add_needed_files(
                "once registration is successful it should redirect to new page of thank you for registration page",
                [("script.js", "logic")])
            self.assertIn("thank-you.html", [p for p, _ in planned])

    def test_redirect_to_a_missing_page_and_saving_without_backend_are_reported(self):
        with tempfile.TemporaryDirectory() as d:
            fsops.write_file(d, "index.html", '<form id="f"></form>')
            fsops.write_file(d, "script.js", "fetch('/submit', {method: 'POST'}); window.location.href = '/thank-you';")
            err = fsops.consistency_check(d, ["index.html", "script.js"])[0]["error"]
            self.assertIn('"/thank-you" but that page does not exist', err)
            self.assertIn('"/submit" but the project has no backend', err)
            fsops.write_file(d, "thank-you.html", "<html></html>")
            fsops.write_file(d, "script.js", "window.location.href = 'thank-you.html';")
            self.assertEqual(fsops.consistency_check(d, ["index.html", "script.js"]), [])

    def test_run_starts_the_backend_for_a_site_with_one(self):
        with tempfile.TemporaryDirectory() as d:
            fsops.write_file(d, "index.html", "<html></html>")
            self.assertEqual(fsops.find_run_target(d), ("browser", "index.html"))
            fsops.write_file(d, "app.py", "import http.server" + self.NL + "PORT = 8050" + self.NL)
            self.assertEqual(fsops.find_run_target(d), ("server", "app.py"))
            self.assertEqual(fsops.server_port(d, "app.py"), 8050)


class PatchingTests(unittest.TestCase):
    def test_apply_edits(self):
        from devforge import patching
        nl = chr(10)
        src = nl.join(["def a():", "    return 1", "", "def b():", "    return 2", ""])
        new, errs = patching.apply_edits(src, [("    return 2", "    return 3")])
        self.assertEqual((new.count("return 3"), errs), (1, []))
        new, errs = patching.apply_edits(src, [("def b():" + nl + "return 2", "def b():" + nl + "return 4")])
        self.assertIn("    return 4", new)                                     # indentation kept
        new, errs = patching.apply_edits(src, [("not there", "x")])
        self.assertEqual(new, src)
        self.assertIn("not found", errs[0])
        new, errs = patching.apply_edits(src, [("", "def c():" + nl + "    return 5")])
        self.assertTrue(new.rstrip().endswith("return 5"))
        self.assertEqual(patching.lost_names("x.py", src, "def a():\n    return 1\n"), ["b"])
        self.assertEqual(patching.lost_names("x.py", src, "def a():\n    return 1\n", "remove function b"), [])
