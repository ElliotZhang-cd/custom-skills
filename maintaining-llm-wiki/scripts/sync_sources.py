#!/usr/bin/env python3
"""以正文「来源」段为唯一真相源，生成 frontmatter sources 数组。
同时规范化「来源段」格式（裸 URL → [url](url)，md 链接 raw → [[raw/path]]）。

规则：LLM 只写「来源」段，frontmatter `sources` 由本脚本统一生成。
提取顺序：raw 路径 → URL → 本地路径 → 原创观察标记。

用法: python3 sync_sources.py [wiki_root]
"""
import os, re, glob, sys

W = sys.argv[1] if len(sys.argv) > 1 else "/mnt/c/Users/elliot/Documents/LLMWiki"
DIRS = ["concepts", "entities", "syntheses"]


def parse_fm_sources(fm):
    """返回 (items, span) 或 (None, None)。span = (start, end)，覆盖整个 sources 键值。"""
    m = re.search(r'^sources:\s*\[([^\]]*)\]', fm, re.M)
    if m:
        items = [s.strip() for s in m.group(1).split(',') if s.strip()]
        return items, (m.start(), m.end())
    m = re.search(r'^sources:\s*\n((?:\s+-\s+.+\n?)+)', fm, re.M)
    if m:
        items = [re.sub(r'^\s+-\s+', '', l).strip() for l in m.group(1).splitlines() if l.strip()]
        return items, (m.start(), m.end())
    return None, None


def normalize_section(body):
    """规范化「来源」段格式；返回 new_body, fixed。"""
    sec_m = re.search(r'^(## 来源\s*\n)((?:.*\n)*?)(?=^## |\Z)', body, re.S | re.M)
    if not sec_m:
        return body, False
    sec = sec_m.group(2)

    fixed = False
    new_lines = []
    for line in sec.split('\n'):
        stripped = line.strip()
        # 裸 URL 行（以 - https://... 开头，无 []()）
        m = re.match(r'^- (https?://\S+)$', stripped)
        if m:
            url = m.group(1)
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(f'{indent}- [{url}]({url})')
            fixed = True
            continue
        # [text](raw/path.md) → [[raw/path.md]]
        m = re.match(r'^- \[([^\]]*)\]\((raw/\S+)\)', stripped)
        if m:
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(f'{indent}- [[{m.group(2)}]]')
            fixed = True
            continue
        new_lines.append(line)

    if not fixed:
        return body, False
    new_sec = '\n'.join(new_lines)
    new_body = body[:sec_m.start(2)] + new_sec + body[sec_m.end(2):]
    return new_body, True


def parse_section_sources(body):
    """从「来源」段按出现顺序提取条目。"""
    m = re.search(r'^## 来源\s*\n(.*?)(?=^## |\Z)', body, re.S | re.M)
    if not m:
        return None
    body = m.group(1)
    items = []
    seen = set()
    for tok in re.finditer(
        r'\[\[(raw/[^\]]+?)\]\]'
        r'|\[[^\]]*\]\((https?://[^)\s]+)\)'
        r'|((?:~/|/home/|/mnt/)[^\s`，。）]+)',
        body,
    ):
        item = tok.group(1) or tok.group(2) or tok.group(3)
        if item and item not in seen:
            if item.startswith(('/', '~/')):
                item = item.rstrip('。，）)')
            seen.add(item)
            items.append(item)
    if '原创观察' in body:
        items.append('原创观察')
    return items


def normalize(items):
    return {s.strip().strip('"').strip("'") for s in items if s and s.strip()}


def yaml_flow_value(items):
    """生成 YAML flow-style 数组值，仅对含特殊字符的条目加单引号。"""
    _special = set('?:#&*!|>%@`,[]{}')
    parts = []
    for s in items:
        if any(c in s for c in _special) or s.startswith('~') or s.strip() != s:
            parts.append("'" + s.replace("'", "''") + "'")
        else:
            parts.append(s)
    return ', '.join(parts)


changed = 0
for d in DIRS:
    for f in sorted(glob.glob(f"{W}/wiki/{d}/*.md")):
        name = os.path.basename(f)[:-3]
        text = open(f, encoding="utf-8").read()
        fm_m = re.match(r'^(---\n)(.*?)(\n---)', text, re.S)
        if not fm_m:
            continue

        section_fixed, fm_fixed = False, False
        text, section_fixed = normalize_section(text)

        fm_m2 = re.match(r'^(---\n)(.*?)(\n---)', text, re.S)
        fm = fm_m2.group(2)
        cur, span = parse_fm_sources(fm)
        new = parse_section_sources(text[fm_m2.end():])
        if new is None:
            if section_fixed:
                open(f, 'w', encoding='utf-8').write(text)
                changed += 1
                print(f"已规范来源段: {d}/{name}.md")
            continue

        flow = yaml_flow_value(new)
        new_line = f'sources: [{flow}]'
        cur_line = fm[span[0]:span[1]].strip() if span else None
        need_rewrite = cur is None or normalize(cur) != normalize(new) or (cur_line and cur_line != new_line)

        if need_rewrite:
            if span:
                new_fm = fm[:span[0]] + fm[span[1]:]
            else:
                new_fm = fm
            new_fm = new_fm.rstrip('\n')
            if new_fm.strip():
                new_fm = new_fm + f'\n{new_line}'
            else:
                new_fm = new_line
            text = text[:fm_m2.start(2)] + new_fm + text[fm_m2.end(2):]
            fm_fixed = True

        if section_fixed or fm_fixed:
            open(f, 'w', encoding='utf-8').write(text)
            changed += 1
            print(f"已同步: {d}/{name}.md → [{flow}]")

print(f"\n== 同步完成: {changed} 页更新 / {sum(len(glob.glob(f'{W}/wiki/{d}/*.md')) for d in DIRS)} 页 ==")
