#!/usr/bin/env python3
"""以 wiki 页面 frontmatter 的 tags 为唯一真相源，全量重建 index.md 标签索引表。
同时重建页脚「最后更新」行（计数 + 日期），消除手工派生数据。

用法: python3 rebuild_tags.py [wiki_root]
  wiki_root 默认 /mnt/c/Users/elliot/Documents/LLMWiki

配套 lint 检查: 运行后不产生 diff 即说明索引无漂移。
"""
import os, re, glob, sys, collections, subprocess

W = sys.argv[1] if len(sys.argv) > 1 else "/mnt/c/Users/elliot/Documents/LLMWiki"
DIRS = {"concepts": "concept", "entities": "entity", "syntheses": "synthesis"}

tags = collections.defaultdict(list)
counts = {}
for d in DIRS:
    files = sorted(glob.glob(f"{W}/wiki/{d}/*.md"))
    counts[d] = len(files)
    for f in files:
        name = os.path.basename(f)[:-3]
        text = open(f, encoding='utf-8').read()
        fm = re.match(r'^---\n(.*?)\n---', text, re.S)
        if not fm:
            continue
        tm = re.search(r'^tags:\s*\[([^\]]*)\]', fm.group(1), re.M)
        if tm:
            for t in tm.group(1).split(','):
                t = t.strip()
                if t:
                    tags[t].append(name)

rows = ["| 标签 | 相关页面 |", "|------|----------|"]
for t in sorted(tags):
    rows.append(f"| {t} | {', '.join(sorted(tags[t]))} |")
new_table = "\n".join(rows)

idx_path = f"{W}/index.md"
idx = open(idx_path, encoding='utf-8').read()
pat = re.compile(r'(## 标签索引表\n\n).*?(\n\n---)', re.S)
m = pat.search(idx)
if not m:
    sys.exit("错误: index.md 中未找到标签索引表段")
idx_new = idx[:m.start()] + m.group(1) + new_table + m.group(2) + idx[m.end():]

tag_changed = idx_new != idx
if tag_changed:
    open(idx_path, 'w', encoding='utf-8').write(idx_new)
    print(f"已重建标签索引: {len(tags)} 个标签, 覆盖 {len(set(p for ps in tags.values() for p in ps))} 个页面")
else:
    print("标签索引无漂移")

# 重建页脚
date = subprocess.run(['date', '+%F'], capture_output=True, text=True).stdout.strip()
raw_count = len(glob.glob(f"{W}/raw/**/*.md", recursive=True))
total = sum(counts.values())
footer = f"*最后更新：{date} | wiki 页面：{counts['concepts']} concepts + {counts['entities']} entities + {counts['syntheses']} syntheses = {total} | 原始资料：{raw_count}*"
new_idx = re.sub(r'\*最后更新：[^\n]+\*\n?', footer + '\n', idx_new)
footer_changed = new_idx != idx_new
if footer_changed:
    open(idx_path, 'w', encoding='utf-8').write(new_idx)
    print(f"已重建页脚: {counts['concepts']}+{counts['entities']}+{counts['syntheses']}={total} | raw {raw_count} | {date}")
else:
    print("页脚无漂移")
