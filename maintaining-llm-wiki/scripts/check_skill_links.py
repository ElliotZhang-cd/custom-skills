#!/usr/bin/env python3
"""检查各平台 skill 入口是否指向同一个 maintaining-llm-wiki。

默认检查：
- WSL: ~/.agents/skills/maintaining-llm-wiki
- WSL: ~/.claude/skills/maintaining-llm-wiki
- Windows: %USERPROFILE%\\.workbuddy\\skills\\maintaining-llm-wiki
- Windows: %USERPROFILE%\\.trae-cn\\skills\\maintaining-llm-wiki

用法: python3 check_skill_links.py [wiki_root]
  wiki_root 可选，默认平台自识别（见 wiki_paths.py）
"""
import os, sys, pathlib
from wiki_paths import default_wiki_root

W = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else default_wiki_root())
SKILL_NAME = "maintaining-llm-wiki"
TARGET = W / "skills" / SKILL_NAME

errors, infos = [], []

def check_path(label, path):
    p = pathlib.Path(path)
    if not p.exists():
        infos.append(f"[skill-link] {label} 不存在：{p}")
        return
    try:
        resolved = p.resolve()
    except Exception as e:
        errors.append(f"[skill-link] {label} 无法解析：{p} ({e})")
        return
    if TARGET.exists() and resolved != TARGET.resolve():
        infos.append(f"[skill-link] {label} 指向 {resolved}，当前期望 {TARGET.resolve()}（若尚未迁移可忽略）")
    else:
        infos.append(f"[skill-link] {label} OK -> {resolved}")

if os.name == "nt":
    userprofile = os.environ.get("USERPROFILE", "")
    check_path("WorkBuddy", os.path.join(userprofile, ".workbuddy", "skills", SKILL_NAME))
    check_path("Trae", os.path.join(userprofile, ".trae-cn", "skills", SKILL_NAME))
else:
    home = pathlib.Path.home()
    check_path("WSL .agents", home / ".agents" / "skills" / SKILL_NAME)
    check_path("WSL .claude", home / ".claude" / "skills" / SKILL_NAME)

for e in errors:
    print(f"[E] {e}")
for i in infos:
    print(f"[I] {i}")
print(f"\n== {len(errors)} ERROR / {len(infos)} INFO ==")
sys.exit(1 if errors else 0)
