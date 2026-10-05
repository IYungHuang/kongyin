#!/usr/bin/env python3
"""合稿：把 manuscript/chapter_01~10.md 的正文（刪去「## 編輯附註」「## 交稿說明」以後）合成 delivery/空印_全稿.md。
附註與交稿說明不屬小說正文，匯出時排除。後記另置於 delivery/afterword.md，附於全稿之後。"""
import re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
out = []
total = 0
for n in range(1, 11):
    t = (root / "manuscript" / f"chapter_{n:02d}.md").read_text(encoding="utf-8")
    body = re.split(r"\n## 編輯附註", t)[0].strip()
    k = len(re.findall(r"[一-鿿]", body))
    total += k
    out.append(body)
    print(f"ch{n:02d}: {k}")
print("正文純漢字合計:", total)
title = "# 空印\n\n"
after = (root / "delivery" / "afterword.md").read_text(encoding="utf-8").strip()
text = title + "\n\n---\n\n".join(out) + "\n\n---\n\n" + after + "\n"
(root / "delivery" / "空印_全稿.md").write_text(text, encoding="utf-8")
(root / "空印_全稿.md").write_text(text, encoding="utf-8")
print("已寫入 delivery/空印_全稿.md 與根目錄 空印_全稿.md")
