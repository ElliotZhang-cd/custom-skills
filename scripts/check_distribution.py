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
  STALE    = 该面 expected 的**链接类**来源（自建 / 第二个来源 / 面已声明 thirdparty 且非存储面的
             第三方）在本面存在同名 SKILL.md 条目，但它不是指向该来源权威位置的链接（真实目录
             或外来链接）——即本体系 junction/符号链接被工具自建的真实副本顶掉了。两点例外：
             manual 池永不参与（按定义就是真实副本）；存储面（role=storage）是第三方真实目录的
             所在地，其第三方也不参与。只在 role 为 junction/link/storage（或未声明 role）的面启用。
  WARN(面) = 面目录不存在（本机无此面）：只打 [WARN]，但该面 required: true 时计入退出码 1。
配置自检 = 分发清单字段缺失/拼错、目标 id 不在 LEDGER_TOKENS、账本「所在目标」列含未声明的
              token —— 一律明确报错并退出码 1，不再静默剔除或静默降级（见 specs/syncing-skills R5）。
未登记目标 = 本机家目录下非空、含 SKILL.md、却不在分发清单里的技能目录 —— 只打 [NEW?] 提醒，
              不影响退出码（空目录不报）。这是「工具在用、体系不知道」类事故的防线（R4）。
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


def thirdparty_set(home=None):
    """第三方 expected = 该**平台**的 skills CLI 锁文件的 skills key 集；读不到则空（不假装对账）。

    npx 是仓库层、按平台各持一份存储面与锁（见 docs/adr/0001/0004），所以池必须按被审面所在
    平台的 home 取——否则在 WSL 上审计 win 面时会拿 WSL 的锁去要求 Windows 的面。"""
    lock = (home or Path.home()) / ".agents" / ".skill-lock.json"
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

VALID_PLATFORM = {"win", "posix"}
VALID_EXPECT = {"selfbuilt", "mllw", "thirdparty", "manual"}
VALID_ROLE = {"junction", "link", "storage"}
SURFACE_KEYS = {"id", "platform", "relpath", "expect", "role", "required", "note"}


def ledger_faces():
    """账本第 5 列（所在目标）的原样取值 → 行号列表。用于校验 token 是否已声明。"""
    if not LEDGER.is_file():
        return {}
    out = {}
    try:
        text = LEDGER.read_text(encoding="utf-8")
    except OSError:
        return {}
    for n, line in enumerate(text.splitlines(), 1):
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or cells[0] in ("名字", ""):
            continue
        if all(set(c) <= {"-", ":", " "} for c in cells):
            continue   # markdown 分隔行 |---|---|
        out.setdefault(cells[4], []).append(n)
    return out


def validate_config(surfaces):
    """声明自检（R5）：字段缺失/拼错一律报错，不静默降级。

    三类历史静默失败：platform 漏写 → Windows 端静默剔除该目标（连 [skip] 都不打）；
    expect 键名或值拼错 → 该目标全部条目降 UNKNOWN；目标 id 不在 LEDGER_TOKENS →
    该目标的 manual 池恒为空、账本里的手工技能一起失踪。"""
    errors = []
    tokens = set(LEDGER_TOKENS.values())
    seen_ids = set()
    for i, s in enumerate(surfaces, 1):
        where = f"surfaces[{i}]"
        if not isinstance(s, dict):
            errors.append(f"{where} 不是对象")
            continue
        sid = s.get("id")
        if sid:
            where = f"surfaces[{i}] (id={sid})"
        unknown = sorted(set(s) - SURFACE_KEYS)
        if unknown:
            errors.append(f"{where} 含未知字段: {', '.join(unknown)}"
                          f"（合法字段: {', '.join(sorted(SURFACE_KEYS))}）")
        if not isinstance(sid, str) or not sid:
            errors.append(f"{where} 缺少 id")
        elif not all(c.islower() or c.isdigit() or c == "-" for c in sid):
            errors.append(f"{where} id 只能用小写字母/数字/连字符: {sid!r}")
        elif sid in seen_ids:
            errors.append(f"{where} id 与其他条目重复")
        else:
            seen_ids.add(sid)
        if s.get("platform") not in VALID_PLATFORM:
            errors.append(f"{where} platform 必须是 win 或 posix（当前 {s.get('platform')!r}）；"
                          f"漏写会让该目标在 Windows 端被静默剔除")
        rel = s.get("relpath")
        if not isinstance(rel, list) or not rel or not all(
                isinstance(x, str) and x for x in rel):
            errors.append(f"{where} relpath 必须是非空字符串数组")
        if "expect" not in s:
            errors.append(f"{where} 缺少 expect（键名拼错会静默把该目标全部降为「多余」）")
        else:
            exp = s.get("expect")
            if not isinstance(exp, list):
                errors.append(f"{where} expect 必须是数组")
            else:
                bad = sorted(set(exp) - VALID_EXPECT)
                if bad:
                    errors.append(f"{where} expect 含非法来源: {', '.join(bad)}"
                                  f"（合法: {', '.join(sorted(VALID_EXPECT))}）")
                if "manual" in exp and sid not in LEDGER_TOKENS:
                    errors.append(f"{where} 声明了 manual 但 id 不在 LEDGER_TOKENS，"
                                  f"该目标的 manual 池会恒为空")
        if s.get("role") not in VALID_ROLE:
            errors.append(f"{where} role 必须是 junction / link / storage"
                          f"（当前 {s.get('role')!r}）")
        if "required" in s and not isinstance(s["required"], bool):
            errors.append(f"{where} required 必须是布尔（当前 {s['required']!r}）")
    for face, lines in sorted(ledger_faces().items()):
        for part in [p.strip().lower() for p in face.split("+")]:
            if part and part not in tokens:
                errors.append(f"账本第 {lines[0]} 行「{face}」含未声明的目标 token: {part!r}"
                              f"（已声明: {', '.join(sorted(tokens))}）")
    return errors


DISCOVER_MAX_DEPTH = 4
DISCOVER_SKIP = {"node_modules", ".git", "__pycache__", ".vscode-server",
                 ".cargo", ".rustup", ".venv", "venv"}


def _same_path(a, b):
    try:
        return a.resolve() == b.resolve()
    except OSError:
        return a == b


def discover_skill_dirs(declared, root=None):
    """本机家目录下「非空、含 SKILL.md、却不在分发清单里」的技能目录（R4）。

    这是 09-03（ZCode 冻结快照）与 10-16（DSH 未登记）两次「工具在用、体系不知道」
    事故的防线。空目录不报——2026-08-04 的历史清理留下过 58 个空壳。"""
    base = Path(root) if root else Path.home()
    base_depth = len(base.parts)
    found = []
    for dirpath, dirnames, _ in os.walk(base, followlinks=False):
        cur = Path(dirpath)
        if len(cur.parts) - base_depth >= DISCOVER_MAX_DEPTH:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames
                       if d not in DISCOVER_SKIP and not (cur / d).is_symlink()]
        if cur.name != "skills":
            continue
        if any(_same_path(cur, d) for d in declared):
            continue
        try:
            names = sorted(e.name for e in cur.iterdir()
                           if e.is_dir() and (e / "SKILL.md").is_file())
        except OSError:
            continue
        if names:
            found.append((cur, names))
    return found


def mllw_source_dirs():
    """第二个来源自身的目录（它是来源、不是分发目标，发现机制应排除，避免自报）。"""
    cands = [Path.home() / "Documents" / "LLMWiki" / "skills"]
    mnt = Path("/mnt/c/Users")
    if mnt.is_dir():
        cands += [u / "Documents" / "LLMWiki" / "skills"
                  for u in mnt.iterdir() if u.is_dir() and u.name not in SKIP_WIN_USERS]
    return [c for c in cands if (c / MLLW).is_dir()]


def report_undeclared(declared):
    """[NEW?] 提醒：未登记的非空技能目录。只提醒，不改退出码。"""
    for path, names in discover_skill_dirs(declared):
        shown = ", ".join(names[:12])
        if len(names) > 12:
            shown += f" …(+{len(names) - 12})"
        print(f"  [NEW?] {path}  未登记的非空技能目录: {len(names)} 项（{shown}）"
              f"—— 属提醒、不影响退出码；在用则登记进分发清单，不用则清理")


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
        if all(set(c) <= {"-", ":", " "} for c in cells):
            continue   # markdown 分隔行 |---|---|
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
                        "role": role, "required": required, "home": home})
        else:
            for wh in win_homes():
                out.append({"id": sid, "label": f"[win:{wh.name}] " + "/".join(rel),
                            "path": wh.joinpath(*rel), "expect": expect,
                            "role": role, "required": required, "home": wh})
    return out


def resolve_surface_paths(s):
    """面在本机的绝对路径候选：posix 面取本机 home，win 面取 win_homes()"""
    rel = [x for x in s.get("relpath", []) if x]
    if not rel:
        return []
    if s.get("platform", "posix") == "posix":
        return [Path.home().joinpath(*rel)]
    return [wh.joinpath(*rel) for wh in win_homes()]


_MANAGED_ROOTS = None


def managed_roots():
    """本体系管理根（is_managed 的判据来源）。

    本机 clone（REPO）之外还要认 WSL 经 /mnt/c 看到的 Windows clone：WSL 审计 win 面时
    面里的 junction 被 drvfs 暴露为符号链接，目标是 /mnt/c/Users/<u>/custom-skills/...，
    而 Path.home() 在 WSL 是 /home/<u>——只认 home 会把每个 Windows junction 误判成
    「外来真实副本」，STALE 就会全线误报。"""
    global _MANAGED_ROOTS
    if _MANAGED_ROOTS is None:
        roots = [REPO, Path.home() / "custom-skills"]
        mnt = Path("/mnt/c/Users")
        if mnt.is_dir():
            roots += [u / "custom-skills" for u in mnt.iterdir()
                      if u.is_dir() and u.name not in SKIP_WIN_USERS]
        _MANAGED_ROOTS = roots
    return _MANAGED_ROOTS


def is_managed(entry):
    """管理标记 = bat 写入的 .custom-src，或指向自建仓库/LLMWiki 的符号链接或 junction"""
    if (entry / MARKER).is_file():
        return True

    def under_managed(real):
        posix = real.as_posix().replace("\\", "/")
        if "LLMWiki/skills" in posix:
            return True
        for root in managed_roots():
            try:
                real.relative_to(root)
                return True
            except ValueError:
                continue
        # 兜底：Windows 盘符形式的目标（C:/Users/<u>/custom-skills/...）转不成 /mnt 路径
        return "/custom-skills/" in posix

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
    # STALE：该面 expected 的链接类来源（自建 / 第二个来源 / 已声明 thirdparty 的第三方）在本面
    # 存在同名 SKILL.md 条目，但它不是指向该来源权威位置的链接 → 链接被工具自建副本顶掉。
    # manual 池永不参与（它按定义就是真实副本）；thirdparty 是否算链接类，由该面 expect 决定
    # ——声明了 thirdparty 就表示「第三方在本面应是链接（指向 npx 的仓库层）」。
    # 只对 role in junction/link/storage（或未声明 role）的面启用。
    stale = []
    if role in ("", "junction", "link", "storage"):
        # 自建 / 第二个来源：必须是**指向本仓库或 LLMWiki 的链接**（is_managed 认的就是这个）
        owned = pools.get("selfbuilt", set()) | pools.get("mllw", set())
        stale_owned = (present - managed) & owned
        # 第三方（该面声明了 thirdparty 且不是存储面）：必须是**链接**——指向该平台的 npx 仓库层，
        # 因此不必落在仓库/LLMWiki 之下；登记在册的存量副本显式接纳，存储面本身就是真实目录。
        stale_tp = set()
        if role != "storage":
            for n in sorted(present & (pools.get("thirdparty", set()) - pools.get("manual", set()))):
                e = path / n
                if not (e.is_symlink() or read_link_target(e) is not None):
                    stale_tp.add(n)
        stale = sorted(stale_owned | stale_tp)
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
    errs = validate_config(surfaces)
    if errs:
        print("[audit] 错误: 分发清单/账本自检未通过（不静默降级，见 R5）:")
        for e in errs:
            print(f"  - {e}")
        return 1
    if "--retire" in argv:
        i = argv.index("--retire")
        if i + 1 >= len(argv):
            print("[retire] 用法: check_distribution.py --retire <surface-id>")
            return 2
        return retire_mode(argv[i + 1], surfaces)
    pools = {
        "selfbuilt": selfbuilt_set(),
        "mllw": {MLLW} if mllw_source_exists() else set(),
    }
    local_tp = thirdparty_set()
    conflict = sorted(pools["selfbuilt"] & local_tp)
    manual = manual_entries()
    expanded = expand_surfaces(surfaces)
    total = sum(len(v) for v in pools.values()) + len(local_tp)
    print(f"[audit] 真相源 {total} 个"
          f"（自建 {len(pools['selfbuilt'])} / mllw {len(pools['mllw'])}"
          f" / 第三方 {len(local_tp)}（本机锁））；"
          f"手动件登记表 {sum(len(v) for v in manual.values())} 条")
    if conflict:
        print(f"[CONFLICT] 命名冲突（自建 ∩ 第三方同名，必须改名）: {', '.join(conflict)}")
    bad = bool(conflict)
    req_missing = []
    for sf in expanded:
        sub = {k: (v if k in sf["expect"] else set()) for k, v in pools.items()}
        if "thirdparty" in sf["expect"]:
            sub["thirdparty"] = thirdparty_set(sf["home"])   # 按被审面所在平台取锁
        if "manual" in sf["expect"]:
            sub["manual"] = manual.get(sf["id"], set())
        if not sf["path"].is_dir() and sf["required"]:
            req_missing.append(sf["label"])
        bad |= audit(sf["label"], sf["path"], sub, sf["role"], sf["required"])
    report_undeclared([sf["path"] for sf in expanded] + mllw_source_dirs())
    if bad:
        if req_missing:
            print(f"[audit] required 面缺失 {len(req_missing)} 个（计入退出码 1）: "
                  f"{', '.join(req_missing)}")
        print("[audit] 存在缺口：MISSING 跑对应端同步脚本补齐；EXTRA/BROKEN 确认后清理；"
              "STALE 说明该面 expected 的链接类来源被复制成了真实副本（自建 / 第二个来源 / 已声明 "
              "thirdparty 的第三方），跑对应端的同步脚本恢复；UNKNOWN 为残留仅列出、不改写。")
        return 1
    print("[audit] 全部分发面对齐。（若上方有 UNK 残留，属非本体系，不影响结论）")
    return 0


if __name__ == "__main__":
    sys.exit(main())