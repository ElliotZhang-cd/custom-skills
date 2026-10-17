#!/usr/bin/env python3
"""低频 git 健康检查。

用法: python3 check_repo.py [wiki_root]
  wiki_root 可选，默认平台自识别（见 wiki_paths.py）
"""
import os, sys, subprocess, pathlib
from wiki_paths import default_wiki_root

W = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else default_wiki_root())
errors, infos = [], []

def run_git(args):
    r = subprocess.run(["git"] + args, cwd=W, capture_output=True, text=True)
    return r

# 1. fsck
r = run_git(["fsck", "--no-dangling"])
if r.returncode != 0:
    errors.append(f"[git] fsck 发现问题：{r.stdout.strip() or r.stderr.strip()}")

# 2. 未提交变更
r = run_git(["status", "--porcelain"])
if r.returncode == 0 and r.stdout.strip():
    dirty = [l.strip() for l in r.stdout.strip().splitlines() if l.strip()]
    infos.append(f"[git] 工作区未提交：{len(dirty)} 个文件")

# 3. 落后 remote（仅提示，不自动 fetch）
r = run_git(["rev-list", "--count", "HEAD..@{u}"])
if r.returncode == 0 and r.stdout.strip().isdigit() and int(r.stdout.strip()) > 0:
    infos.append(f"[git] 当前落后 remote {r.stdout.strip()} 个提交")

for e in errors:
    print(f"[E] {e}")
for i in infos:
    print(f"[I] {i}")
print(f"\n== {len(errors)} ERROR / {len(infos)} INFO ==")
sys.exit(1 if errors else 0)
