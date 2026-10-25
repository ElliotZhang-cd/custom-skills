#!/usr/bin/env bash
# ============================================================
# sync-wsl.sh - WSL 侧同步 custom-skills（GitHub 为唯一真相源）
# 架构: GitHub repo = 唯一真相源; WSL ~/custom-skills 与 Windows 均为 clone + 编辑入口
# 用法: bash ~/custom-skills/scripts/sync-wsl.sh [--strict]   （或 ~/.local/bin 软链后直接跑）
# 流程: 脏树守卫(含 untracked) -> git pull --ff-only -> 按分发清单同步 POSIX 面的链接
#       (清失效链 + 建链) -> 刷新 AGENTS.md 技能表 -> 分发对账 -> 锁文件快照备份
# --strict: 对账非 0 时以退出码 1 结束（供计划任务/钩子自动化用）；
#       默认只记录不中断（历史行为）。无论哪种模式，都以对账输出为准。
# 面清单: scripts/distribution-targets.json 里 platform=posix 的面（唯一声明处）
#   role=storage 的面直指源目录；role=link 的面用相对路径指向第一个 storage 面
#   expect 决定每个面该有哪些来源（selfbuilt / thirdparty / manual）：
#   本脚本建 selfbuilt / thirdparty 的链接——第三方指向 npx 的**仓库层**
#   （存储面同名条目），名字以 CLI 锁文件为权威；manual 是人工放置的真实副本，
#   不由本脚本增删（真实副本一律只点名、不替换）。
#   （mllw 类别已于 2026-10-25 退役——maintaining-llm-wiki 已并入自建，见 docs/adr/0005）。
# 注意: 自建 skill 绝不进入 skills CLI 锁文件; 编辑只发生在任一 clone, push 后他端 pull
# ============================================================
set -u

STRICT=0
[ "${1:-}" = "--strict" ] && STRICT=1

REPO="$HOME/custom-skills"
CONFIG="$REPO/scripts/distribution-targets.json"
TABLE_SCRIPT="$REPO/scripts/gen-skills-table.py"
AUDIT_SCRIPT="$REPO/scripts/check_distribution.py"
LOCK="$HOME/.agents/.skill-lock.json"
LOCK_BAK="$REPO/scripts/.backup/skill-lock.json"
ORIGIN="origin"
BRANCH="master"

fail() {
    echo "[sync] 错误: $*" >&2
    exit 1
}

note() {
    echo "  [note] $*"
}

[ -d "$REPO/.git" ] || fail "仓库不存在: $REPO"
[ -f "$CONFIG" ] || fail "缺少分发清单: $CONFIG"
cd "$REPO" || fail "无法进入 $REPO"

# ---- [1/6] 脏树守卫（含 untracked，与 sync-windows.bat 对齐） ----
if [ -n "$(git status --porcelain)" ]; then
    echo "[sync] 错误: 仓库有本地未提交修改，--ff-only pull 会被拒绝:"
    git status --short
    echo "[sync] 处理: 改动是你要的则先 commit + push；否则 git checkout -- . 丢弃"
    exit 1
fi

# ---- [2/6] pull ----
git pull --ff-only "$ORIGIN" "$BRANCH" || fail "pull 失败（已排除本地修改干扰），请检查网络/代理"
echo "[sync] 当前版本: $(git log -1 --oneline)"

# ---- 读清单：platform=posix 的面 → id / role / expect / 目录 ----
FACE_DUMP="$(python3 - "$CONFIG" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as f:
    cfg = json.load(f)
for s in cfg.get("surfaces", []):
    if s.get("platform", "posix") == "posix":
        print("\t".join([s.get("id", ""), s.get("role", ""),
                         " ".join(s.get("expect", [])),
                         "/".join(s.get("relpath", []))]))
PY
)" || fail "分发清单解析失败（需要 python3）"
[ -n "$FACE_DUMP" ] || fail "清单里没有 platform=posix 的面: $CONFIG"

declare -A FACE_DIR=() FACE_ROLE=() FACE_EXPECT=()
STORAGE_DIR=""
while IFS=$'\t' read -r id role exp rel; do
    [ -n "${id:-}" ] || continue
    [ -n "${rel:-}" ] || fail "面 $id 的 relpath 为空"
    FACE_DIR["$id"]="$HOME/$rel"
    FACE_ROLE["$id"]="$role"
    FACE_EXPECT["$id"]="$exp"
    if [ "${role:-}" = "storage" ] && [ -z "$STORAGE_DIR" ]; then
        STORAGE_DIR="$HOME/$rel"
    fi
done <<<"$FACE_DUMP"
[ "${#FACE_DIR[@]}" -gt 0 ] || fail "清单里没有可用的 posix 面"

# ---- 源集合：仓库根下含 SKILL.md 的目录（仓库即列表；mllw 已并入自建，见 docs/adr/0005） ----
declare -A SRC=()
declare -A SRC_POOL=()   # 名字 -> 归属池（当前只有 selfbuilt）：门控按**池**判，不按名字
while IFS= read -r s; do
    if [ -n "$s" ]; then
        SRC["$s"]="$REPO/$s"
        SRC_POOL["$s"]="selfbuilt"
    fi
done < <(find "$REPO" -maxdepth 2 -name SKILL.md -printf "%h\n" 2>/dev/null \
         | sed "s|$REPO/||" | sort)
[ "${#SRC[@]}" -gt 0 ] || fail "仓库里没找到任何自建 skill（根下含 SKILL.md 的目录）"

# ---- 第三方池（**仓库层**）：npx 只管存储面与锁，本脚本负责把这些条目链到各面 ----
# 名字**以 CLI 锁文件为权威**（与 check_distribution.py 的 thirdparty 池同源，绝不擅自扩面：
# 存储面里锁外的目录不链，否则会在对账里变成 [UNK]）；只链「锁里有 且 存储面里真的在」的，
# 避免造出悬空链。锁读不到 → 池为空（不假装有第三方）。
declare -A TP=()
if [ -n "$STORAGE_DIR" ] && [ -d "$STORAGE_DIR" ] && [ -f "$LOCK" ]; then
    tp_names="$(python3 -c 'import json,sys
try:
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    print("\n".join(sorted((d.get("skills") or {}).keys())))
except Exception:
    pass' "$LOCK" 2>/dev/null || true)"
    while IFS= read -r n; do
        [ -n "$n" ] || continue
        [ -n "${SRC[$n]:-}" ] && continue              # 自建另有归属
        [ -f "$STORAGE_DIR/$n/SKILL.md" ] || continue  # 真实目录且是技能
        TP["$n"]="$STORAGE_DIR/$n"
    done <<<"$tp_names"
fi

# 归属判定：只看链接自身的**字面目标**（v7.1 的教训——不要用 realpath 链式解析，
# 否则 .agents 旧链先删后，.claude 链会断在半途而漏删）。
#
# 关键：指向另一个已声明面的同名条目时，必须**跟随该基准条目的归属**再判——
# 基准层是真实目录/外来链（例如第三方的真实目录、人工放置的副本）就一律不动。
# 2026-10-17 实证：少了这一步会把第三方在 .claude 面的 20 条二级链当成本体系残留删掉。
entry_owned() {  # $1 = 指向链接的绝对路径
    local e="$1" t d rel name base bt
    [ -L "$e" ] || return 1                      # 真实目录/文件 → 不是我们的
    t="$(readlink "$e" 2>/dev/null)" || return 1
    case "$t" in
        "$REPO"/*) return 0 ;;
    esac
    name="$(basename "$e")"
    for d in "${FACE_DIR[@]}"; do
        rel="${d#"$HOME"/}"
        case "$t" in
            "$d/$name"|*"/$rel/$name")
                base="$d/$name"
                # 基准条目整个不存在（既非文件也非链接）→ 我们的残留
                if [ ! -e "$base" ] && [ ! -L "$base" ]; then
                    return 0
                fi
                # 基准条目是我们的链接 → 跟随归属；否则（真实条目/外来链）不动
                if [ -L "$base" ]; then
                    bt="$(readlink "$base" 2>/dev/null)"
                    case "$bt" in
                        "$REPO"/*) return 0 ;;
                    esac
                fi
                return 1
                ;;
        esac
    done
    return 1
}

# ---- [3/6] 同步链接（清失效链 + 建链），面与来源都来自清单 ----
echo "[sync] 清理失效链接（只看链接自身目标；非本体系链接一律保留）..."
cleaned=0
for id in "${!FACE_DIR[@]}"; do
    dir="${FACE_DIR[$id]}"
    [ -d "$dir" ] || continue
    for link in "$dir"/*; do
        [ -L "$link" ] || continue
        name="$(basename "$link")"
        if entry_owned "$link" && [ -z "${SRC[$name]:-}" ]; then
            rm "$link"
            echo "  [clean] - ${dir#"$HOME"/}/$name（源已不存在）"
            cleaned=$((cleaned + 1))
        fi
    done
done
[ "$cleaned" -eq 0 ] && echo "  （无失效链接）"

echo "[sync] 同步链接（POSIX 面: ${!FACE_DIR[*]}；源: ${#SRC[@]} 个）..."
added=0
for id in "${!FACE_DIR[@]}"; do
    dir="${FACE_DIR[$id]}"
    role="${FACE_ROLE[$id]}"
    exp=" ${FACE_EXPECT[$id]} "
    if [ ! -d "$dir" ]; then
        # 工具懒创建技能根：父目录在而技能根不在时由本脚本建（与 ensure_junctions.ps1 同款）
        parent="$(dirname "$dir")"
        if [ -d "$parent" ]; then
            mkdir -p "$dir" && echo "  [new]  面目录已建: ${dir#"$HOME"/}"
        else
            note "父目录不存在，跳过该面: $parent"
            continue
        fi
    fi
    for name in $(printf '%s\n' "${!SRC[@]}" | sort); do
        # 按**来源池**门控（不是按名字）：该名字所属的池 ∈ 本面 expect 才链
        case "$exp" in *" ${SRC_POOL[$name]} "*) ;; *) continue ;; esac
        link="$dir/$name"
        if [ -L "$link" ]; then
            # 死链必须修：`-L` 对**死链**同样为真，只看它会把它当成"已有链接"跳过，
            # 于是目标已消失的旧链接永远不被修复（2026-10-17 实证：源目录挪位后
            # 两面一直报 [BRK]，而本脚本报"新增 0"）。
            if [ -e "$link" ]; then
                continue
            fi
            rm -f "$link"
            echo "  [$id] ~ $name 死链已清，重建"
        elif [ -e "$link" ]; then
            note "非符号链接，保留原样: $link"
            continue
        fi
        if [ "$role" = "link" ]; then
            base="${STORAGE_DIR:-$REPO}"
            # 纯词法相对路径（**不解析符号链接**）：要的是"指向 storage 面同名条目"的二级链，
            # 而不是被 realpath 一路解析到仓库本体——形制见 docs/adr/0002。
            tgt="$(python3 -c 'import os, sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))' \
                   "$base/$name" "$dir" 2>/dev/null || true)"
            [ -n "$tgt" ] || tgt="${SRC[$name]}"
        else
            tgt="${SRC[$name]}"
        fi
        if ln -s "$tgt" "$link"; then
            echo "  [$id] + $name -> $(readlink "$link")"
            added=$((added + 1))
        fi
    done

    # 第三方：本面声明了 thirdparty 就该有链接（指向存储面同名条目）——npx 只管仓库层，
    # 平台层由本脚本建链；真实副本占位不删（那是用户内容），只点名，让对账去判 [STALE]。
    if [ "$role" != "storage" ]; then
        case "$exp" in *" thirdparty "*)
            for name in $(printf '%s\n' "${!TP[@]}" | sort); do
                [ -n "$name" ] || continue
                link="$dir/$name"
                if [ -L "$link" ]; then
                    if [ -e "$link" ]; then continue; fi
                    rm -f "$link"
                    echo "  [$id] ~ $name 第三方死链已清，重建"
                elif [ -e "$link" ]; then
                    note "真实副本占位（第三方在本面应为链接，确认后删掉再跑一次）: ${link#"$HOME"/}"
                    continue
                fi
                pbase="${STORAGE_DIR:-}"
                [ -n "$pbase" ] || continue
                tgt="$(python3 -c 'import os, sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))' \
                       "$pbase/$name" "$dir" 2>/dev/null || true)"
                [ -n "$tgt" ] || tgt="$pbase/$name"
                if ln -s "$tgt" "$link"; then
                    echo "  [$id] + $name -> $(readlink "$link")"
                    added=$((added + 1))
                fi
            done
            ;;
        esac
    fi
done
echo "  [sum]  新增 $added / 清理 $cleaned（第三方池 ${#TP[@]} 个，来自 ${STORAGE_DIR:-未发现存储面}）"

# ---- [4/6] 刷新 AGENTS.md 技能表 ----
table_failed=0
if [ -f "$TABLE_SCRIPT" ]; then
    python3 "$TABLE_SCRIPT" || table_failed=1
fi

# ---- [5/6] 分发对账（清单里的 posix 面 + 经 /mnt/c 看到的 win 面）----
# 默认：对账非 0 只记录、不中断（历史行为，脚本退出码仍 0）；--strict 时以退出码 1 结束。
# 无论哪种模式，结论都以对账输出为准——同步脚本的退出码与结尾话术从不是判据。
audit_failed=0
if [ -f "$AUDIT_SCRIPT" ]; then
    python3 "$AUDIT_SCRIPT" || audit_failed=1
fi

# ---- [6/6] 锁文件快照备份（第三方 expected 权威源兜底，随 git 推送远端） ----
if [ -f "$LOCK" ]; then
    mkdir -p "$(dirname "$LOCK_BAK")"
    cp -f "$LOCK" "$LOCK_BAK"
    echo "[sync] 锁文件快照已备份 -> scripts/.backup/skill-lock.json"
else
    echo "[sync] 提示: 未找到锁文件 $LOCK，跳过备份"
fi

if [ "$audit_failed" -eq 0 ] && [ "$table_failed" -eq 0 ]; then
    echo "[sync] 完成。符号链接即改即生效；新/变更 skill 已在 ~/AGENTS.md 技能表中。"
else
    [ "$table_failed" -ne 0 ] && echo "[sync] 未完成：技能表生成器失败（见上方输出）。" >&2
    [ "$audit_failed" -ne 0 ] && echo "[sync] 未完成：对账存在缺口（见上方输出；以对账输出为准）。" >&2
fi
if [ "$audit_failed" -ne 0 ] && [ "$STRICT" -eq 1 ]; then
    exit 1
fi
exit 0
