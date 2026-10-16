#!/usr/bin/env bash
# ============================================================
# sync-wsl.sh - WSL 侧同步 custom-skills（GitHub 为唯一真相源）
# 架构: GitHub repo = 唯一真相源; WSL ~/custom-skills 与 Windows 均为 clone + 编辑入口
# 用法: bash ~/custom-skills/scripts/sync-wsl.sh   （或 ~/.local/bin 软链后直接跑）
# 流程: 脏树守卫(含 untracked) -> git pull --ff-only -> 同步两级符号链接(清失效链 + 建链)
#       -> 刷新 AGENTS.md 技能表 -> 分发对账 -> 锁文件快照备份
# 注意: 自建 skill 绝不进入 skills CLI 锁文件; 编辑只发生在任一 clone, push 后他端 pull
# ============================================================
set -u

REPO="$HOME/custom-skills"
AGENTS_DIR="$HOME/.agents/skills"
CLAUDE_DIR="$HOME/.claude/skills"
TABLE_SCRIPT="$REPO/scripts/gen-skills-table.py"
ORIGIN="origin"
BRANCH="master"

fail() {
    echo "[sync] 错误: $*" >&2
    exit 1
}

[ -d "$REPO/.git" ] || fail "仓库不存在: $REPO"
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

# ---- [3/6] 同步两级符号链接（清失效链 + 建链）----
# 仓库根目录含 SKILL.md 的目录 = 自建 skill（真相源）
mapfile -t SKILLS < <(find "$REPO" -maxdepth 2 -name SKILL.md -printf "%h\n" | sed "s|$REPO/||" | sort)

is_repo_skill() { [ -f "$REPO/$1/SKILL.md" ]; }

# .agents 层的归属：看链接自己的目标是否以 $REPO/ 开头。
# v7.1 修正（补 2026-10-12 记录的缺口）：不再用 `realpath -m` 链式解析——
# .agents 旧链先被删后，.claude 链的 realpath 会断在半途，落不进 "$REPO"/* 分支而漏删。
agents_link_owned() {
    local target
    target="$(readlink "$AGENTS_DIR/$1" 2>/dev/null)" || return 1
    case "$target" in
        "$REPO"/*) return 0 ;;
    esac
    return 1
}

echo "[sync] 清理失效链接（只看链接自身目标；非本体系链接一律保留）..."
cleaned=0
for link in "$AGENTS_DIR"/* "$CLAUDE_DIR"/*; do
    [ -L "$link" ] || continue
    name="$(basename "$link")"
    case "$link" in
        "$AGENTS_DIR"/*)
            if agents_link_owned "$name" && ! is_repo_skill "$name"; then
                rm "$link"
                echo "  [clean] - .agents/$name（仓库已无此 skill）"
                cleaned=$((cleaned + 1))
            fi
            ;;
        *)
            # .claude 层：目标为 .agents 层同名链接（两级链）或直接指仓库
            target="$(readlink "$link" 2>/dev/null)"
            owned=0
            case "$target" in
                "$REPO"/*) owned=1 ;;
                *".agents/skills/$name"|"$AGENTS_DIR/$name")
                    # 跟随 .agents 层归属：该层完全不存在（本轮已删或从未建立）→ 本体系残留；
                    # 该层是本体系链接 → 本体系；该层是 foreign 链接（含悬空）或真实条目 → 不动。
                    # 注意用 -L/-e 区分“不存在”与“存在但悬空”，否则会误删 foreign 链的二级链
                    if { [ ! -L "$AGENTS_DIR/$name" ] && [ ! -e "$AGENTS_DIR/$name" ]; } \
                       || { [ -L "$AGENTS_DIR/$name" ] && agents_link_owned "$name"; }; then
                        owned=1
                    fi
                    ;;
            esac
            if [ "$owned" = 1 ] && ! is_repo_skill "$name"; then
                rm "$link"
                echo "  [clean] - .claude/$name（仓库已无此 skill）"
                cleaned=$((cleaned + 1))
            fi
            ;;
    esac
done
[ "$cleaned" -eq 0 ] && echo "  （无失效链接）"

echo "[sync] 同步符号链接（共 ${#SKILLS[@]} 个自建 skill）..."
added=0
for s in "${SKILLS[@]}"; do
    link="$AGENTS_DIR/$s"
    if [ ! -L "$link" ]; then
        if [ -e "$link" ]; then
            echo "  [note] 非符号链接，保留原样: $link"
        else
            ln -s "$REPO/$s" "$link"
            echo "  [agents] + $s -> $REPO/$s"
            added=$((added + 1))
        fi
    fi
    link_c="$CLAUDE_DIR/$s"
    if [ ! -L "$link_c" ]; then
        if [ -e "$link_c" ]; then
            echo "  [note] 非符号链接，保留原样: $link_c"
        else
            ln -s "../../.agents/skills/$s" "$link_c"
            echo "  [claude] + $s -> ../../.agents/skills/$s"
            added=$((added + 1))
        fi
    fi
done
echo "  [sum]  新增 $added / 清理 $cleaned"

# ---- [4/6] 刷新 AGENTS.md 技能表 ----
if [ -f "$TABLE_SCRIPT" ]; then
    python3 "$TABLE_SCRIPT"
fi

# ---- [5/6] 分发对账（五面: .agents/.claude + workbuddy/ZCode/DSH 经 /mnt/c；缺口退出码 1 但不中断） ----
AUDIT_SCRIPT="$REPO/scripts/check_distribution.py"
if [ -f "$AUDIT_SCRIPT" ]; then
    python3 "$AUDIT_SCRIPT" || true
fi

# ---- [6/6] 锁文件快照备份（第三方 expected 权威源兜底，随 git 推送远端） ----
LOCK="$HOME/.agents/.skill-lock.json"
LOCK_BAK="$REPO/scripts/.backup/skill-lock.json"
if [ -f "$LOCK" ]; then
    mkdir -p "$(dirname "$LOCK_BAK")"
    cp -f "$LOCK" "$LOCK_BAK"
    echo "[sync] 锁文件快照已备份 -> scripts/.backup/skill-lock.json"
else
    echo "[sync] 提示: 未找到锁文件 $LOCK，跳过备份"
fi

echo "[sync] 完成。符号链接即改即生效；新/变更 skill 已在 ~/AGENTS.md 技能表中。"
