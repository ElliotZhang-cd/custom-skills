#!/usr/bin/env bash
# ============================================================
# sync-wsl.sh - WSL 侧同步 custom-skills（GitHub 为唯一真相源）
# 架构: GitHub repo = 唯一真相源; WSL ~/custom-skills 与 Windows 均为 clone + 编辑入口
# 用法: bash ~/custom-skills/scripts/sync-wsl.sh   （或 ~/.local/bin 软链后直接跑）
# 流程: 脏树守卫(含 untracked) -> git pull --ff-only -> 按分发清单同步 POSIX 面的链接
#       (清失效链 + 建链) -> 刷新 AGENTS.md 技能表 -> 分发对账 -> 锁文件快照备份
# 面清单: scripts/distribution-targets.json 里 platform=posix 的面（唯一声明处）
#   role=storage 的面直指源目录；role=link 的面用相对路径指向第一个 storage 面
#   expect 决定每个面该有哪些来源（selfbuilt / mllw / thirdparty / manual；
#   本脚本只建链接类来源 selfbuilt 与 mllw——thirdparty 是 CLI 落的真实目录，
#   manual 是人工放置的真实副本，都不由本脚本增删）
# 注意: 自建 skill 绝不进入 skills CLI 锁文件; 编辑只发生在任一 clone, push 后他端 pull
# ============================================================
set -u

REPO="$HOME/custom-skills"
CONFIG="$REPO/scripts/distribution-targets.json"
TABLE_SCRIPT="$REPO/scripts/gen-skills-table.py"
AUDIT_SCRIPT="$REPO/scripts/check_distribution.py"
LOCK="$HOME/.agents/.skill-lock.json"
LOCK_BAK="$REPO/scripts/.backup/skill-lock.json"
ORIGIN="origin"
BRANCH="master"
MLLW_NAME="maintaining-llm-wiki"

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

# ---- 第二个来源：探测 LLMWiki 里的 maintaining-llm-wiki ----
find_mllw_src() {
    local c
    for c in "$HOME/Documents/LLMWiki/skills/$MLLW_NAME" \
             /mnt/c/Users/*/Documents/LLMWiki/skills/$MLLW_NAME; do
        if [ -f "$c/SKILL.md" ]; then
            printf '%s\n' "$c"
            return 0
        fi
    done
    return 1
}
MLLW_SRC="$(find_mllw_src || true)"

# ---- 源集合：仓库根下含 SKILL.md 的目录（仓库即列表）+ 第二个来源 ----
declare -A SRC=()
while IFS= read -r s; do
    [ -n "$s" ] && SRC["$s"]="$REPO/$s"
done < <(find "$REPO" -maxdepth 2 -name SKILL.md -printf "%h\n" 2>/dev/null \
         | sed "s|$REPO/||" | sort)
[ -n "$MLLW_SRC" ] && SRC["$MLLW_NAME"]="$MLLW_SRC"
[ "${#SRC[@]}" -gt 0 ] || fail "仓库里没找到任何自建 skill（根下含 SKILL.md 的目录）"

# 归属判定：只看链接自身的**字面目标**（v7.1 的教训——不要用 realpath -m 链式解析，
# 否则 .agents 旧链先删后，.claude 链会断在半途而漏删）。
link_owned() {  # $1=面目录 $2=名字
    local dir="$1" name="$2" tgt d rel
    tgt="$(readlink "$dir/$name" 2>/dev/null)" || return 1
    case "$tgt" in
        "$REPO"/*) return 0 ;;
    esac
    # 第二个来源的链：只有在我们**知道**源在哪时才认领，避免误删指向别处活链
    if [ -n "$MLLW_SRC" ]; then
        case "$tgt" in
            *"Documents/LLMWiki/skills/$MLLW_NAME"*) return 0 ;;
        esac
    fi
    # 指向另一个已声明面的同名条目（两级链）
    for d in "${FACE_DIR[@]}"; do
        rel="${d#"$HOME"/}"
        case "$tgt" in
            "$d/$name"|*"/$rel/$name") return 0 ;;
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
        if link_owned "$dir" "$name" && [ -z "${SRC[$name]:-}" ]; then
            rm "$link"
            echo "  [clean] - ${dir#"$HOME"/}/$name（源已不存在）"
            cleaned=$((cleaned + 1))
        fi
    done
done
[ "$cleaned" -eq 0 ] && echo "  （无失效链接）"

echo "[sync] 同步链接（POSIX 面: ${!FACE_DIR[*]}；源: ${#SRC[@]} 个$([ -n "$MLLW_SRC" ] && echo "，含 $MLLW_NAME")）..."
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
        if [ "$name" = "$MLLW_NAME" ]; then
            case "$exp" in *" mllw "*) ;; *) continue ;; esac
        else
            case "$exp" in *" selfbuilt "*) ;; *) continue ;; esac
        fi
        link="$dir/$name"
        if [ -L "$link" ]; then
            continue
        fi
        if [ -e "$link" ]; then
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
done
echo "  [sum]  新增 $added / 清理 $cleaned"

# ---- [4/6] 刷新 AGENTS.md 技能表 ----
if [ -f "$TABLE_SCRIPT" ]; then
    python3 "$TABLE_SCRIPT"
fi

# ---- [5/6] 分发对账（清单里的 posix 面 + 经 /mnt/c 看到的 win 面；缺口退出码 1 但不中断） ----
if [ -f "$AUDIT_SCRIPT" ]; then
    python3 "$AUDIT_SCRIPT" || true
fi

# ---- [6/6] 锁文件快照备份（第三方 expected 权威源兜底，随 git 推送远端） ----
if [ -f "$LOCK" ]; then
    mkdir -p "$(dirname "$LOCK_BAK")"
    cp -f "$LOCK" "$LOCK_BAK"
    echo "[sync] 锁文件快照已备份 -> scripts/.backup/skill-lock.json"
else
    echo "[sync] 提示: 未找到锁文件 $LOCK，跳过备份"
fi

echo "[sync] 完成。符号链接即改即生效；新/变更 skill 已在 ~/AGENTS.md 技能表中。"
