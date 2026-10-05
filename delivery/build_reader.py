#!/usr/bin/env python3
"""產生精裝閱讀版 HTML：空印_精裝閱讀版.html（根目錄；版式參照《至斬而止》精裝閱讀版）。
正文取自 manuscript/chapter_01~10.md（排除編輯附註、交稿說明），後記取自 delivery/afterword.md。
樣式在 delivery/reader.css。"""
import html, pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent
NUM = "一二三四五六七八九十"

def inline(s):
    s = html.escape(s, quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

def han(s):
    return len(re.findall(r"[一-鿿]", s))

chapters, total = [], 0
for n in range(1, 11):
    t = (root / "manuscript" / f"chapter_{n:02d}.md").read_text(encoding="utf-8")
    body = re.split(r"\n## 編輯附註", t)[0].strip()
    lines = body.splitlines()
    title = re.match(r"# 《(.+)》", lines[0]).group(1)
    rest = [l.strip() for l in lines[1:]]
    while rest and rest[-1] in ("", "---"):
        rest.pop()
    k = han("".join(rest))
    total += k
    out, prev_hr = [], False
    for l in rest:
        if not l:
            continue
        if l == "---":
            if not prev_hr:
                out.append('<div class="scene-divider">◇ ◇ ◇</div>')
            prev_hr = True
            continue
        prev_hr = False
        out.append(f"<p>{inline(l)}</p>")
    chapters.append((n, title, k, "\n".join(out)))

# 後記
after, items, para = [], [], []
def flush():
    global items
    if items:
        after.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>")
        items = []
for l in (root / "delivery" / "afterword.md").read_text(encoding="utf-8").splitlines():
    s = l.strip()
    if not s:
        continue
    if s.startswith("## "):
        continue
    if s.startswith("### "):
        flush(); after.append(f"<h3>{inline(s[4:])}</h3>"); continue
    if s.startswith("- "):
        items.append(s[2:]); continue
    flush(); after.append(f"<p>{inline(s)}</p>")
flush()

nav = "\n".join(
    f'''            <li class="nav-item" data-target="ch{n:02d}">
                <a href="#ch{n:02d}">
                    <div class="nav-title">第{NUM[n-1]}章：{t}</div>
                    <div class="nav-meta"><span>{k:,} 字</span></div>
                </a>
            </li>''' for n, t, k, _ in chapters)
nav += '''
            <li class="nav-item" data-target="afterword">
                <a href="#afterword">
                    <div class="nav-title">創作後記</div>
                    <div class="nav-meta"><span>史實與虛構的邊界</span></div>
                </a>
            </li>'''

cards = "\n".join(f'''            <article id="ch{n:02d}" class="chapter-card">
                <header class="chapter-header">
                    <div class="chapter-badge">
                        <span class="badge-seq">第 {n} 章</span>
                        <span class="badge-date">{k:,} 字</span>
                    </div>
                    <h2 class="chapter-main-heading">第{NUM[n-1]}章：{t}</h2>
                    <div class="chapter-divider-line"></div>
                </header>
                <div class="chapter-body">
{b}
                </div>
            </article>''' for n, t, k, b in chapters)

css = (root / "delivery" / "reader.css").read_text(encoding="utf-8")

JS = """
        const K = 'kongyin_';
        const get = k => { try { return localStorage.getItem(K + k); } catch (e) { return null; } };
        const set = (k, v) => { try { localStorage.setItem(K + k, v); } catch (e) {} };
        const root = document.documentElement;

        window.addEventListener('scroll', () => {
            const h = root.scrollHeight - root.clientHeight;
            document.getElementById('progress-bar').style.width = (h > 0 ? root.scrollTop / h * 100 : 0) + '%';
        });

        const sidebar = document.getElementById('sidebar');
        document.getElementById('toggle-sidebar').addEventListener('click', () => {
            sidebar.classList.toggle(window.innerWidth <= 992 ? 'mobile-open' : 'collapsed');
        });
        sidebar.addEventListener('click', e => {
            if (e.target.closest('a') && window.innerWidth <= 992) sidebar.classList.remove('mobile-open');
        });
        document.getElementById('btn-back-top').addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

        const themes = [{ id: 'xuan', label: '宣紙' }, { id: 'ivory', label: '象牙' }, { id: 'moon', label: '月魄' }, { id: 'white', label: '素白' }];
        let ti = 0;
        const themeLabel = document.getElementById('theme-label');
        const applyTheme = i => { ti = i; root.setAttribute('data-theme', themes[i].id); themeLabel.textContent = themes[i].label; };
        document.getElementById('btn-theme').addEventListener('click', () => { applyTheme((ti + 1) % themes.length); set('theme', themes[ti].id); });

        let fs = 19;
        const applySize = () => root.style.setProperty('--font-size', fs + 'px');
        document.getElementById('btn-font-dec').addEventListener('click', () => { if (fs > 15) { fs--; applySize(); set('fontsize', fs); } });
        document.getElementById('btn-font-inc').addEventListener('click', () => { if (fs < 25) { fs++; applySize(); set('fontsize', fs); } });

        const fonts = [{ name: '宋體', val: 'var(--font-serif)' }, { name: '楷體', val: 'var(--font-kai)' }, { name: '黑體', val: 'var(--font-sans)' }];
        let fi = 0;
        const fontLabel = document.getElementById('font-family-label');
        const applyFont = i => { fi = i; root.style.setProperty('--reader-font', fonts[i].val); fontLabel.textContent = fonts[i].name; };
        document.getElementById('btn-font-family').addEventListener('click', () => { applyFont((fi + 1) % fonts.length); set('font', fonts[fi].name); });

        const sections = document.querySelectorAll('.chapter-card, .afterword-card');
        const navItems = document.querySelectorAll('.nav-item');
        window.addEventListener('scroll', () => {
            let cur = '';
            sections.forEach(s => { if (window.pageYOffset >= s.offsetTop - 120) cur = s.id; });
            navItems.forEach(i => i.classList.toggle('active', i.dataset.target === cur));
        });

        const st = themes.findIndex(t => t.id === get('theme')); if (st >= 0) applyTheme(st);
        const sz = parseInt(get('fontsize')); if (sz >= 15 && sz <= 25) { fs = sz; applySize(); }
        const sf = fonts.findIndex(f => f.name === get('font')); if (sf >= 0) applyFont(sf);
"""

page = f"""<!DOCTYPE html>
<html lang="zh-Hant" data-theme="xuan">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>空印 — 全書精裝閱讀版</title>
    <style>
{css}
    </style>
</head>
<body>
    <div id="progress-bar"></div>

    <header class="top-toolbar">
        <div class="brand-section">
            <button class="tool-btn" id="toggle-sidebar" title="切換章節目錄"><span class="btn-icon">☰</span><span class="btn-text">目錄</span></button>
            <span class="brand-title">空印</span>
            <span class="brand-badge">十章全</span>
        </div>
        <div class="toolbar-actions">
            <button class="tool-btn" id="btn-font-family" title="切換字體風格"><span class="btn-icon">文</span><span class="btn-text" id="font-family-label">宋體</span></button>
            <button class="tool-btn" id="btn-font-dec" title="字級縮小">A-</button>
            <button class="tool-btn" id="btn-font-inc" title="字級放大">A+</button>
            <button class="tool-btn" id="btn-theme" title="切換閱讀色調"><span class="btn-icon">🎨</span><span class="btn-text" id="theme-label">宣紙</span></button>
        </div>
    </header>

    <div class="app-layout">
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header"><div class="sidebar-title">章節目錄</div></div>
            <ul class="nav-list">
{nav}
            </ul>
        </aside>

        <main class="main-content">
            <div class="reader-container">
                <section class="front-card">
                    <div class="front-seal">洪武九年</div>
                    <h1 class="front-title">空印</h1>
                    <p class="front-subtitle">借古喻今的歷史中篇</p>
                    <div class="meta-grid">
                        <div><div class="meta-col-label">背景</div><div class="meta-col-val">明洪武九年（1376）空印案</div></div>
                        <div><div class="meta-col-label">篇幅</div><div class="meta-col-val">十章，正文約 {total:,} 字</div></div>
                        <div><div class="meta-col-label">附錄</div><div class="meta-col-val">創作後記：有史可據與全屬虛構</div></div>
                    </div>
                </section>

{cards}

                <section id="afterword" class="chapter-card afterword-card">
                    <header class="chapter-header">
                        <h2 class="chapter-main-heading">創作後記</h2>
                        <div class="chapter-divider-line"></div>
                    </header>
                    <div class="afterword-body">
{chr(10).join(after)}
                    </div>
                    <div style="text-align:center"><div class="fin-seal">空印</div></div>
                </section>
            </div>
        </main>
    </div>

    <div class="fab-container">
        <button class="fab-btn" id="btn-back-top" title="回到頂部">▲</button>
    </div>

    <script>{JS}    </script>
</body>
</html>
"""
(root / "空印_精裝閱讀版.html").write_text(page, encoding="utf-8")
print("已寫入 空印_精裝閱讀版.html", len(page), "bytes；正文", total, "字")
