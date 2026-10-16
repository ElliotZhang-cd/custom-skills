# 四类操作的分步流程

命令里的 `scripts/…` 都相对仓库根。Windows 用 `python`，WSL 用 `python3`。

---

## 第二个来源（`maintaining-llm-wiki`）

它不在本仓库里，两个平台的建链方式**不一样**，而且 WSL 侧**不由同步脚本负责**（这是实测结论，别照 `sync-wsl.sh` 的名字猜）：

| 平台 | 谁建链 | 命令 |
|---|---|---|
| Windows | 同步脚本自动（`ensure_junctions.ps1` 读清单，把 mllw 源目录也纳入） | `sync-custom-skills.bat` |
| WSL | **LLMWiki 仓库自己的脚本**，只建 `.agents` 那一条 | `bash skills/maintaining-llm-wiki/scripts/install_links.sh` |
| WSL | `.claude` 的二级链要**手工**补（`sync-wsl.sh` 只处理仓库内的自建技能） | `ln -s ../../.agents/skills/maintaining-llm-wiki ~/.claude/skills/maintaining-llm-wiki` |

**全新 WSL 家目录必须先做这一步**：两个 POSIX 目标都声明了 `mllw`，不建这两条链，对账永远到不了退出码 0（会留两条 `[MISS] maintaining-llm-wiki`）。

审计入口：LLMWiki 仓库的 `scripts/check_skill_links.py` 会按分发清单逐平台检查 mllw 入口是否指向源目录。

---

## 技能

### 新增（自建）

1. 在任一 clone 建 `<name>/SKILL.md`（内容自己写，或先转 `authoring-skills`）。
2. `git add -A && git commit -m "[skill] 说明"` → push。**push 等于发布**；投影目标里的任何改动都不算数。
3. 他端 `pull`，然后**两端各跑一次同步**：`sync-custom-skills.bat` / `bash scripts/sync-wsl.sh`。
   自建技能不需要登记进清单——「仓库即列表」：同步脚本扫描仓库根下含 `SKILL.md` 的目录自动建链接。
   首次在 WSL 侧做这件事之前，先确认「第二个来源」的两条链已在（见上一节）。
4. **刷新派生表**：`python3 scripts/gen-skills-table.py`（AGENTS.md，仅 WSL）与
   `python3 scripts/gen-skills-table.py --readme README.md`（README，两端可跑）。
5. **把派生表也提交推送**：生成会改动 `README.md`/`~/AGENTS.md`，工作树随之变脏，而两端同步脚本都有脏树守卫——不提交，下一次同步会被自己挡住。正确循环是
   `同步 → 生成 → commit + push → 他端 pull → 对账`。
6. 对账（两端）→ 退出码 0。**只在单端做过改动时，另一端必然报 `[MISS]`，这是预期**：全绿的前提是两端都同步过。
7. **加载实证**：在工具里真的看到。注意区分「模型技能目录」与 `/` 命令面板——
   技能自己声明 `disable-model-invocation: true` 时只进后者，属预期，不是同步缺口。
   纯命令行环境无法在工具里复核时，退化口径是：经每个目标的链接能读到 `SKILL.md`，并把"在工具里复核"留作下一步。
8. 落账规则见本文末「落账」。

### 改名

改名 = 退役旧名 + 新增新名的**同一次提交**（同一次同步里清旧链、建新链，避免中间态）。

1. 旧目录改名/删除、新目录建好，同一次 commit + push。
2. 两端同步。
3. **查同名冲突**：新名字若与第三方技能同名，对账会报 `[CONFLICT]` —— 必须改名，不能共存。
4. 清残留：对账若报 `[EXTRA]`（本体系僵尸）或 `[UNK ]`（非本体系残留），逐条确认后手工删。
   同步脚本只清「目标落在本仓库 / LLMWiki 之下、且已不解析为技能」的链接，其余不动。
5. 刷新派生表、按「新增」第 5 步提交、两端同步、对账。
6. 若旧名也在 `manual-skills.md` 里（手工技能同名），一并改账。

### 退役 / 删除（自建）

预览就是**同步前的对账输出**：`[BRK ]` 是待清的死链、`[EXTRA]` 是本体系僵尸。
`--retire <id>` 只服务于**分发目标**下线，传技能名会报未知目标（退出码 2）。

1. 删仓库目录 → commit + push。
2. 两端同步：本体系的链接会被自动清掉（`ensure_junctions.ps1` 的清理、`sync-wsl.sh` 的失效链清理）。
   注意：技能删掉后，同步前残留的是**死链 `[BRK ]`**，不是 `[EXTRA]`——`[EXTRA]` 只发生在仍能解析的本体系条目上。
3. 对账确认该名字不再出现在任何目标；若有 `[EXTRA]`/`[STALE]` 残留，确认后手工删。
4. 刷新派生表、提交、两端同步。
5. 落账见「落账」。

### 修改内容（自建）

内容由人改；本技能只管"改完之后"。1) 改 `SKILL.md` 或 references → 2) commit + push → 3) 他端 pull（**不用**重建链接，链接指的就是仓库）→ 4) `description` 若变了，刷新派生表并按「新增」第 5 步提交 → 5) 落账。

---

## 分发目标

「分发目标」= 某个 agent 平台加载技能的目录。声明在 `scripts/distribution-targets.json`，那是"应该有什么"的唯一**声明处**（注意：账本 token 词表另有一处在代码里，见下）。

### 新增

1. **先查证加载机制**（读 vendor 文档或代码，不靠猜）：扫描哪些根、优先级 rank、是否读 `~/.claude/skills`、是否跟随 junction/符号链接、frontmatter 规则、是否有 `disable-model-invocation` 一类开关、watcher 是否热加载、**是否自带技能管理器**（会覆盖或复活技能）。据此再定路径与 `role`——**能链接就不复制**。
2. **登记清单**：加一条 `{id, platform, relpath, expect, role, required, note}`。
   - `id` 小写 token，同时也是账本「所在目标」列的词表。
   - `platform` 取 `win` / `posix`：**漏写会让这个目标在 Windows 端被静默剔除**。
   - `expect` 取 `selfbuilt` / `mllw` / `thirdparty` / `manual` 的子集。
   - `role` 取 `junction` / `link` / `storage`：Windows 侧补链脚本只处理 `junction`，对账用它划定"被顶替"的范围。
   - `required`：本机在装则 `true`；目标目录缺失会计入退出码 1。
   - `note` 里写清该平台的加载机制细节（README 只指路到这里）。
   自检会拦住字段缺失、拼错、未知字段、`id` 重复或在 `LEDGER_TOKENS` 里缺失。
3. **建链接 / 建副本**——两个平台的自动化程度**不一样**：
   - **Windows（`role: junction`）**：跑 `sync-custom-skills.bat`。`ensure_junctions.ps1` **读清单**、按 `role=junction` 补链，并在父目录在而 `skills` 不在时自动建目录。
   - **WSL（`role: link`）**：**同步脚本不读清单**——`sync-wsl.sh` 里 `$HOME/custom-skills`、`$HOME/.agents/skills`、`$HOME/.claude/skills` 三个路径是写死的，全文对清单零引用。
     所以新增/改名 POSIX 目标必须**同时改 `sync-wsl.sh`**（把它加进去），或者手工建链并在 log 里留痕。
     "不要手工建链接"这条纪律只对 junction 目标成立——别把它套到 POSIX 面上。
   - `expect` 含 `manual` 时，还要把手工技能目录**复制**过去并改账（手工技能是真实副本）。
4. **逐链接校验**：目标末段 == 技能名，且目标下 `SKILL.md` 可达。只查"目录存在"会漏——曾有一批 junction 指向仓库根，`[ -d ]` 与对账双双假信号。
5. **对账**（两端）。登记了目标目录却还没建链时，`required: true` 会先报 `[WARN] surface missing` + 退出码 1，这是预期。
6. **加载实证**：见「技能 → 新增」第 7 条。
7. **落账与登记点**（按序）：
   1. `README.md` 目标一览——生成块，重跑 `--readme` 即可，**不要手改**。
   2. **仅当 `expect` 含 `manual`**：先给 `check_distribution.py` 的 `LEDGER_TOKENS` 加 `"<id>": "<token>"`，然后才能在账本表格的「所在目标」列写该 token。**顺序不能反**：先加账本行会立刻触发自检错误（`账本第 N 行…含未声明的目标 token`）。
      `expect` 不含 `manual` 时**两处都不用动**——动了反而会因"声明了 manual 但 id 不在 LEDGER_TOKENS"或未声明 token 而报错。
   3. POSIX 目标：改 `sync-wsl.sh`（见第 3 条）。
   4. `log.md` 与版本表：见「落账」。
   5. `~/AGENTS.md` 的技能表与本改动**无关**（它只列技能，不列目标）。

### 下线

1. **先看清单**：`python3 scripts/check_distribution.py --retire <id>`（只打印、绝不删除；**必须在删清单条目前跑**，否则报未知目标）。
2. **同步销账**：清单条目、`check_distribution.py` 的 `LEDGER_TOKENS`（若该目标有 manual 池）、`manual-skills.md` 表格的「所在目标」列、`README.md`（生成）、POSIX 目标还要清 `sync-wsl.sh` 里的对应代码。
3. **清盘**：只删「目标落在本仓库或 `LLMWiki/skills` 之下、且已不解析为技能」的链接；**手工技能副本属用户内容**，确认后删除或移出账本。
4. **验证**：对账输出里不再出现该目标；重启工具确认它没有被自带管理器物化回来。
5. **落账**：见「落账」；`~/AGENTS.md` 的 Skill 管理章节同步（手写，无脚本可查）。

---

## 手工技能

「手工技能」= 人工放置、没有仓库来源的第三方技能。在 Windows 各目标是**真实副本**（不是链接），账本 = `manual-skills.md`。

### 入账

1. 把技能目录复制到目标 skills 下。
2. 账本加一行：`名字 | 来源 | 一句话 | 更新时间 | 所在目标`。
   - 名字在锁文件 `~/.agents/.skill-lock.json` 里时，**来源以锁文件为准**（取 `sourceUrl`）。
   - 不在锁文件里就写清来源；实在查不到写「来源不详」，不要留空。
3. 对账（两端）：该名字应从「多余」变成「有账」。

### 恢复

工具面板里的删除是**目标级**的：它会连本体系的链接与手工副本一起删掉。善后顺序：

1. 先跑 `ensure_junctions.ps1`（Windows）或 `sync-wsl.sh`（WSL）把本体系的链接补回来。
2. 手工技能没有仓库源，只能从**另一个目标**复制回来（源损坏时从上游重装）。
3. 逐条对账本核对，别漏。

### 注意

- 手工技能会漂移（同一名字在不同目标可能是不同版本），没有自动修复，只能靠对账点名。
- 工具自带市场/云端管理的条目不属本体系：对账只会把它们列为「多余」提醒，不删除。要清就去工具自己的界面删。

---

## 跨端同步

1. 任一端编辑 → commit + push。
2. 他端 pull，然后两端各跑一次同步脚本。
3. **脏树守卫**：任何未提交改动（含未跟踪文件）都会让同步脚本拒绝运行——这是保护，不是故障。生成派生表之后也要提交，否则下一次同步会被自己挡住。
4. **同步脚本自己的成功信息不足信**：`sync-wsl.sh` 用 `|| true` 吞掉对账的非 0 退出码，且技能表生成器崩溃时仍会打印「完成」。**以对账输出为准，不以脚本退出码或结尾那句话为准。**
5. **冲突**：`--ff-only` 只保护、不仲裁。两端同时改同一文件会产生 git 冲突，手工解决，绝不让脚本自动覆盖。

---

## 落账

| 改动类型 | 要落到哪 |
|---|---|
| 常规技能增删改（自建） | **不需要人工写日志**——派生表由脚本生成，对账输出就是记录 |
| 新增 / 下线分发目标、判定语义变化、约定变更 | LLMWiki 的 `log.md` 追加一条，并在 `wiki/syntheses/skill-maintenance-workflow.md` 的版本表加一行 |
| 本仓库（custom-skills） | **没有 `log.md`**——别去找；本仓库的记录就是 git 历史 + 生成块 |
