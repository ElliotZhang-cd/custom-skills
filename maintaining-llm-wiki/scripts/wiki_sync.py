#!/usr/bin/env python3
"""派生数据同步入口：sync_sources → rebuild_tags。

用法: python3 wiki_sync.py [wiki_root]
  wiki_root 可选，默认平台自识别（见 wiki_paths.py）

退出码 = 各子脚本退出码的按位或（0 = 全部成功）。
"""
import os, sys, subprocess
from wiki_paths import default_wiki_root

W = sys.argv[1] if len(sys.argv) > 1 else default_wiki_root()
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))

def run(name):
    r = subprocess.run([sys.executable, f"{SKILL_DIR}/{name}.py", W], capture_output=True, text=True)
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.returncode != 0 and r.stderr.strip():
        print(f"[!] {name}: {r.stderr.strip()}", file=sys.stderr)
    return r.returncode

rc = run('sync_sources') | run('rebuild_tags')
sys.exit(rc)
