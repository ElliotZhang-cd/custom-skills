# custom-skills

[![skills.sh](https://skills.sh/b/ElliotZhang-cd/custom-skills)](https://skills.sh/ElliotZhang-cd/custom-skills)

个人自定义技能仓库（**GitHub 为唯一真相源**，WSL / Windows 双编辑入口）。仅包含自建技能，第三方技能由 `npx skills` 独立管理，不入本仓库。

## 自建技能（本仓库）

| 技能 | 用途 |
|---|---|
| `authoring-skills` | 创建、评审、迭代可移植 Agent Skills（SKILL.md 包，遵循 open SKILL.md / AgentSkills 规范） |
| `analyzing-bigfive` | BFI-2 大五人格分析，生成来访者视角 HTML 报告 |
| `analyzing-cognitive-functions` | 荣格八维认知功能分析、MBTI 推断、依恋类型、恋爱适配/情侣报告 |
| `analyzing-complex-systems` | 复杂适应系统分析：反馈回路、涌现行为、战略博弈、临界转变 |
| `defining-products` | 产品定义框架：初衷分类 + 定位四问 + 不可能三角 + 迁移成本三层（cangjie 蒸馏） |
| `researching-user-costs` | 成本视角用户研究：以用户付出的真实成本为证据，识别口头反馈失真（cangjie 蒸馏） |

> ⚠️ `maintaining-llm-wiki` 已于 2026-08-16 迁出本仓库，迁移至 `LLMWiki/skills/maintaining-llm-wiki`。本仓库不再维护该 skill。

## 常用第三方技能（`npx skills` 管理）

### 文档与办公
- `docx` / `pptx` / `pdf` / `xlsx` — Word/PPT/PDF/Excel 读写与转换
- `ppt-master` — 可编辑 PPTX 生成与模板填充工作流

### 浏览器与自动化
- `browser-use` — CDP 直接控制浏览器（自动化、抓取、截图）
- `playwright-cli` — Playwright 浏览器交互与测试
- `obsidian` — Obsidian vault CLI 读写

### 写作与产品
- `humanizer-zh` — 去除 AI 写作痕迹
- `doc-coauthoring` — 文档共创工作流
- `product-spec-builder` — 产品需求收集与文档编写
- `internal-comms` — 公司内部沟通文案（状态报告、更新、FAQ 等）

### 分析与研究
- `market-research` — 市场调研、竞争分析、投资尽调
- `marketing-campaign` — 营销活动规划与落地
- `ui-ux-pro-max` — UI/UX 设计知识库（风格、配色、字体、动效、图表）

### 方法与流程
- `grill-me` / `grilling` — 方案严苛评审访谈
- `find-skills` — 发现并安装新技能
- `mcp-builder` — MCP 服务器构建指南

## 维护

### 架构

- GitHub remote（`ElliotZhang-cd/custom-skills`）= **唯一真相源**（唯一账本）；WSL `~/custom-skills/` 与 Windows `C:\Users\elliot\custom-skills` 均为 clone + 编辑入口，任一端改完 push，他端 pull
- 分发：WSL 侧 `~/.agents/skills/` → `~/.claude/skills/` 全为符号链接；Windows 侧 workbuddy / TRAE 由 bat「repo 即列表」自动遍历分发（新增/改名零列表维护）；ZCode 的 `.zcode\skills` 自建/mllw 为 junction 直指本仓库与 LLMWiki（push 即生效，无需分发）
- 分发面白名单：`scripts/distribution-targets.json` 为唯一配置源（封闭投影面，新增工具目录须先在此显式登记）
- 对账闭环：`scripts/check_distribution.py` 由白名单驱动五面对账，输出 MISSING / EXTRA / UNKNOWN / BROKEN / CONFLICT（前四类缺失退出码 1，不中断同步）
- 手动件账本：`manual-skills.md` 记录人工放置的第三方技能（TRAE / ZCode，含来源与更新时间），对账时把 UNKNOWN 升格为「有账手动件」
- 冲突纪律：改前先 pull；两端同时改同一文件会产生 git 冲突，手动解决（sync 脚本用 `--ff-only` 保护，绝不自动覆盖）

### 铁律

1. 自建 skill 绝不进入 skills CLI 锁文件（`~/.agents/.skill-lock.json` 只含第三方）；不对自建 skill 跑 `npx skills update`（会毁掉链接）
2. 第三方唯一管理器 = `npx skills`（find/add/update/remove）；openskills 已弃用（曾导致双管理器事故）
3. 编辑只发生在任一 clone（WSL `~/custom-skills/` 或 Windows `C:\Users\elliot\custom-skills`），不编辑 `~/.claude/skills/` 下的任何目录（全是链接，防止改错副本）
4. 维护面 = 使用面，且使用面必须显式登记于 `distribution-targets.json`：WSL-claude/opencode、workbuddy、TRAE、ZCode（2026-09-03 v6 起纳入）。新工具要加载技能，先登记再使用
5. 任何 add/update/remove 后运行 `python3 scripts/gen-skills-table.py` 刷新 AGENTS.md 技能表格
6. Windows `C:\Users\elliot\.agents\skills` 已于 2026-09-03 废弃删除，不得重建为技能存放处；ZCode 的手动第三方件放 `.zcode\skills` 并登记 `manual-skills.md`（junction/锁文件优先，禁止无账拷贝）

### 更新自建（任一端编辑 → push → 他端同步）

```bash
vim <skill>/...                                    # 编辑本端 clone，改完即 push
git add -A && git commit -m "[skill] 变更说明"
git -c http.proxy=$HTTPS_PROXY -c https.proxy=$HTTPS_PROXY push origin master
# 若 description 变更 → python3 scripts/gen-skills-table.py
```

### 第三方（skills CLI 管理，不入本仓库）

- 引入：`npx skills find xxx`（发现）→ `DISABLE_TELEMETRY=1 npx skills add <source> -g -a amp -y`（安装到 `~/.agents/skills/`，实测命令模板）→ `python3 scripts/gen-skills-table.py`
- 更新：发现问题 `DISABLE_TELEMETRY=1 npx skills update <name>`；季度全量 `npx skills update -y` → 刷新表格
- 创建新 skill：`npx skills init <name>` 脚手架 → 并入本仓库 → 链接链自动生效
- 行尾：`.gitattributes` 强制 LF，避免 Windows 检出 CRLF

### WSL 侧同步（一键）

```bash
bash scripts/sync-wsl.sh        # 脏树守卫 → git pull --ff-only → 自动建/删两级符号链接 → 刷新 AGENTS.md 表格 → 分发对账 → 锁文件快照备份
```

### Windows 侧同步（workbuddy + TRAE + ZCode）

- 机制：GitHub 中转（workbuddy/TRAE 为 robocopy 副本）；ZCode 的 `.zcode\skills` 为 junction 直指本仓库与 LLMWiki，push 即生效，无需任何分发动作
- push 后 → Windows 运行 `sync-custom-skills.bat`（转发到本仓库 `scripts/sync-windows.bat`，一键：git pull 到 `C:\Users\elliot\custom-skills` + 自动分发到 workbuddy / TRAE + 五面对账）
- workbuddy：`C:\Users\elliot\.workbuddy\skills\` 由 bat 脚本 robocopy 分发（保留 `_user_meta.json`）
- TRAE：`C:\Users\elliot\.trae-cn\skills\` 同由 bat 分发（TRAE 平台自带 skill 非本体系，对账仅报告不删除）
- ZCode：`C:\Users\elliot\.zcode\skills\` 自建/mllw 为 junction；手动第三方件放此处并登记 `manual-skills.md`（见铁律 6）
- 脚本真相源：`scripts/sync-windows.bat`（已去敏感化，`%USERPROFILE%` 派生路径，不硬编码用户名）