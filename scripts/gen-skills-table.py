#!/usr/bin/env python3
"""Generate the <skills_system> table block for AGENTS.md.

Scans the global skills directory (~/.agents/skills), parses each SKILL.md
frontmatter with PyYAML (handles YAML block scalars that openskills mangled),
and replaces the <skills_system>...</skills_system> section in AGENTS.md.

Usage:
  python3 gen-skills-table.py            # write to ~/AGENTS.md (auto-backup)
  python3 gen-skills-table.py --dry-run  # print diff, no write
  python3 gen-skills-table.py --output /path/to/AGENTS.md
  python3 gen-skills-table.py --agents-dir /path/to/skills
  python3 gen-skills-table.py --readme ~/custom-skills/README.md
                                         # 重建 README 里的两个生成块（分发目标一览 + 自建技能表）

为什么有 --readme：README 里的目标数与技能表以前靠人工维护，正是「文档↔事实」漂移的
高频来源（2026-10-17 对齐现状报告 B1–B5）。生成取代校验：让漂移不可能，而不是检测它。
"""
import argparse
import json
import os
import re
import shutil
import sys
import yaml

SKILLS_SYSTEM_RE = re.compile(r"<skills_system[^>]*>.*?</skills_system>", re.DOTALL)

# --readme 模式的生成块：标记之间的一切由本脚本重建，标记之外一律是手写内容。
EXPECT_LABEL = {"selfbuilt": "自建", "mllw": "第二个来源",
                "thirdparty": "第三方", "manual": "手工技能"}

USAGE_BLOCK = """<usage>
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively. Skills provide specialized capabilities and domain knowledge.

How to use skills:
- Invoke your agent's native skill loading mechanism (e.g. opencode's `skill` tool, Claude Code's `Skill` tool)
- The skill content will load with detailed instructions on how to complete the task
- Base directory provided in output for resolving bundled resources (references/, scripts/, assets/)

Usage notes:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already loaded in your context
- Each skill invocation is stateless
</usage>"""


def xml_escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def read_skill_meta(skill_dir):
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        return None
    try:
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return None
    fm = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm:
        return None
    try:
        meta = yaml.safe_load(fm.group(1)) or {}
    except yaml.YAMLError:
        return None
    name = meta.get("name")
    description = meta.get("description")
    if not name or not description:
        return None
    return {
        "name": str(name).strip(),
        "description": str(description).strip(),
    }


def build_section(skills):
    skill_tags = []
    for s in skills:
        skill_tags.append(
            f"<skill>\n"
            f"<name>{xml_escape(s['name'])}</name>\n"
            f"<description>{xml_escape(s['description'])}</description>\n"
            f"<location>project</location>\n"
            f"</skill>"
        )
    body = "\n\n".join(skill_tags)
    return (
        '<skills_system priority="1">\n\n'
        "## Available Skills\n\n"
        "<!-- SKILLS_TABLE_START -->\n"
        f"{USAGE_BLOCK}\n\n"
        "<available_skills>\n\n"
        f"{body}\n\n"
        "</available_skills>\n"
        "<!-- SKILLS_TABLE_END -->\n\n"
        "</skills_system>"
    )


def collect_skills(agents_dir):
    skills = []
    if os.path.isdir(agents_dir):
        for entry in sorted(os.listdir(agents_dir)):
            full = os.path.join(agents_dir, entry)
            if os.path.isdir(full):
                meta = read_skill_meta(full)
                if meta:
                    skills.append(meta)
    skills.sort(key=lambda s: s["name"])
    return skills


def replace_section(content, new_section):
    if SKILLS_SYSTEM_RE.search(content):
        return SKILLS_SYSTEM_RE.sub(lambda m: new_section, content, count=1)
    return content.rstrip() + "\n\n" + new_section + "\n"


def first_sentence(text, limit=110):
    part = re.split(r"(?<=[。！？!?])\s*", text.strip())[0].strip()
    if len(part) > limit:
        part = part[:limit].rstrip() + "…"
    return part.replace("|", "\\|")


def build_targets_table(targets):
    """分发目标一览（给人看）。平台加载机制的细节不复述——见清单条目的 note 字段。"""
    lines = ["| 目标 | 路径 | 角色 | 加载什么 |", "|---|---|---|---|"]
    for t in targets:
        rel = [x for x in t.get("relpath", []) if x]
        if t.get("platform", "posix") == "win":
            path = "%USERPROFILE%\\" + "\\".join(rel)
        else:
            path = "~/" + "/".join(rel)
        expect = "、".join(EXPECT_LABEL.get(e, e) for e in t.get("expect", []))
        lines.append(f"| `{t.get('id', '')}` | `{path}` | {t.get('role', '')} | {expect} |")
    return "\n".join(lines)


def build_selfbuilt_table(skills):
    lines = ["| 技能 | 一句话 |", "|---|---|"]
    for s in skills:
        lines.append(f"| `{s['name']}` | {first_sentence(s['description'])} |")
    return "\n".join(lines)


def replace_readme_block(content, marker, body):
    """替换 <!-- MARKER_START --> … <!-- MARKER_END -->；标记缺失即报错（不静默追加）。"""
    pat = re.compile(r"<!-- " + marker + r"_START -->.*?<!-- " + marker + r"_END -->",
                     re.DOTALL)
    if not pat.search(content):
        raise KeyError(marker)
    block = f"<!-- {marker}_START -->\n{body}\n<!-- {marker}_END -->"
    return pat.sub(lambda m: block, content, count=1)


def inside_git_worktree(path):
    """目标是否在 git 工作树内：是的话 git 就是备份，不必再写 .bak（.bak 会变成未跟踪文件）。"""
    p = os.path.dirname(os.path.abspath(path))
    while True:
        if os.path.exists(os.path.join(p, ".git")):
            return True
        parent = os.path.dirname(p)
        if parent == p:
            return False
        p = parent


def main_readme(args):
    targets_path = args.targets or os.path.join(args.repo, "scripts",
                                                "distribution-targets.json")
    if not os.path.isfile(targets_path):
        print(f"error: 缺少分发清单 {targets_path}", file=sys.stderr)
        return 1
    try:
        with open(targets_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, ValueError) as e:
        print(f"error: 分发清单读取失败 {targets_path}: {e}", file=sys.stderr)
        return 1
    targets = cfg.get("surfaces")
    if not isinstance(targets, list):
        print(f"error: 分发清单缺少 surfaces 数组 {targets_path}", file=sys.stderr)
        return 1
    skills = collect_skills(args.repo)
    if not skills:
        print(f"error: 未在 {args.repo} 找到自建技能（含 SKILL.md 的目录）", file=sys.stderr)
        return 1
    try:
        with open(args.readme, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        print(f"error: {args.readme} 读取失败: {e}", file=sys.stderr)
        return 1
    new_content = content
    for marker, body in (("TARGETS_TABLE", build_targets_table(targets)),
                         ("SELF_BUILT_TABLE", build_selfbuilt_table(skills))):
        try:
            new_content = replace_readme_block(new_content, marker, body)
        except KeyError:
            print(f"error: {args.readme} 缺少生成块标记 "
                  f"<!-- {marker}_START --> / <!-- {marker}_END -->", file=sys.stderr)
            return 1
    if new_content == content:
        print(f"{args.readme}: no change ({len(targets)} targets, {len(skills)} skills)")
        return 0
    if args.dry_run:
        import difflib
        sys.stdout.writelines(difflib.unified_diff(
            content.splitlines(keepends=True), new_content.splitlines(keepends=True),
            fromfile=f"{args.readme} (current)", tofile=f"{args.readme} (new)", n=2))
        print(f"\n[{len(targets)} targets, {len(skills)} skills, write skipped (dry-run)]")
        return 0
    if inside_git_worktree(args.readme):
        with open(args.readme, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_content)
        print(f"{args.readme}: updated ({len(targets)} targets, {len(skills)} skills)，"
              f"未写 .bak（在 git 工作树内，git 即备份）")
        return 0
    backup = args.readme + ".bak"
    shutil.copy2(args.readme, backup)
    with open(args.readme, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)
    print(f"{args.readme}: updated ({len(targets)} targets, {len(skills)} skills), "
          f"backup at {backup}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print diff without writing")
    parser.add_argument("--output", default=os.path.expanduser("~/AGENTS.md"))
    parser.add_argument("--agents-dir", default=os.path.expanduser("~/.agents/skills"))
    parser.add_argument("--readme", default=None,
                        help="改为重建 README 里的生成块（分发目标一览 + 自建技能表）")
    parser.add_argument("--repo", default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), help="自建仓库根（--readme 模式用）")
    parser.add_argument("--targets", default=None,
                        help="分发清单路径（默认 <repo>/scripts/distribution-targets.json）")
    args = parser.parse_args()

    if args.readme:
        return main_readme(args)

    skills = collect_skills(args.agents_dir)
    if not skills:
        print(f"error: no skills found in {args.agents_dir}", file=sys.stderr)
        sys.exit(1)

    new_section = build_section(skills)

    if os.path.isfile(args.output):
        with open(args.output, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        # 首次运行：目标文件还不存在（新家目录的常见情形）——不要崩在 FileNotFoundError 上
        content = ""
    new_content = replace_section(content, new_section)
    if new_content == content:
        print(f"{args.output}: no change ({len(skills)} skills)")
        return

    if args.dry_run:
        import difflib
        diff = difflib.unified_diff(
            content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"{args.output} (current)",
            tofile=f"{args.output} (new)",
            n=2,
        )
        sys.stdout.writelines(diff)
        print(f"\n[{len(skills)} skills, write skipped (dry-run)]")
        return

    backup = args.output + ".bak"
    if os.path.isfile(args.output):
        shutil.copy2(args.output, backup)
        print(f"{args.output}: updated ({len(skills)} skills), backup at {backup}")
    else:
        print(f"{args.output}: created ({len(skills)} skills)，目标原本不存在故无备份")
    with open(args.output, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
