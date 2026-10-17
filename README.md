# custom-skills

[![skills.sh](https://skills.sh/b/ElliotZhang-cd/custom-skills)](https://skills.sh/ElliotZhang-cd/custom-skills)

> 自建 Agent Skills 的唯一源头，同时是「我的技能管理系统」的说明入口：
> 它声明技能被分发到哪些 agent 平台、怎么保持一致、出问题怎么查。

## 这是什么

一句话：把写好的技能分发到每个 agent 平台，并让**实际加载到的技能列表**与**声明的**一致。

整体结构（五层归属、不变量、机制契约、盲区总账）见 `docs/architecture.md`——那是先读的一份。

两个真相源：

- **自建技能** = 本仓库（GitHub `ElliotZhang-cd/custom-skills`）。WSL `~/custom-skills/` 与 Windows `%USERPROFILE%\custom-skills` 都是它的 clone，都能编辑；**push 才算发布**。
- **第二个来源** = `LLMWiki/skills/maintaining-llm-wiki`（独立仓库、独立历史）。

技能的**内容**由人写（写法规范见 `authoring-skills`）；本仓库管的是它落到哪、怎么分发、怎么对账、怎么退役。

## 四类来源

| 来源 | 是什么 | 怎么分发 | 谁声明 |
|---|---|---|---|
| 自建 | 本仓库根下含 `SKILL.md` 的目录 | 链接（WSL 两级符号链接 / Windows junction） | 仓库自身——仓库即列表 |
| 第二个来源 | `maintaining-llm-wiki` | 同上，指向 LLMWiki 源目录 | LLMWiki 仓库是否存在 |
| 第三方 | `npx skills` 管理的技能 | **链接**：各平台面 → 该平台的 npx **仓库层**（WSL `~/.agents/skills`、Windows `%USERPROFILE%\.agents\skills`；仓库层本身是真实目录） | 各平台自己的锁文件 `.skill-lock.json` |
| 手工技能 | 人工放置、无仓库来源的第三方技能 | Windows 各目标下的真实副本 | 登记表 `manual-skills.md` |

## 分发目标一览

<!-- TARGETS_TABLE_START -->
| 目标 | 路径 | 角色 | 加载什么 |
|---|---|---|---|
| `agents` | `~/.agents/skills` | storage | 自建、第二个来源、第三方 |
| `claude` | `~/.claude/skills` | link | 自建、第二个来源、第三方 |
| `agents-win` | `%USERPROFILE%\.agents\skills` | storage | 第三方 |
| `workbuddy` | `%USERPROFILE%\.workbuddy\skills` | junction | 自建、第二个来源 |
| `zcode` | `%USERPROFILE%\.zcode\skills` | junction | 自建、第二个来源、第三方、手工技能 |
| `dsh` | `%USERPROFILE%\.dsh\skills` | junction | 自建、第二个来源、第三方、手工技能 |
<!-- TARGETS_TABLE_END -->

> 这张表由 `python3 scripts/gen-skills-table.py --readme README.md` 从 `scripts/distribution-targets.json` 生成，**不要手改**。
> 每个平台**怎么加载技能**（扫描根、rank、是否读 `~/.claude/skills`、是否跟随链接、第三方策略）写在该清单条目的 `note` 字段里——那里是唯一出处，本文不复述。

## 自建技能

<!-- SELF_BUILT_TABLE_START -->
| 技能 | 一句话 |
|---|---|
| `analyzing-bigfive` | 解读 BFI-2 的 5 维度 + 15 子维度原始分，产出给来访者阅读的 HTML 报告；不做诊断。 |
| `analyzing-complex-systems` | 帮助用户以系统思维分析多主体复杂问题（平台生态、市场、组织、社会现象等），产出「机制—杠杆—风险」结构化判断。 |
| `analyzing-functions` | 解读荣格八维 / MBTI 八功能分数，判定类型并为单人产出人格 HTML 报告、为情侣双方产出关系动力 HTML 报告；不覆盖职业适配、年龄推断，以及理论范围之外的婚恋适配裁决。 |
| `authoring-skills` | Creates, reviews, and iterates on portable Agent Skills (SKILL.md packages) that follow open SKILL.md / AgentS… |
| `defining-products` | Use when 用户在产品/功能/项目立项或审查阶段需要回答"为什么做、为谁做、先做什么、凭什么是我们"。 |
| `researching-user-costs` | Use when 用户在做用户访谈、收集反馈、评估"用户是否真的接受产品/功能"。 |
| `syncing-skills` | 维护和管理我的技能列表与各 agent 平台的分发，让每个平台加载到的技能与真相源保持一致。 |
<!-- SELF_BUILT_TABLE_END -->

> 同样由上面那条命令生成；新增或改名的技能会自动出现在这里。

## 第三方与手工技能

- 第三方（两端各一份**仓库层**：`~/.agents/skills` 与 `%USERPROFILE%\.agents\skills`）由 `npx skills` 管理，权威名字清单是各平台的锁文件 `.skill-lock.json`（含来源 URL 与哈希）；各平台面上的第三方是指向这一层的**链接**，由同步脚本建。
- 手工技能是**尚未纳入 npx 的存量件**（没有仓库层条目可指），在 Windows 各目标上是真实副本，权威清单是 `manual-skills.md`；一旦某个名字进了 npx 的锁，该面就应改由链接承载——对账会把仍占位的副本报成 `[STALE]`。
- 工具自带市场、云端管理的条目不属本体系：对账只把它们列为「多余」提醒，不删除——要清就去工具自己的界面删。

（本文不列举具体名字：名字的权威来源是上面两个文件，枚举在这里就一定会漂移。）

## 硬规则

1. **自建技能绝不进入第三方 CLI 的锁文件**；不对自建技能跑 `npx skills update`（它会把链接换成拷贝、覆盖本地修改）。
2. **第三方唯一管理器是 `npx skills`**，且它只管**仓库层**（存储面 + 锁）；各平台面上的第三方由同步脚本建链、由对账检查。`openskills` 已弃用。
3. **编辑只发生在两个 clone 里**；不编辑任何分发目标内的条目（那里全是链接或副本）。改完 commit + push，另一端 pull 后才生效。
4. **每个分发目标必须在 `scripts/distribution-targets.json` 里声明**——登记了才算在管；不再使用的目标要显式下线。
5. **任何技能增删改后刷新派生表**（本文件的生成块、`~/AGENTS.md` 的技能表）。`~/AGENTS.md` 那张表只能在 WSL 侧刷新，因为它的来源面在 WSL。
6. **禁止无账拷贝**：手工技能必须登记 `manual-skills.md`。Windows 的 `%USERPROFILE%\.agents\skills` 是第三方存储面，**只能由 `npx skills` 写**：不得手工往里放、不得让它变陈旧（理由见 `docs/adr/0004`）。
7. **严禁向 junction 目标复制**；目标的链接只由 `ensure_junctions.ps1` 增删。

## 日常操作

**流程细节不在这里复述**——完整流程见技能 `syncing-skills/`（`SKILL.md` 是入口），对账输出怎么读见它的 `references/reconciliation.md`。

两条一键命令：

```
Windows:  sync-custom-skills.bat
WSL:      bash scripts/sync-wsl.sh
```

两端脚本各自的分步流程（步数、顺序、脏树守卫、锁快照等）见 skill 的 `references/workflows.md`——本文不复述操作细节。

## 目录

```
<技能名>/SKILL.md        自建技能（仓库根下含 SKILL.md 的目录即一个技能）
scripts/                 分发与对账工具（分发目标声明、补链、对账、派生表生成）
manual-skills.md         手工技能登记表
specs/syncing-skills/    本技能的需求 / 设计 / 任务 / 规则
docs/adr/                难回退的决定及其理由
README.md                本文件（生成块 + 硬规则）
sync-custom-skills.bat   Windows 一键同步入口（转发到 scripts/sync-windows.bat）
```

## 排障

对账输出的每一个标记（失败 / 提醒两级）与常见症状处置，见 `syncing-skills/references/reconciliation.md`。
核心判据一句话：**失败 = 声明的东西没到位或被顶替；提醒 = 有额外的东西**。

## 决定与沿革

- `docs/architecture.md` — **结构总图**：五层归属、不变量、机制契约、盲区总账、文档分工（先读这个）。
- `docs/adr/` — 4 条难回退的决定：自建看 git / 第三方看 npx、链接与副本的分工、对账的子集语义、Windows `.agents` 存储面只能由 npx 管理。
- `specs/syncing-skills/` — 本技能**构建期**的需求、设计、任务与规则（已冻结，勿据以操作）。
- LLMWiki 的 `wiki/syntheses/skill-maintenance-workflow.md` — 为什么这样定、版本沿革与事故教训。
