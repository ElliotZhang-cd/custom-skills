#!/usr/bin/env python3
"""check_distribution.py - skill 分发对账（双平台，仅标准库）

真相源（expected 全集，分四类来源）:
  selfbuilt  = 本仓库(clone)根下含 SKILL.md 的目录（自建，唯一真相源）
  mllw       = maintaining-llm-wiki（LLMWiki 仓库可探测时，第二源）
  thirdparty = ~/.agents/.skill-lock.json 的 skills key 集（skills CLI 管理，读不到则空）
  manual     = manual-skills.md 账本（人工放置的第三方件，按「所在面」列逐面取名字集）
检查面: 由 scripts/distribution-targets.json 驱动（唯一配置源，白名单=封闭投影面）。
        每条含 role（junction/link/storage，v7.3 起为消费方）与 required（布尔，缺省 false）。
判定:
  MISSING  = 应分发但目标缺失
  EXTRA    = 带本体系管理标记(.custom-src / 指向自建仓库或 LLMWiki 的符号链接或 junction)
             但已不在 expected（改名/删除残留的僵尸）
  UNKNOWN  = 面内存在、既不在 expected 也无体系标记（历史残留 / 平台技能 / 第三方 Windows 残留）
             仅列出，不报错不删除
  BROKEN   = 死符号链接 / 死 junction
  CONFLICT = 同名同时出现在自建集与第三方锁文件（命名空间冲突，必须改名）
  STALE    = 来自 selfbuilt/mllw 池的 expected 名字在本面存在同名 SKILL.md 条目，但它不是指向
             本仓库/LLMWiki 的链接（真实目录或外来链接）——即本体系 junction/符号链接被工具
             自建的真实副本顶掉了。manual/thirdparty 池豁免（它们在投影面本来就是真实副本）。
             只在 role 为 junction/link/storage（或未声明 role）的面启用。
  WARN(面) = 面目录不存在（本机无此面）：只打 [WARN]，但该面 required: true 时计入退出码 1。
默认只报告不删除；MISSING/EXTRA/BROKEN/CONFLICT/STALE 与 required 面缺失有哪样退出码 1；
UNKNOWN 不影响结论。`--retire <surface-id>` 只打印该面的待清理链接清单，绝不删除（退出码 0）。
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
                 "zcode": "zcode", "dsh": "dsh"}


def manual_entries():
    """manual-skills.md 账本 → {surface_id: set(名字)}；账本缺失返回空（不假装对账）。
    「所在面」列按大小写不敏感 token 匹配 surface id（ZCode→zcode，DSH→dsh…）。"""
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
    """白名单读取失败返回 None（调用方必须报错退出，不得静默空跑）"""
    if not CONFIG.is_file():
        print(f"[audit] 错误: 缺少配置 {CONFIG}，无法对账。")
        return None
    try:
        with open(CONFIG, encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, ValueError) as e:
        print(f"[audit] 错误: 配置读取失败 {CONFIG}: {e}")
        return None
    surfaces = cfg.get("surfaces")
    if not isinstance(surfaces, list):
        print(f"[audit] 错误: 配置缺少 surfaces 数组 {CONFIG}。")
        return None
    return surfaces


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
        role = s.get("role", "")
        required = bool(s.get("required", False))
        if s.get("platform", "posix") == "posix":
            if os.name != "posix":
                continue  # Windows 原生不审计 WSL 的符号链接面
            out.append({"id": sid, "label": "~/" + "/".join(rel),
                        "path": home.joinpath(*rel), "expect": expect,
                        "role": role, "required": required})
        else:
            for wh in win_homes():
                out.append({"id": sid, "label": f"[win:{wh.name}] " + "/".join(rel),
                            "path": wh.joinpath(*rel), "expect": expect,
                            "role": role, "required": required})
    return out


def resolve_surface_paths(s):
    """面在本机的绝对路径候选：posix 面取本机 home，win 面取 win_homes()"""
    rel = [x for x in s.get("relpath", []) if x]
    if not rel:
        return []
    if s.get("platform", "posix") == "posix":
        return [Path.home().joinpath(*rel)]
    return [wh.joinpath(*rel) for wh in win_homes()]


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


def audit(label, path, pools, role="", required=False):
    if not path.is_dir():
        print(f"  [WARN] surface missing: {label}（本机无此面）")
        if required:
            return True   # 汇总行由 main() 打印
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
    # STALE：selfbuilt/mllw 池的 expected 名字在本面存在同名 SKILL.md 条目，但它不是指向
    # 本仓库/LLMWiki 的链接（真实目录 / 外来链接）→ 链接被工具自建副本顶掉。
    # manual/thirdparty 池豁免（在投影面本来就是真实副本）；只对 role in junction/link/storage
    # （或未声明 role）的面启用。
    stale = []
    if role in ("", "junction", "link", "storage"):
        link_pool = pools.get("selfbuilt", set()) | pools.get("mllw", set())
        stale = sorted((present - managed) & link_pool)
    bad = bool(missing or extra or broken or stale)
    if not bad and not unknown:
        print(f"  [OK]   {label}  对齐（{len(present & expected)}/{len(expected)}）")
        return False
    if missing:
        print(f"  [MISS] {label}  缺失: {', '.join(missing)}")
    if extra:
        print(f"  [EXTRA]{label}  僵尸: {', '.join(extra)} （源已改名/删除，确认后手动删）")
    if broken:
        print(f"  [BRK ] {label}  死链: {', '.join(broken)}")
    if stale:
        print(f"  [STALE]{label}  非链接副本: {', '.join(stale)}"
              f"（expected 自建/mllw 在本面应是 junction/符号链接；疑似被工具自建副本覆盖，见事故教训）")
    if unknown:
        print(f"  [UNK ] {label}  非本体系残留(不删，仅列出): {', '.join(unknown)}")
    return bad


def retire_mode(sid, surfaces):
    """--retire <surface-id>：只打印该面的待清理清单，绝不删除任何东西。
    未知 id → 退出码 2；正常打印 → 退出码 0。"""
    hit = [s for s in surfaces if s.get("id") == sid]
    if not hit:
        print(f"[retire] unknown surface: {sid}")
        return 2
    s = hit[0]
    print(f"[retire] surface: {sid}  (platform={s.get('platform', 'posix')}"
          f", role={s.get('role', '?')}, required={bool(s.get('required', False))}"
          f", expect={','.join(s.get('expect', []))})")
    for p in resolve_surface_paths(s):
        print(f"[retire] relpath: {p}")
        if not p.is_dir():
            print(f"[retire] surface dir absent: {p}（无需清盘）")
            continue
        ours = [e for e in sorted(p.iterdir())
                if (e.is_symlink() or read_link_target(e) is not None) and is_managed(e)]
        print("[retire] 待清理清单（本体系所有的链接；本脚本绝不删除任何东西）:")
        if ours:
            for e in ours:
                print(f"    - {e.name} -> {read_link_target(e)}")
        else:
            print("    （无本体系链接）")
        print("[retire] 提示: 手动第三方件是真实副本，属用户内容，需人工确认后删除或移出账本。")
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    surfaces = load_surfaces()
    if surfaces is None:
        return 1   # 配置不可用：不静默空跑
    if "--retire" in argv:
        i = argv.index("--retire")
        if i + 1 >= len(argv):
            print("[retire] 用法: check_distribution.py --retire <surface-id>")
            return 2
        return retire_mode(argv[i + 1], surfaces)
    pools = {
        "selfbuilt": selfbuilt_set(),
        "mllw": {MLLW} if mllw_source_exists() else set(),
        "thirdparty": thirdparty_set(),
    }
    conflict = sorted(pools["selfbuilt"] & pools["thirdparty"])
    manual = manual_entries()
    expanded = expand_surfaces(surfaces)
    total = sum(len(v) for v in pools.values())
    print(f"[audit] 真相源 {total} 个"
          f"（自建 {len(pools['selfbuilt'])} / mllw {len(pools['mllw'])}"
          f" / 第三方 {len(pools['thirdparty'])}）；"
          f"手动件账本 {sum(len(v) for v in manual.values())} 条")
    if conflict:
        print(f"[CONFLICT] 命名冲突（自建 ∩ 第三方同名，必须改名）: {', '.join(conflict)}")
    bad = bool(conflict)
    req_missing = []
    for sf in expanded:
        sub = {k: (v if k in sf["expect"] else set()) for k, v in pools.items()}
        if "manual" in sf["expect"]:
            sub["manual"] = manual.get(sf["id"], set())
        if not sf["path"].is_dir() and sf["required"]:
            req_missing.append(sf["label"])
        bad |= audit(sf["label"], sf["path"], sub, sf["role"], sf["required"])
    if bad:
        if req_missing:
            print(f"[audit] required 面缺失 {len(req_missing)} 个（计入退出码 1）: "
                  f"{', '.join(req_missing)}")
        print("[audit] 存在缺口：MISSING 跑对应端同步脚本补齐；EXTRA/BROKEN 确认后清理；"
              "STALE 说明自建/mllw 的链接被复制成了真实副本，跑 ensure_junctions.ps1 恢复；"
              "UNKNOWN 为残留仅列出、不改写。")
        return 1
    print("[audit] 全部分发面对齐。（若上方有 UNK 残留，属非本体系，不影响结论）")
    return 0


if __name__ == "__main__":
    sys.exit(main())