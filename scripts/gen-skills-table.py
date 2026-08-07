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
"""
import argparse
import os
import re
import shutil
import sys
import yaml

SKILLS_SYSTEM_RE = re.compile(r"<skills_system[^>]*>.*?</skills_system>", re.DOTALL)

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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print diff without writing")
    parser.add_argument("--output", default=os.path.expanduser("~/AGENTS.md"))
    parser.add_argument("--agents-dir", default=os.path.expanduser("~/.agents/skills"))
    args = parser.parse_args()

    skills = collect_skills(args.agents_dir)
    if not skills:
        print(f"error: no skills found in {args.agents_dir}", file=sys.stderr)
        sys.exit(1)

    new_section = build_section(skills)

    with open(args.output, "r", encoding="utf-8") as f:
        content = f.read()
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
    shutil.copy2(args.output, backup)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"{args.output}: updated ({len(skills)} skills), backup at {backup}")


if __name__ == "__main__":
    main()
