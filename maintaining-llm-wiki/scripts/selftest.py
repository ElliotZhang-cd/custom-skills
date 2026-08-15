#!/usr/bin/env python3
"""最小 smoke test：确保核心脚本可导入/编译、路径解析可用。

用法: python3 selftest.py
"""
import os, sys, py_compile, pathlib

HERE = pathlib.Path(__file__).resolve().parent
SCRIPTS = [
    "wiki_paths.py",
    "sync_sources.py",
    "rebuild_tags.py",
    "gen_index_tables.py",
    "lint_check.py",
    "check_skill_links.py",
    "check_secrets.py",
    "check_repo.py",
    "update_readme.py",
]

errors = []
for name in SCRIPTS:
    path = HERE / name
    if not path.exists():
        errors.append(f"[selftest] 缺少脚本：{name}")
        continue
    try:
        py_compile.compile(str(path), doraise=True)
    except Exception as e:
        errors.append(f"[selftest] 编译失败：{name}: {e}")

# 路径解析
sys.path.insert(0, str(HERE))
try:
    from wiki_paths import default_wiki_root
    root = default_wiki_root()
    if not root:
        errors.append("[selftest] default_wiki_root() 返回空")
except Exception as e:
    errors.append(f"[selftest] wiki_paths 导入失败：{e}")

for e in errors:
    print(f"[E] {e}")
print(f"\n== {len(errors)} ERROR ==")
sys.exit(1 if errors else 0)
