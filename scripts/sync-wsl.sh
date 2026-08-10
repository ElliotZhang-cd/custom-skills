#!/usr/bin/env bash
# ============================================================
# sync-wsl.sh - WSL 侧同步 custom-skills（GitHub 为唯一真相源）
# 架构: GitHub repo = 唯一真相源; WSL ~/custom-skills 与 Windows 均为 clone + 编辑入口
# 用法: bash ~/custom-skills/scripts/sync-wsl.sh   （或 ~/.local/bin 软链后直接跑）
# 流程: 脏树守卫(含 untracked) -> git pull --ff-only -> 同步两级符号链接 -> 刷新 AGENTS.md 技能表
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

# ---- [1/4] 脏树守卫（含 untracked，与 sync-windows.bat 对齐） ----
if [ -n "$(git status --porcelain)" ]; then
    echo "[sync] 错误: 仓库有本地未提交修改，--ff-only pull 会被拒绝:"
    git status --short
    echo "[sync] 处理: 改动是你要的则先 commit + push；否则 git checkout -- . 丢弃"
    exit 1
fi

# ---- [2/4] pull ----
git pull --ff-only "$ORIGIN" "$BRANCH" || fail "pull 失败（已排除本地修改干扰），请检查网络/代理"
echo "[sync] 当前版本: $(git log -1 --oneline)"

# ---- [3/4] 同步两级符号链接 ----
# 仓库根目录含 SKILL.md 的目录 = 自建 skill（真相源）
mapfile -t SKILLS < <(find "$REPO" -maxdepth 2 -name SKILL.md -printf "%h\n" | sed "s|$REPO/||" | sort)

echo "[sync] 同步符号链接（共 ${#SKILLS[@]} 个自建 skill）..."
for s in "${SKILLS[@]}"; do
    link="$AGENTS_DIR/$s"
    if [ ! -L "$link" ]; then
        ln -s "$REPO/$s" "$link"
        echo "  [agents] + $s -> $REPO/$s"
    fi
    link_c="$CLAUDE_DIR/$s"
    if [ ! -L "$link_c" ]; then
        ln -s "../../.agents/skills/$s" "$link_c"
        echo "  [claude] + $s -> ../../.agents/skills/$s"
    fi
done

# 清理过期链接（仓库中已不存在的自建 skill；realpath 解析两级链，claude 链接也能命中）
for link in "$AGENTS_DIR"/* "$CLAUDE_DIR"/*; do
    [ -L "$link" ] || continue
    name="$(basename "$link")"
    case "$(realpath -m "$link")" in
        "$REPO"/*)
            if [ ! -d "$REPO/$name" ]; then
                rm "$link"
                echo "  [clean] - $name（仓库已无此 skill）"
            fi
            ;;
    esac
done

# ---- [4/4] 刷新 AGENTS.md 技能表 ----
if [ -f "$TABLE_SCRIPT" ]; then
    python3 "$TABLE_SCRIPT"
fi

echo "[sync] 完成。符号链接即改即生效；新/变更 skill 已在 ~/AGENTS.md 技能表中。"
