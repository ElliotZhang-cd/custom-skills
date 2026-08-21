#!/usr/bin/env python3
"""check_distribution.py - 自建 skill 分发对账（双平台，仅标准库）

真相源 = 本仓库(clone)根下含 SKILL.md 的目录
       + maintaining-llm-wiki（当 LLMWiki 仓库可探测到时，第二源）
检查面:
  POSIX home:   ~/.agents/skills, ~/.claude/skills        （符号链接面）
  Windows home: ~/.workbuddy/skills, ~/.trae-cn/skills    （robocopy 拷贝面；
                 WSL 下经 /mnt/c/Users/* 自动探测，故任一端跑都能审四面）
判定:
  MISSING = 应分发但目标缺失
  EXTRA   = 带管理标记(.custom-src)的拷贝、或指向自建仓库的符号链接，
            但已不在真相源中（改名/删除残留的僵尸副本）
  BROKEN  = 死符号链接
第三方 skill 无管理标记，永不误报 EXTRA。默认只报告不删除；有缺口退出码 1。
"""
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARKER = ".custom-src"
MLLW = "maintaining-llm-wiki"
SKIP_WIN_USERS = {"All Users", "Default", "Default User", "Public"}


def mllw_source_exists():
    cands = [Path.home() / "Documents" / "LLMWiki" / "skills" / MLLW]
    mnt = Path("/mnt/c/Users")
    if mnt.is_dir():
        cands += [u / "Documents" / "LLMWiki" / "skills" / MLLW
                  for u in mnt.iterdir() if u.is_dir() and u.name not in SKIP_WIN_USERS]
    return any((c / "SKILL.md").is_file() for c in cands)


def truth_set():
    names = {d.name for d in REPO.iterdir()
             if d.is_dir() and (d / "SKILL.md").is_file()}
    if mllw_source_exists():
        names.add(MLLW)
    return names


def win_homes():
    if os.name == "nt":
        return [Path.home()]
    mnt = Path("/mnt/c/Users")
    if not mnt.is_dir():
        return []
    return [p for p in sorted(mnt.iterdir())
            if p.is_dir() and p.name not in SKIP_WIN_USERS]


def surfaces():
    home = Path.home()
    out = []
    if os.name == "posix":
        # 符号链接面是 WSL 侧机制；Windows 原生 %USERPROFILE%\.agents 是
        # skills CLI 的第三方安装位，不归本体系管，不审计
        out += [("~/.agents/skills", home / ".agents" / "skills"),
                ("~/.claude/skills", home / ".claude" / "skills")]
    for wh in win_homes():
        out.append((f"[win:{wh.name}] .workbuddy/skills", wh / ".workbuddy" / "skills"))
        out.append((f"[win:{wh.name}] .trae-cn/skills", wh / ".trae-cn" / "skills"))
    return out


def is_managed(entry):
    """管理标记 = bat 写入的 .custom-src，或指向自建仓库/LLMWiki 的符号链接"""
    if (entry / MARKER).is_file():
        return True
    if entry.is_symlink():
        try:
            real = entry.resolve()
        except OSError:
            return False
        custom = Path.home() / "custom-skills"
        try:
            real.relative_to(custom)
            return True
        except ValueError:
            pass
        return "LLMWiki/skills" in real.as_posix()
    return False


def audit(label, path, expected):
    if not path.is_dir():
        print(f"  [skip] {label} （本机无此面）")
        return False
    present, managed, broken = set(), set(), []
    for e in sorted(path.iterdir()):
        if e.is_symlink() and not e.exists():
            broken.append(e.name)
            continue
        if e.is_dir() and (e / "SKILL.md").is_file():
            present.add(e.name)
            if is_managed(e):
                managed.add(e.name)
    missing = sorted(expected - present)
    extra = sorted(managed - expected)
    if not (missing or extra or broken):
        print(f"  [OK]   {label}  对齐（自建 {len(present & expected)}/{len(expected)}）")
        return False
    if missing:
        print(f"  [MISS] {label}  缺失: {', '.join(missing)}")
    if extra:
        print(f"  [EXTRA]{label}  僵尸: {', '.join(extra)} （源已改名/删除，确认后手动删）")
    if broken:
        print(f"  [BRK ] {label}  死链: {', '.join(broken)}")
    return True


def main():
    expected = truth_set()
    print(f"[audit] 真相源 {len(expected)} 个: {', '.join(sorted(expected))}")
    bad = False
    for label, path in surfaces():
        bad |= audit(label, path, expected)
    if bad:
        print("[audit] 存在缺口：MISSING 跑对应端同步脚本补齐；EXTRA/BROKEN 确认后清理。")
        sys.exit(1)
    print("[audit] 全部分发面对齐。")


if __name__ == "__main__":
    main()
