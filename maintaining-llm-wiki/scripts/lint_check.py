#!/usr/bin/env python3
"""LLM Wiki 机械 lint 检查 — 确定性检查脚本化，LLM 只做语义判断。

6 项检查（机械可判定，无需语义）：
1. 断链      wikilink 目标不存在（剥离代码块/行内代码后提取）
2. 禁止字段  frontmatter 含 source_count/updated（派生物，已两次回潮，见 pitfalls.md）
3. type 一致 frontmatter type 与所在目录一致
4. index     页脚计数 vs 文件系统；wiki/raw 文件全部登记
5. sources   frontmatter sources 与正文「来源」段一一对应
6. 互链      孤立页（入链 ≤2）+ 单向链接（A→B 但 B 不回链）

用法: python3 lint_check.py [wiki_root]
  wiki_root 默认 /mnt/c/Users/elliot/Documents/LLMWiki

输出分两级：
  [E] ERROR — 机械可判定、应修复（检查 1-5）
  [I] INFO  — 需人工判断（检查 6；已确认跳过的单项链录入 KNOWN_ONEWAY）
退出码: 0 = 无 ERROR, 1 = 有 ERROR
"""
import os, re, glob, sys, collections

W = sys.argv[1] if len(sys.argv) > 1 else "/mnt/c/Users/elliot/Documents/LLMWiki"
DIRS = {"concepts": "concept", "entities": "entity", "syntheses": "synthesis"}

# 用户确认跳过的单向链接对（A→B 无回链被接受）。lint 确认残留后追加到此。
KNOWN_ONEWAY = frozenset({
    # ("a-page", "b-page"),
})

# 用户确认的孤立页（入链少属有意独立，非缺陷）。
KNOWN_ORPHAN = frozenset({
    "English-level-up-tips",  # 2026-07-21 用户裁定：独立岛页，无需强加关联
})

# 用户确认的 sources 特例（fm 与来源段有意不一一对应）。
KNOWN_SOURCES_EXCEPTION = frozenset({
    # "page-name",  # 原因
})

errors, infos = [], []

# ---------- 读取全部 wiki 页面 ----------
pages = {}  # name -> {dir, text, fm, links}
for d in DIRS:
    for f in sorted(glob.glob(f"{W}/wiki/{d}/*.md")):
        name = os.path.basename(f)[:-3]
        text = open(f, encoding="utf-8").read()
        fm_m = re.match(r"^---\n(.*?)\n---", text, re.S)
        fm = fm_m.group(1) if fm_m else ""
        # 剥离代码块与行内代码后提取 wikilink（历史误报：TOML 的 [[plugins]]、代码中的 [[wikilink]]）
        body = re.sub(r"```.*?```", "", text, flags=re.S)
        body = re.sub(r"`[^`\n]*`", "", body)
        links = re.findall(r"\[\[([^\[\]|]+?)(?:\|[^\[\]]*)?\]\]", body)
        pages[name] = {"dir": d, "text": text, "fm": fm, "links": links}

root_files = {f for f in os.listdir(W) if f.endswith(".md")}  # index.md / log.md 等

def resolve(link):
    """返回 (kind, exists)。kind: wiki | raw | root"""
    if link.startswith("raw/") or "/" in link:
        return "raw", os.path.isfile(f"{W}/{link}") or os.path.isfile(f"{W}/{link}.md")
    if link in pages:
        return "wiki", True
    if f"{link}.md" in root_files or link in root_files:
        return "root", True
    name = link[:-3] if link.endswith(".md") else link
    return "wiki", name in pages

# ---------- 检查 1: 断链 ----------
for name, p in sorted(pages.items()):
    for link in p["links"]:
        kind, exists = resolve(link)
        if not exists:
            hint = "（缺 .md 后缀？）" if "/" in link and os.path.isfile(f"{W}/{link}.md") else ""
            errors.append(f"[断链] {p['dir']}/{name}.md → [[{link}]]{hint}")

# ---------- 检查 2: 禁止字段 ----------
for name, p in sorted(pages.items()):
    for field in ("source_count", "updated"):
        if re.search(rf"^{field}:", p["fm"], re.M):
            errors.append(f"[禁止字段] {p['dir']}/{name}.md frontmatter 含 {field}（派生物，真相源：sources 数组 / git）")

# ---------- 检查 3: type 与目录一致 ----------
for name, p in sorted(pages.items()):
    tm = re.search(r"^type:\s*(\S+)", p["fm"], re.M)
    if not tm:
        errors.append(f"[type] {p['dir']}/{name}.md 缺 type 字段")
    elif tm.group(1) != DIRS[p["dir"]]:
        errors.append(f"[type] {p['dir']}/{name}.md type={tm.group(1)}，应为 {DIRS[p['dir']]}")

# ---------- 检查 4: index 一致性 ----------
idx = open(f"{W}/index.md", encoding="utf-8").read()
actual = {d: len(glob.glob(f"{W}/wiki/{d}/*.md")) for d in DIRS}
raw_files = sorted(os.path.relpath(f, W) for f in glob.glob(f"{W}/raw/**/*.md", recursive=True))
fm_m = re.search(r"wiki 页面：(\d+) concepts \+ (\d+) entities \+ (\d+) syntheses = (\d+) \| 原始资料：(\d+)", idx)
if not fm_m:
    errors.append("[index] 页脚计数行缺失或格式不符")
else:
    got = tuple(map(int, fm_m.groups()))
    want = (actual["concepts"], actual["entities"], actual["syntheses"], sum(actual.values()), len(raw_files))
    if got != want:
        errors.append(f"[index] 页脚计数漂移：index={got} 实际={want}")
for name, p in sorted(pages.items()):
    if f"[[{name}]]" not in idx:
        errors.append(f"[index] wiki 页未登记：{p['dir']}/{name}.md")
for rf in raw_files:
    if f"[[{rf}]]" not in idx:
        errors.append(f"[index] raw 未登记：{rf}")

# ---------- 检查 5: sources 一致性 ----------
def parse_fm_sources(fm):
    m = re.search(r"^sources:\s*\[([^\]]*)\]", fm, re.M)
    if m:
        return [s.strip().strip("'\"") for s in m.group(1).split(",") if s.strip()]
    m = re.search(r"^sources:\s*\n((?:\s+-\s+.+\n?)+)", fm, re.M)
    if m:
        return [re.sub(r"^\s+-\s+", "", l).strip().strip("'\"") for l in m.group(1).splitlines() if l.strip()]
    return None

def parse_source_section(text):
    m = re.search(r"^## 来源\s*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        return None
    body = m.group(1)
    md_raws = set(re.findall(r"\[[^\]]*\]\((raw/[^)\s]+)\)", body))
    raws = set(re.findall(r"\[\[(raw/[^\]]+?)\]\]", body)) | md_raws
    md_urls = set(re.findall(r"\[[^\]]*\]\((https?://[^)\s]+)\)", body))
    bare_urls = {u for u in re.findall(r"https?://[^\s)\]，。]+", body) if u not in md_urls}
    urls = md_urls | bare_urls
    locals_ = set(re.findall(r"(?:^|[\s`])((?:~/|/home/|/mnt/)[^\s`，。）]+)", body, re.M))
    return {"raws": raws, "md_raws": md_raws, "urls": urls, "bare_urls": bare_urls, "locals": locals_, "original": "原创观察" in body}

for name, p in sorted(pages.items()):
    fm_src = parse_fm_sources(p["fm"])
    sec = parse_source_section(p["text"])
    if fm_src is None:
        errors.append(f"[sources] {p['dir']}/{name}.md frontmatter 缺 sources 字段")
        continue
    if name in KNOWN_SOURCES_EXCEPTION:
        continue
    if sec is None:
        errors.append(f"[sources] {p['dir']}/{name}.md 缺「## 来源」段")
        continue
    fm_raws = {s for s in fm_src if s.startswith("raw/")}
    fm_urls = {s for s in fm_src if s.startswith("http")}
    fm_locals = {s for s in fm_src if s.startswith(("~/", "/home/", "/mnt/"))}
    fm_original = any("原创观察" in s for s in fm_src)
    fm_other = set(fm_src) - fm_raws - fm_urls - fm_locals - {s for s in fm_src if "原创观察" in s}
    diff = []
    if fm_raws != sec["raws"]:
        diff.append(f"raw 不一致 fm={sorted(fm_raws)} 段={sorted(sec['raws'])}")
    if fm_urls != sec["urls"]:
        diff.append(f"URL 不一致 fm={sorted(fm_urls)} 段={sorted(sec['urls'])}")
    if fm_locals != sec["locals"]:
        diff.append(f"本地路径不一致 fm={sorted(fm_locals)} 段={sorted(sec['locals'])}")
    if fm_original != sec["original"]:
        diff.append("原创观察标记不一致")
    if fm_other:
        diff.append(f"无法归类条目：{sorted(fm_other)}")
    if diff:
        errors.append(f"[sources] {p['dir']}/{name}.md — {'；'.join(diff)}")
    if sec["md_raws"]:
        errors.append(f"[格式] {p['dir']}/{name}.md 来源段 raw 引用应使用 wikilink 而非 md 链接：{sorted(sec['md_raws'])}")
    if sec["bare_urls"]:
        errors.append(f"[格式] {p['dir']}/{name}.md 来源段 URL 应使用 [描述](url) 而非裸链接：{sorted(sec['bare_urls'])}")

# ---------- 检查 6: 互链（INFO） ----------
inlinks = collections.Counter()
out = {n: {l for l in p["links"] if resolve(l)[1] and resolve(l)[0] == "wiki" and l != n} for n, p in pages.items()}
# 统一解析成页面名（容忍 [[name.md]] 写法）
def to_page(l):
    return l[:-3] if l.endswith(".md") else l
out = {n: {to_page(l) for l in ls if to_page(l) in pages} for n, ls in out.items()}
for n, ls in out.items():
    for l in ls:
        inlinks[l] += 1
for name in sorted(pages):
    if inlinks[name] <= 2 and name not in KNOWN_ORPHAN:
        infos.append(f"[孤立页] {pages[name]['dir']}/{name}.md 入链={inlinks[name]}")
for a in sorted(out):
    for b in sorted(out[a]):
        if a not in out.get(b, set()) and (a, b) not in KNOWN_ONEWAY and (b, a) not in KNOWN_ONEWAY:
            infos.append(f"[单向] {a} → {b}（{b} 无回链）")

# ---------- 检查 7: log 行数 + git 脏工作区（INFO） ----------
log_path = f"{W}/log.md"
if os.path.isfile(log_path):
    log_lines = sum(1 for _ in open(log_path, encoding="utf-8"))
    if log_lines > 500:
        infos.append(f"[log] log.md 已 {log_lines} 行，超过 500 行阈值，建议归档（见 references/log-format.md）")

import subprocess
r = subprocess.run(["git", "status", "--porcelain"], cwd=W, capture_output=True, text=True)
if r.returncode == 0 and r.stdout.strip():
    dirty = [l.strip() for l in r.stdout.strip().split("\n") if l.strip()]
    infos.append(f"[git] 工作区未提交：{len(dirty)} 个文件（可能忘 commit）")

# ---------- 输出 ----------
for e in errors:
    print(f"[E] {e}")
for i in infos:
    print(f"[I] {i}")
print(f"\n== {len(errors)} ERROR / {len(infos)} INFO | 页面 {len(pages)} | raw {len(raw_files)} ==")
sys.exit(1 if errors else 0)
