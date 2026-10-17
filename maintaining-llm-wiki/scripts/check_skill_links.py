#!/usr/bin/env python3
"""检查各平台 skill 入口是否指向同一个 maintaining-llm-wiki。

检查面来源 = custom-skills 白名单 `~/custom-skills/scripts/distribution-targets.json`
（唯一配置源，与补链脚本 / 对账脚本共用；v7.4 起本脚本不再硬编码面清单）：
- Windows 主机取 `platform == "win"` 的面（workbuddy / zcode / dsh …）
- POSIX 主机取 `platform == "posix"` 的面（agents 存储面 / claude 链接面）

逐面检查 `<用户主目录>/<relpath>/maintaining-llm-wiki` 是否指向
`~/custom-skills/maintaining-llm-wiki`——**本 skill 的家**（2026-10-17 起它从 LLMWiki 仓库
迁进 custom-skills，见 wiki 的 log）。判据沿用原脚本：解析后路径 != 期望目标报 INFO，
条目不存在同样报 INFO。白名单读不到 / 解析失败 → 明确报错并 exit 1，不做静默降级
（本脚本是技能入口检查，读不到面清单时「全绿」是假信号）。

项目级入口已退役：技能迁走后本仓库不再含 `skills/`，`<wiki>/.claude/skills` 与
`.agent/skills` 两个项目级入口随之删除——技能现在只由 skill 分发体系装到各**用户级面**。

用法: python3 check_skill_links.py
"""
import json, os, sys, pathlib

SKILL_NAME = "maintaining-llm-wiki"
# 家 = custom-skills 仓库根下的同名目录（不再是 wiki 仓库里的 skills/）
TARGET = pathlib.Path.home() / "custom-skills" / SKILL_NAME
WHITELIST = pathlib.Path.home() / "custom-skills" / "scripts" / "distribution-targets.json"
PLATFORM = "win" if os.name == "nt" else "posix"

# 仅用于显示大小写，不是面清单：未知 id 回退为 `~/<relpath>`，新增面无须改这里。
DISPLAY = {"workbuddy": "WorkBuddy", "zcode": "ZCode", "dsh": "DSH"}

errors, infos = [], []


def load_surfaces():
    """读白名单并筛出本平台的面；返回 (面列表, 白名单是否成功读到)。

    任何读取/解析问题都计入 errors（不静默、不降级）。
    """
    try:
        data = json.loads(WHITELIST.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"[skill-link] 白名单不存在：{WHITELIST}（本脚本白名单驱动，无法降级）")
        return [], False
    except (OSError, ValueError) as e:
        errors.append(f"[skill-link] 白名单读取/解析失败：{WHITELIST}（{e}）")
        return [], False
    surfaces = data.get("surfaces") if isinstance(data, dict) else None
    if not isinstance(surfaces, list):
        errors.append(f"[skill-link] 白名单缺 surfaces 列表：{WHITELIST}")
        return [], False
    picked = []
    for s in surfaces:
        if not isinstance(s, dict):
            errors.append(f"[skill-link] 白名单含非对象条目，已跳过：{s!r}")
            continue
        if str(s.get("platform", "posix")) != PLATFORM:  # platform 缺省视为 posix（同 check_distribution.py）
            continue
        rel = s.get("relpath")
        if not isinstance(rel, list) or not rel:
            errors.append(f"[skill-link] 白名单条目 {s.get('id')!r} 的 relpath 非法，已跳过")
            continue
        picked.append(s)
    if not picked:
        errors.append(f"[skill-link] 白名单里没有 platform == {PLATFORM!r} 的面：{WHITELIST}")
    return picked, True


def label_of(surface):
    sid = str(surface.get("id") or "?")
    if sid in DISPLAY:
        return DISPLAY[sid]
    return "~/" + "/".join(str(x) for x in surface["relpath"])


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


surfaces, whitelist_ok = load_surfaces()
if whitelist_ok:
    infos.append(f"[skill-link] 面来源：{WHITELIST}（platform={PLATFORM}，{len(surfaces)} 面）")
for s in surfaces:
    home_path = pathlib.Path.home().joinpath(*[str(x) for x in s["relpath"]])
    check_path(label_of(s), home_path / SKILL_NAME)

for e in errors:
    print(f"[E] {e}")
for i in infos:
    print(f"[I] {i}")
print(f"\n== {len(errors)} ERROR / {len(infos)} INFO ==")
sys.exit(1 if errors else 0)
