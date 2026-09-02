#!/usr/bin/env python3
"""check_distribution.py - skill 分发对账（双平台，仅标准库）

真相源（expected 全集，分四类来源）:
  selfbuilt  = 本仓库(clone)根下含 SKILL.md 的目录（自建，唯一真相源）
  mllw       = maintaining-llm-wiki（LLMWiki 仓库可探测时，第二源）
  thirdparty = ~/.agents/.skill-lock.json 的 skills key 集（skills CLI 管理，读不到则空）
  manual     = manual-skills.md 账本（人工放置的第三方件，按「所在面」列逐面取名字集）
检查面: 由 scripts/distribution-targets.json 驱动（唯一配置源，白名单=封闭投影面）
判定:
  MISSING  = 应分发但目标缺失
  EXTRA    = 带本体系管理标记(.custom-src / 指向自建仓库或 LLMWiki 的符号链接或 junction)
             但已不在 expected（改名/删除残留的僵尸）
  UNKNOWN  = 面内存在、既不在 expected 也无体系标记（历史残留 / 平台技能 / 第三方 Windows 残留）
             仅列出，不报错不删除
  BROKEN   = 死符号链接 / 死 junction
  CONFLICT = 同名同时出现在自建集与第三方锁文件（命名空间冲突，必须改名）
默认只报告不删除；MISSING/EXTRA/BROKEN/CONFLICT 有哪样退出码 1；UNKNOWN 不影响结论。
"""
import os
import sys
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARKER = ".custom-src"
MLLW = "maintaining-llm-wiki"
LEDGER = REPO / "manual-skills.md"
SKIP_WIN_USERS = {"All Users", "Default", "Default User", "Public"}
CONFIG = REPO / "scripts" / "distribution-targets.json"


def mllw_source_exists():
    cands = [Path.home() / "Documents" / "LLMWiki" / "skills" / MLLW]
    mnt = Path("/mnt/c/Users")
    if mnt.is_dir():
        cands += [u / "Documents" / "LLMWiki" / "skills" / MLLW
                  for u in mnt.iterdir() if u.is_dir() and u.name not in SKIP_WIN_USERS]
    return any((c / "SKILL.md").is_file() for c in cands)


def selfbuilt_set():
    return {d.name for d in REPO.iterdir()
            if d.is_dir() and (d / "SKILL.md").is_file()}


def thirdparty_set():
    """第三方 expected = skills CLI 锁文件的 skills key 集；读不到则空（不假装对账）"""
    lock = Path.home() / ".agents" / ".skill-lock.json"
    if not lock.is_file():
        return set()
    try:
        with open(lock, encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("skills", {}).keys())
    except (OSError, ValueError):
        return set()


LEDGER_TOKENS = {"agents": "wsl", "claude": "wsl", "workbuddy": "workbuddy",
                 "trae": "trae", "zcode": "zcode"}


def manual_entries():
    """manual-skills.md 账本 → {surface_id: set(名字)}；账本缺失返回空（不假装对账）。
    「所在面」列按大小写不敏感 token 匹配 surface id（TRAE→trae，ZCode→zcode…）。"""
    if not LEDGER.is_file():
        return {}
    out = {sid: set() for sid in LEDGER_TOKENS}
    try:
        text = LEDGER.read_text(encoding="utf-8")
    except OSError:
        return {}
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or cells[0] in ("名字", ""):
            continue
        face = cells[4].lower()
        for sid, token in LEDGER_TOKENS.items():
            if token in face:
                out[sid].add(cells[0])
    return out


def read_link_target(entry):
    """读 junction/symlink 目标；非链接返回 None。兼容 junction 的 \\??\\ 前缀。"""
    try:
        target = os.readlink(entry)
    except (OSError, ValueError):
        return None
    if os.name == "nt" and target.startswith("\\\\?\\"):
        target = target[4:]
    return target


def load_surfaces():
    if not CONFIG.is_file():
        print(f"[audit] 警告: 缺少配置 {CONFIG}，无检查面。")
        return []
    try:
        with open(CONFIG, encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, ValueError) as e:
        print(f"[audit] 警告: 配置读取失败 {CONFIG}: {e}")
        return []
    return cfg.get("surfaces", [])


def win_homes():
    if os.name == "nt":
        return [Path.home()]
    mnt = Path("/mnt/c/Users")
    if not mnt.is_dir():
        return []
    return [p for p in sorted(mnt.iterdir())
            if p.is_dir() and p.name not in SKIP_WIN_USERS]


def expand_surfaces(surfaces):
    home = Path.home()
    out = []
    for s in surfaces:
        expect = set(s.get("expect", []))
        rel = [x for x in s.get("relpath", []) if x]
        sid = s.get("id", "")
        if s.get("platform", "posix") == "posix":
            if os.name != "posix":
                continue  # Windows 原生不审计 WSL 的符号链接面
            out.append((sid, "~/" + "/".join(rel), home.joinpath(*rel), expect))
        else:
            for wh in win_homes():
                out.append((sid, f"[win:{wh.name}] " + "/".join(rel),
                            wh.joinpath(*rel), expect))
    return out


def is_managed(entry):
    """管理标记 = bat 写入的 .custom-src，或指向自建仓库/LLMWiki 的符号链接或 junction"""
    if (entry / MARKER).is_file():
        return True
    custom = Path.home() / "custom-skills"

    def under_managed(real):
        try:
            real.relative_to(custom)
            return True
        except ValueError:
            return "LLMWiki/skills" in real.as_posix()

    if entry.is_symlink():
        try:
            return under_managed(entry.resolve())
        except OSError:
            return False
    target = read_link_target(entry)  # Windows junction（is_symlink 不识别）
    if target is None:
        return False
    tp = Path(target)
    if not tp.is_absolute():
        tp = (entry.parent / tp)
    try:
        return under_managed(tp.resolve())
    except OSError:
        return False


def audit(label, path, pools):
    if not path.is_dir():
        print(f"  [skip] {label} （本机无此面）")
        return False
    expected = set().union(*pools.values())
    present, managed, broken = set(), set(), []
    for e in sorted(path.iterdir()):
        if e.is_symlink() and not e.exists():
            broken.append(e.name)
            continue
        if not e.is_symlink():
            # Windows junction：is_symlink 不识别，用 readlink 探测死链
            target = read_link_target(e)
            if target is not None and not Path(target).exists():
                broken.append(e.name)
                continue
        if e.is_dir() and (e / "SKILL.md").is_file():
            present.add(e.name)
            if is_managed(e):
                managed.add(e.name)
    missing = sorted(expected - present)
    extra = sorted(managed - expected)
    unknown = sorted(present - expected - managed)
    bad = bool(missing or extra or broken)
    if not bad and not unknown:
        print(f"  [OK]   {label}  对齐（{len(present & expected)}/{len(expected)}）")
        return False
    if missing:
        print(f"  [MISS] {label}  缺失: {', '.join(missing)}")
    if extra:
        print(f"  [EXTRA]{label}  僵尸: {', '.join(extra)} （源已改名/删除，确认后手动删）")
    if broken:
        print(f"  [BRK ] {label}  死链: {', '.join(broken)}")
    if unknown:
        print(f"  [UNK ] {label}  非本体系残留(不删，仅列出): {', '.join(unknown)}")
    return bad


def main():
    pools = {
        "selfbuilt": selfbuilt_set(),
        "mllw": {MLLW} if mllw_source_exists() else set(),
        "thirdparty": thirdparty_set(),
    }
    conflict = sorted(pools["selfbuilt"] & pools["thirdparty"])
    manual = manual_entries()
    surfaces = expand_surfaces(load_surfaces())
    total = sum(len(v) for v in pools.values())
    print(f"[audit] 真相源 {total} 个"
          f"（自建 {len(pools['selfbuilt'])} / mllw {len(pools['mllw'])}"
          f" / 第三方 {len(pools['thirdparty'])}）；"
          f"手动件账本 {sum(len(v) for v in manual.values())} 条")
    if conflict:
        print(f"[CONFLICT] 命名冲突（自建 ∩ 第三方同名，必须改名）: {', '.join(conflict)}")
    bad = bool(conflict)
    for sid, label, path, expect in surfaces:
        sub = {k: (v if k in expect else set()) for k, v in pools.items()}
        if "manual" in expect:
            sub["manual"] = manual.get(sid, set())
        bad |= audit(label, path, sub)
    if bad:
        print("[audit] 存在缺口：MISSING 跑对应端同步脚本补齐；EXTRA/BROKEN 确认后清理；"
              "UNKNOWN 为残留仅列出、不改写。")
        sys.exit(1)
    print("[audit] 全部分发面对齐。（若上方有 UNK 残留，属非本体系，不影响结论）")


if __name__ == "__main__":
    main()