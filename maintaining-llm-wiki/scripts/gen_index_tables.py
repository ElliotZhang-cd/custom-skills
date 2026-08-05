#!/usr/bin/env python3
"""重建 index.md 三表 + 原始资料表。

分工：
- 三表（概念/实体/综合）：行骨架自动生成（保证每页登记，消灭漏登）；
  语义列（简述、实体类型、综合涵盖范围）保留旧表内容，新页标记「待补」由 LLM 填写。
- 原始资料表：全自动（类型=目录映射，入库日期=git 首次提交日期）。
- 页脚计数与标签索引由 rebuild_tags.py 处理，本脚本不碰。

用法: python3 gen_index_tables.py [wiki_root]
  wiki_root 可选，默认平台自识别（见 wiki_paths.py）
"""
import os, re, glob, sys, subprocess
from wiki_paths import default_wiki_root

W = sys.argv[1] if len(sys.argv) > 1 else default_wiki_root()
IDX = f"{W}/index.md"

TYPE_MAP = {
    "reference": "reference",
    "configs": "configs",
    "logs": "logs",
    "webpages": "webpages",
    "projects": "projects",
    "hermes-agent-orange-book": "reference",
    "README.md": "meta",
}

TABLES = {
    "concepts": ("概念表", "概念", "简述", "标签"),
    "entities": ("实体表", "实体", "类型", "简述"),
    "syntheses": ("综合表", "主题", "涵盖范围", "简述"),
}

def get_fm_tags(text):
    m = re.search(r"^tags:\s*\[([^\]]*)\]", text, re.M)
    if not m:
        return ""
    return ", ".join(t.strip() for t in m.group(1).split(",") if t.strip())

def git_first_date(path):
    r = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%ad", "--date=short", "--", path],
        cwd=W, capture_output=True, text=True)
    d = r.stdout.strip().splitlines()
    return d[0] if d else ""

def parse_table(idx, dirname, ncols):
    """提取现有表格行: name -> 语义列列表（跳过首列）。"""
    m = re.search(rf"^## {dirname}\n\n(?:扫描[^\n]*\n)?\n?\|[^\n]*\n\|[-| :]+\|\n((?:.*\n)*?)(?=^## |\Z)", idx, re.M)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < ncols:
            continue
        name = cells[0].strip("[]")
        out[name] = cells[1:ncols]
    return out

def build_table(idx, d, headers):
    label, h1, *semantic_headers = headers
    old = parse_table(idx, label, 1 + len(semantic_headers))
    rows = []
    for f in sorted(glob.glob(f"{W}/wiki/{d}/*.md")):
        name = os.path.basename(f)[:-3]
        text = open(f, encoding="utf-8").read()
        sem = old.get(name) or ["待补简述"] * len(semantic_headers)
        sem = sem + ["待补简述"] * (len(semantic_headers) - len(sem))  # 列数变化兜底
        tags = get_fm_tags(text)
        if d == "concepts":
            cells = [f"[[{name}]]", sem[0], tags]
        elif d == "entities":
            cells = [f"[[{name}]]", sem[0], sem[1]]
        else:
            cells = [f"[[{name}]]", sem[0], sem[1]]
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)

def build_raw_table(idx):
    raw_files = sorted(os.path.relpath(f, W).replace("\\", "/") for f in glob.glob(f"{W}/raw/**/*.md", recursive=True))
    old = parse_table(idx, "原始资料表", 3)
    rows = []
    for rf in raw_files:
        top = rf.split("/")[1] if rf.count("/") >= 2 else rf.split("/")[1]
        kind = TYPE_MAP.get(rf.split("/")[1], TYPE_MAP.get(os.path.basename(rf), "unknown"))
        if rf.count("/") == 1:
            kind = TYPE_MAP.get(os.path.basename(rf), "unknown")
        date = git_first_date(rf)
        rows.append(f"| [[{rf}]] | {kind} | {date} |")
    return "\n".join(rows)

idx = open(IDX, encoding="utf-8").read()
stats = {"added": [], "todo": []}

for d, headers in TABLES.items():
    label = headers[0]
    new_rows = build_table(idx, d, headers)
    pat = re.compile(rf"(^## {label}\n\n(?:扫描[^\n]*\n)?\n?\|[^\n]*\n\|[-| :]+\|\n)(.*?)(?=^## |\Z)", re.M | re.S)
    m = pat.search(idx)
    if not m:
        print(f"[!] 未找到 {label} 段，跳过")
        continue
    new_table = m.group(1) + new_rows + "\n\n"
    idx = idx[:m.start()] + new_table + idx[m.end():]

raw_rows = build_raw_table(idx)
pat = re.compile(r"(^## 原始资料表\n\n[^\n]*\n\n\|[^\n]*\n\|[-| :]+\|\n)(.*?)(?=^## |\Z)", re.M | re.S)
m = pat.search(idx)
if not m:
    print("[!] 未找到 原始资料表 段，跳过")
else:
    idx = idx[:m.start()] + m.group(1) + raw_rows + "\n\n" + idx[m.end():]

open(IDX, "w", encoding="utf-8").write(idx)
print(f"== index 三表 + 原始资料表已重建 ==")
