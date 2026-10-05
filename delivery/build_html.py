#!/usr/bin/env python3
"""由 delivery/空印_全稿.md 產生閱讀版 HTML：空印_全稿.html（置於專案根目錄，版式同《凌遲》等姊妹專案）。
先執行 delivery/build.py 合稿，再執行本檔。"""
import html, pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent
src = (root / "delivery" / "空印_全稿.md").read_text(encoding="utf-8")

def inline(s):
    s = html.escape(s, quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

CSS = """
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Songti TC", "Songti SC", "Noto Serif CJK TC", "Source Han Serif TC", serif;
    background-color: #f7f4ed;
    color: #262626;
    line-height: 1.95;
    padding: 30px 15px;
    margin: 0;
  }
  .reader-container {
    max-width: 860px;
    margin: 0 auto;
    background: #ffffff;
    padding: 70px 90px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.06);
    border-radius: 4px;
    border: 1px solid #e8e2d5;
  }
  h1 {
    text-align: center;
    font-size: 2.1em;
    margin-top: 50px;
    margin-bottom: 30px;
    color: #801d1d;
    border-bottom: 2px solid #801d1d;
    padding-bottom: 18px;
    letter-spacing: 0.05em;
  }
  h2 {
    font-size: 1.45em;
    color: #3b2220;
    margin-top: 40px;
    border-left: 5px solid #801d1d;
    padding-left: 14px;
  }
  h3 {
    font-size: 1.2em;
    color: #5c3532;
    margin-top: 30px;
    letter-spacing: 0.03em;
  }
  p {
    text-indent: 2em;
    margin-bottom: 1.25em;
    font-size: 1.1em;
    text-align: justify;
  }
  ul { margin: 0 0 1.25em; padding-left: 2em; }
  li { margin-bottom: 0.6em; font-size: 1.05em; text-align: justify; }
  hr {
    border: none;
    height: 1px;
    background: #e5dac6;
    margin: 60px 0;
  }
  strong { color: #111111; }
  @media (max-width: 768px) {
    .reader-container { padding: 30px 20px; }
    p { font-size: 1.02em; }
  }
"""

out, para, items = [], [], []

def flush():
    global para, items
    if para:
        out.append("<p>" + inline("".join(para)) + "</p>")
        para = []
    if items:
        out.append("<ul>\n" + "\n".join(f"<li>{inline(i)}</li>" for i in items) + "\n</ul>")
        items = []

for line in src.splitlines():
    s = line.strip()
    if not s:
        flush(); continue
    m = re.match(r"^(#{1,3}) (.+)$", s)
    if m:
        flush(); n = len(m.group(1)); out.append(f"<h{n}>{inline(m.group(2))}</h{n}>"); continue
    if s == "---":
        flush(); out.append("<hr/>"); continue
    if s.startswith("- "):
        if para: flush()
        items.append(s[2:]); continue
    if items: flush()
    out.append("<p>" + inline(s) + "</p>")
flush()

page = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>《空印》（全十章·定稿閱讀本）</title>
<style>{CSS}</style>
</head>
<body>
<div class="reader-container">
{chr(10).join(out)}
</div>
</body>
</html>
"""
(root / "空印_全稿.html").write_text(page, encoding="utf-8")
print("已寫入 空印_全稿.html", len(page), "bytes")
