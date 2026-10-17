# 真相源、来源类别与平台前提

## 两个真相源

- **自建技能**：GitHub `ElliotZhang-cd/custom-skills`（唯一源头）。两端各一个 clone：WSL `~/custom-skills/`、Windows `%USERPROFILE%\custom-skills`，都能编辑，但**只有 push 才算发布**（见 `docs/adr/0001`）。投影目标里的任何改动都不算数。
- **第二个来源**：`LLMWiki/skills/maintaining-llm-wiki`——一个技能，独立仓库、独立 git 历史。

## 四类来源

| 来源 | 是什么 | 怎么分发 | 谁声明 |
|---|---|---|---|
| `selfbuilt` | 本仓库根下含 `SKILL.md` 的目录 | 链接（WSL 两级符号链接 / Windows junction） | 仓库自身——仓库即列表 |
| `mllw` | `maintaining-llm-wiki` | 两端都由同步脚本按清单建链（Windows：junction；WSL：storage 面直指源 + link 面二级链），前提是源可被发现 | LLMWiki 仓库是否存在 |
| `thirdparty` | `npx skills` 管理的第三方技能 | 各平台面 → **链接**到该平台的仓库层（仓库层本身是 CLI 维护的真实目录；增删改流程见 `references/workflows.md`「第三方技能」） | 各平台自己的锁文件 `.skill-lock.json` |
| `manual` | 人工放置、无仓库来源的第三方技能 | Windows 各目标下的真实副本 | 登记表 `manual-skills.md` |

链接与副本的分工理由见 `docs/adr/0002`。

## 分发目标

目标清单的唯一来源 = `scripts/distribution-targets.json`（**注意它只是声明层五处之一**，见 `docs/architecture.md` 第二节）。**这里不列目标清单**；`README.md` 里有一览，由脚本生成。

每个目标的加载机制细节（扫描根、rank、是否读 `~/.claude/skills`、是否跟随链接、第三方策略）写在该条目的 `note` 字段里，别在文档里复述。

## 平台前提

| 动作 | Windows | WSL |
|---|---|---|
| 对账 | `python scripts\check_distribution.py` | `python3 scripts/check_distribution.py` |
| 一键同步 | `sync-custom-skills.bat`（转发到 `scripts/sync-windows.bat`） | `bash scripts/sync-wsl.sh` |
| 刷新 AGENTS.md 技能表 | ✗ 来源面 `~/.agents/skills` 只在 WSL 存在 | ✓ |
| 刷新 README 生成块 | ✓ `--readme` | ✓ `--readme` |
| 对账覆盖 | 只审 `platform: win` 的目标 | 全部：本机 posix 面 + 所有 `/mnt/c/Users/*` 上的 win 面 |
| 第三方池 | 读 Windows 自己的锁（首次在那台机器跑 `npx skills` 之前为空） | 读锁文件 |
| 建链接 | `junction`：**读清单**、按 `role=junction` 补链（`ensure_junctions.ps1`） | 符号链接：**读清单**、按 `role` 建链（`storage` 直指源 / `link` 走二级链），父目录在时自动建技能根（`sync-wsl.sh`，v7.7 起） |

## 文档分工（别在错的地方找东西）

| 文件 | 给谁 | 放什么 |
|---|---|---|
| `README.md` | 人 | 目标一览（生成）、四类来源、硬规则、日常操作指路 |
| 本技能 | agent | 四类操作的分步流程、判定分级、排查手册 |
| `docs/adr/` | 人 | 4 条难回退的决定及其理由 |
| LLMWiki `wiki/syntheses/skill-maintenance-workflow.md` | 人 | 为什么这样定、版本沿革、事故教训 |
| `specs/syncing-skills/` | 维护者 | 本技能的需求/设计/任务/规则（构建期的产物） |

## 已知盲区

- **跨系统的同名工具目录**：清单的 `platform` 同时表达"哪个操作系统"和"谁的家目录"，所以装在 WSL 里的 `~/.zcode`、`~/.dsh` 这类目录在两端都不会被审。对账的 `[NEW?]` 提醒是唯一防线——**先登记再使用**。
- **技能根不必叫 `skills`**：未登记目标发现只认目录名恰好是 `skills` 的根，且只扫本机家目录、最多四层。名字不同的工具技能根、以及"仓库形"的目录（一个 clone 里带若干技能）都不会被发现。
- **项目级技能根**（仓库内的 `.claude/skills`、`.agent/skills` 等）不在清单模型里，属脚本内的显式附加检查。
- **工具自带市场 / 云端管理**：它们可以往自己的技能目录写东西，甚至可以复活已删技能。本体系不删它们，只把它们列为提醒。
