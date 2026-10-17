# design.md — syncing-skills

## 架构

四层，各自只有一个权威：

```
① 真相源层     custom-skills（自建，GitHub 唯一源头） · LLMWiki/skills（第二个来源）
② 声明层       distribution-targets.json（有哪些分发目标、各自期望什么）
               manual-skills.md（Windows 手工技能：名字 / 来源 / 所在目标）
               ~/.agents/.skill-lock.json（WSL 第三方：名字 / 来源 / 哈希）
③ 投影层       5 个已登记目标：WSL .agents(storage) .claude(link) + Win workbuddy/zcode/dsh(junction)
④ 执行层       sync-wsl.sh · sync-custom-skills.bat → ensure_junctions.ps1 → check_distribution.py
               文档层：README（人） · SKILL.md（agent） · 合成页（why + 历史）
```

不变量：

- 真相源只有两个，且都在 git 里；投影层永远可以删了重建。
- 声明层是**唯一**的"应该有什么"的表达；任何没被声明的目标都不在管理范围内（但会被 R4 发现机制点出来）。
- 执行层的判定只有两类结果：**失败**（声明没到位/被顶替）与**提醒**（多出来的）。

## 数据流

```
人提供改好的技能包
  → 编辑某个 clone 的仓库目录（唯一源头）
  → commit + push（发布）
  → 另一端 pull
  → 建链接 / 清死链接（ensure_junctions.ps1 或 sync-wsl.sh）
  → 刷新派生表（AGENTS.md 技能表、README 目标一览）（仅 WSL 侧可跑）
  → 对账（声明自检 + 子集判定 + 未登记目标发现）
  → 落账（log.md、登记表、合成页）
```

## 接口

| 动作 | 命令 | 平台前提 |
|---|---|---|
| 对账（含本轮新增的自检与发现） | `python3 scripts/check_distribution.py` | 两端 |
| 下线预览（只打印） | `python3 scripts/check_distribution.py --retire <id>` | 两端；须在删清单词条前跑 |
| 建链接 / 清死链接 | `powershell -File scripts/ensure_junctions.ps1` | Windows；清单驱动，无需传参 |
| 一键同步（Windows） | `sync-custom-skills.bat` | Windows |
| 一键同步（WSL） | `bash scripts/sync-wsl.sh` | WSL |
| 刷新派生表 | `python3 scripts/gen-skills-table.py` | **仅 WSL**：来源面是 `~/.agents/skills`，Windows 上不存在 |

退出码语义：`0` 无失败；`1` 有失败或声明目标缺失；`2` `--retire` 用法错误或未知目标。

## 数据模型

**分发目标（清单条目）**

| 字段 | 取值 | 说明 |
|---|---|---|
| `id` | 小写 token | 同时是登记表「所在目标」的词表 |
| `platform` | `win` \| `posix` | 缺省为 `posix`；写错会导致该端静默不审 |
| `relpath` | 相对家目录的路径段 | 写错会静默失去该目标的检查 |
| `expect` | `selfbuilt` \| `mllw` \| `thirdparty` \| `manual` 的子集 | 声明"这个目标应该有什么" |
| `role` | `junction` \| `link` \| `storage` | 谁负责建链、哪些算被顶替 |
| `required` | 布尔 | 目标目录缺失时是否计为失败 |

**手工技能（登记表行）**：`名字 | 来源 | 一句话 | 更新时间 | 所在目标`

**判定分级**

| 判定 | 触发 | 结果 |
|---|---|---|
| 缺失 | 声明名字解析不到 | 失败 |
| 损坏 | 声明的链接悬空 | 失败 |
| 被顶替 | 名字在、`SKILL.md` 在，但不是本体系的链接 | 失败 |
| 同名冲突 | 自建与第三方同名 | 失败 |
| 多余 | 声明之外的文件/目录 | 提醒（附"多了哪些、哪些像旧文件"） |
| 未登记目标 | 非空技能目录不在清单里 | 提醒 |
| 声明非法 | 字段缺失/拼错、登记表出现未声明 id | 失败（新增） |

## 关键决策与理由

- **ADR-0001**：GitHub 唯一源头 + 双 clone 编辑入口（发布只认 push）。
- **ADR-0002**：自建/第二来源用链接，Windows 第三方用真实副本；由此推出「自建绝不进 CLI 锁文件」。
- **ADR-0003**：对账判「声明必须包含」，多余只作提醒（残余风险：僵尸件靠人看）。
- **ADR-0004**：Windows 的 `~/.agents/skills` 存在，但**只能由 `npx skills` 管理**（第三方存储面）。

次级决策：

1. **skill 只写程序与判定规则，易腐状态改读取点**（R8）。理由：写死的数字是前三次漂移的共同起点。
2. **0 个新增可执行文件**：必要的两处检查（声明自检 R5、未登记目标发现 R4）并入既有对账脚本；文档名字集合漂移改为**生成**而非校验。理由：校验代码比被校验的表还长；把漂移变成不可能比检测它更省。
3. **术语改平实**：分发目标 / 分发清单 / 手工技能 / 登记表 / 硬规则 / 唯一源头 / 第二个来源 / 建链接 / 清死链接；脚本输出与代码标识符不动。理由：同一概念曾有五个名字（面 / 使用面 / 维护面 / 分发面 / 投影面）。
4. **单一出处**：操作程序只在 skill 写一次；README 面向人（目标一览 + 四类来源 + 硬规则 + 指路）；合成页面向 why 与历史。

## 约束

- `specs/` 与 `docs/` 下**不得**出现名为 `SKILL.md` 的文件：自建技能的收集规则是「仓库根下含 `SKILL.md` 的目录」与 `find -maxdepth 2 -name SKILL.md`，放错位置会让规格文档被当成技能分发。
- 不新增可执行文件；不改脚本输出的中文字串；不改代码标识符与清单字段名。
- 删除工作区外的条目之前必须先打印清单（R11）。
- 不 commit、不 push：由人确认后执行。

## 需求映射

| 需求 | 落点 |
|---|---|
| R1 / R2 | `scripts/check_distribution.py`（子集判定，已有） |
| R3 | `sync-wsl.sh` / `sync-custom-skills.bat` / `ensure_junctions.ps1`（已有） |
| R4 / R5 | `scripts/check_distribution.py`（本轮新增两处检查） |
| R6 | `manual-skills.md` 入账纪律 + SKILL.md 流程 |
| R7 | 清单增删 + `--retire`（已有）+ SKILL.md 流程 |
| R8 / R9 | `syncing-skills/SKILL.md` 与 `references/` |
| R10 | `README.md` 目标一览（生成块）+ 来源说明 |
| R11 | `--retire` 预览 + 清理流程 |
| R12 | `specs/syncing-skills/tasks.md` 的验收任务 |
