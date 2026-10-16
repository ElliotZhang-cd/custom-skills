# 四类操作的分步流程

命令里的 `scripts/…` 都相对仓库根。Windows 用 `python`，WSL 用 `python3`。

---

## 技能

### 新增（自建）

1. 在任一 clone 建 `<name>/SKILL.md`（内容自己写，或先转 `authoring-skills`）。
2. `git add -A && git commit -m "[skill] 说明"` → push。**push 等于发布**；投影目标里的任何改动都不算数。
3. 他端 `pull`，然后**两端各跑一次同步**：`sync-custom-skills.bat` / `bash scripts/sync-wsl.sh`。
   自建技能不需要登记进清单——「仓库即列表」：同步脚本扫描仓库根下含 `SKILL.md` 的目录自动建链接。
4. 刷新派生表：`python3 scripts/gen-skills-table.py`（AGENTS.md，仅 WSL）与
   `python3 scripts/gen-skills-table.py --readme README.md`（README，两端可跑）。
5. 对账（两端）→ 退出码 0。
6. **加载实证**：在工具里真的看到。注意区分「模型技能目录」与 `/` 命令面板——
   技能自己声明 `disable-model-invocation: true` 时只进后者，属预期，不是同步缺口。
7. `log.md` 追加一条。

### 改名

改名 = 退役旧名 + 新增新名的**同一次提交**（同一次同步里清旧链、建新链，避免中间态）。

1. 旧目录改名/删除、新目录建好，同一次 commit + push。
2. 两端同步。
3. **查同名冲突**：新名字若与第三方技能同名，对账会报 `[CONFLICT]` —— 必须改名，不能共存。
4. 清残留：对账若报 `[EXTRA]`（本体系僵尸）或 `[UNK ]`（非本体系残留），逐条确认后手工删。
   同步脚本只清「目标落在本仓库 / LLMWiki 之下、且已不解析为技能」的链接，其余不动。
5. 刷新派生表 + `log.md`。
6. 若旧名也在 `manual-skills.md` 里（手工技能同名），一并改账。

### 退役 / 删除（自建）

1. 删仓库目录 → commit + push。
2. 两端同步：本体系的链接会被自动清掉（`ensure_junctions.ps1` 的清理、`sync-wsl.sh` 的失效链清理）。
3. 对账确认该名字不再出现在任何目标；若有 `[EXTRA]`/`[STALE]` 残留，确认后手工删。
4. 若该技能曾在 AGENTS.md 技能表里，刷新派生表即可（表是生成的）。
5. `log.md` 记一条，写清"为什么退役"。

### 修改内容（自建）

内容由人改；本技能只管"改完之后"。1) 改 `SKILL.md` 或 references → 2) commit + push → 3) 他端 pull（**不用**重建链接，链接指的就是仓库）→ 4) `description` 若变了，刷新派生表（技能表里的描述是生成的）→ 5) `log.md`。

---

## 分发目标

「分发目标」= 某个 agent 平台加载技能的目录。声明在 `scripts/distribution-targets.json`，那是**唯一**的"应该有什么"的表达。

### 新增

1. **先查证加载机制**（读 vendor 文档或代码，不靠猜）：扫描哪些根、优先级 rank、是否读 `~/.claude/skills`、是否跟随 junction/符号链接、frontmatter 规则、是否有 `disable-model-invocation` 一类开关、watcher 是否热加载、**是否自带技能管理器**（会覆盖或复活技能）。据此再定路径与 `role`——**能链接就不复制**。
2. **登记清单**：加一条 `{id, platform, relpath, expect, role, required, note}`。
   - `id` 小写 token，同时也是账本「所在目标」列的词表。
   - `platform` 取 `win` / `posix`：**漏写会让这个目标在 Windows 端被静默剔除**。
   - `expect` 取 `selfbuilt` / `mllw` / `thirdparty` / `manual` 的子集。
   - `role` 取 `junction` / `link` / `storage`：补链脚本只处理 `junction`，对账用它划定"被顶替"的范围。
   - `required`：本机在装则 `true`；目标目录缺失会计入退出码 1。
   - `note` 里写清该平台的加载机制细节（README 只指路到这里）。
   自检会拦住字段缺失、拼错、未知字段、`id` 重复或在 `LEDGER_TOKENS` 里缺失。
3. **建链接 / 建副本**：Windows 跑 `sync-custom-skills.bat`（按白名单补链，工具懒创建技能根时脚本会建目录）；WSL 跑 `sync-wsl.sh`。`expect` 含 `manual` 时，还要把手工技能目录**复制**过去并改账（手工技能是真实副本）。
4. **逐链接校验**：目标末段 == 技能名，且目标下 `SKILL.md` 可达。只查"目录存在"会漏——注册的 junction 曾指向仓库根，`[ -d ]` 与对账双双假信号。
5. **对账**（两端）。
6. **加载实证**：见上「新增技能」第 6 条。
7. **落账**：README 目标一览（生成）、`log.md`；若该平台需要人手工放置技能，`manual-skills.md` 表头的「现存目标」也要补上。

### 下线

1. **先看清单**：`python3 scripts/check_distribution.py --retire <id>`（只打印、绝不删除；**必须在删清单条目前跑**，否则报未知目标）。
2. **四处同步销账**：清单条目、`check_distribution.py` 的 `LEDGER_TOKENS`（若该目标有 manual 池）、`manual-skills.md` 的「所在目标」列与表头、`README.md`（生成）。
3. **清盘**：只删「目标落在本仓库或 `LLMWiki/skills` 之下、且已不解析为技能」的链接；**手工技能副本属用户内容**，确认后删除或移出账本。
4. **验证**：对账输出里不再出现该目标；重启工具确认它没有被自带管理器物化回来。
5. **落账**：`log.md` 写明退原理由；`~/AGENTS.md` 的 Skill 管理章节同步（手写，无脚本可查）。

---

## 手工技能

「手工技能」= 人工放置、没有仓库来源的第三方技能。在 Windows 各目标是**真实副本**（不是链接），账本 = `manual-skills.md`。

### 入账

1. 把技能目录复制到目标 skills 下。
2. 账本加一行：`名字 | 来源 | 一句话 | 更新时间 | 所在目标`。
   - 名字在锁文件 `~/.agents/.skill-lock.json` 里时，**来源以锁文件为准**（取 `sourceUrl`）。
   - 不在锁文件里就写清来源；实在查不到写「来源不详」，不要留空。
3. 表头的「现存目标」若多了/少了一个目标，同步改。
4. 对账（两端）：该名字应从「多余」变成「有账」。

### 恢复

工具面板里的删除是**目标级**的：它会连本体系的链接与手工副本一起删掉。善后顺序：

1. 先跑 `ensure_junctions.ps1`（Windows）或 `sync-wsl.sh`（WSL）把本体系的链接补回来。
2. 手工技能没有仓库源，只能从**另一个目标**复制回来（源损坏时从上游重装）。
3. 逐条对账本核对，别漏。

### 注意

- 手工技能会漂移（同一名字在不同目标可能是不同版本），没有自动修复，只能靠对账点名。
- 工具自带市场/云端管理的条目（`*__skillhub`、云管技能）不属本体系：对账只会把它们列为「多余」提醒，不删除。要清就去工具自己的界面删。

---

## 跨端同步

1. 任一端编辑 → commit + push。
2. 他端 pull，然后两端各跑一次同步脚本。
3. **脏树守卫**：任何未提交改动（含未跟踪文件）都会让同步脚本拒绝运行——这是保护，不是故障。
4. **冲突**：`--ff-only` 只保护、不仲裁。两端同时改同一文件会产生 git 冲突，手工解决，绝不让脚本自动覆盖。
5. 同步脚本各自做的六件事（顺序固定）：脏树守卫 → `git pull --ff-only` → 清死链接 + 建缺失链接 → 刷新派生表 → 对账 → 备份锁文件快照（WSL）。
