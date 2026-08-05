#!/usr/bin/env python3
"""迁移超长页正文到 raw/reference/（蒸馏拆分 2026-08-05）。

function-calling.md:      正文 = ## 要点 之后 → ## 相关 之前
reasonix-guide-summary.md: 正文 = ## 新手快速入门 之后 → ## 相关 之前
"""
import re, sys

W = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\elliot\Documents\LLMWiki"

JOBS = [
    (
        f"{W}/wiki/concepts/function-calling.md",
        f"{W}/raw/reference/function-calling-guide-zh.md",
        r"^## 要点\s*\n", r"^## 相关",
        """# Function Calling 中文详解（翻译整理版）

> 来源：https://platform.openai.com/docs/guides/function-calling
> 性质：OpenAI Function Calling 官方文档的中文翻译 + 结构重组详解（§1-§17）
> 关联原文：[[raw/webpages/openai-function-calling.md]]（英文原文存档）
> 迁移：2026-08-05 蒸馏拆分，由 wiki/concepts/function-calling.md 正文迁移至此

---
""",
    ),
    (
        f"{W}/wiki/syntheses/reasonix-guide-summary.md",
        f"{W}/raw/reference/reasonix-guide-zh.md",
        r"^## 新手快速入门\s*\n", r"^## 相关",
        """# Reasonix 使用指南 逐章详解（整理版）

> 来源：https://github.com/esengine/DeepSeek-Reasonix/blob/main-v2/docs/GUIDE.zh-CN.md
> 性质：Reasonix 官方 GUIDE.zh-CN.md 的逐章详解整理（含示例、快捷键、命令速查）
> 关联原文：[[raw/reference/GUIDE.zh-CN.md]]（官方指南存档）
> 迁移：2026-08-05 蒸馏拆分，由 wiki/syntheses/reasonix-guide-summary.md 正文迁移至此

---
""",
    ),
]

for src, dst, start_re, end_re, header in JOBS:
    text = open(src, encoding="utf-8").read()
    m = re.search(start_re, text, re.M)
    if not m:
        print(f"[!] {src}: 起点未找到")
        continue
    body = text[m.end():]
    m2 = re.search(end_re, body, re.M)
    if m2:
        body = body[:m2.start()]
    body = body.rstrip() + "\n"
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(header + body)
    print(f"OK: {dst} ({body.count(chr(10))} 行正文)")
