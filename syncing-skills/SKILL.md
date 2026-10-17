---
name: syncing-skills
description: 维护和管理我的技能列表与各 agent 平台的分发，让每个平台加载到的技能与真相源保持一致。当用户说某平台看不到某技能、技能没生效、对账不绿，或要接入、弃用某个 agent 平台时使用。
---

# Syncing Skills

## 目标

维护和管理我的技能列表与 agent 分发：**技能有增添、删除、修改，或 agent 平台有新增、删除时，让每个平台加载到的技能跟着同步更新与分发**，并把「不一致」变成可判定、可复现的输出。

本技能从**已经写好的技能包**出发——管的是它们落到哪些平台、怎么同步、怎么对账、怎么退役。

## 工作流

1. **先判定输入属于哪一类**（四类来源与两个真相源见 `references/environment.md`）：
   - 自建技能的新增 / 改名 / 退役 / 改内容 → `references/workflows.md`「技能」
   - 第三方技能的引入 / 更新 / 卸载（`npx skills` 管的那些）→ `references/workflows.md`「第三方技能」
   - 人工放置的手工技能入账 / 恢复 → `references/workflows.md`「手工技能」
   - agent 平台的新增 / 下线 → `references/workflows.md`「分发目标」
   - 只是「对不齐 / 没生效」 → `references/reconciliation.md`
2. **先改声明层，再动投影层**：读 `scripts/distribution-targets.json`（声明有哪些目标、各自期望什么）与 `manual-skills.md`（手工技能的账），然后才动目录。
3. **两端各同步一次**：Windows 跑 `sync-custom-skills.bat`，WSL 跑 `bash scripts/sync-wsl.sh`——两者都读分发清单。push 只让另一端"可以拉"，不会让它自动生效；**只在一端同步时，另一端必然报 `[MISS]`，这是预期**。
4. **刷新派生表并再次提交**：`python3 scripts/gen-skills-table.py`（AGENTS.md，仅 WSL）与 `python3 scripts/gen-skills-table.py --readme README.md`（两端）。生成会改动文件、工作树变脏，而同步脚本有脏树守卫——不提交，下一次同步会被自己挡住。
5. **读对账结论**（判定分级与排查手册见 `references/reconciliation.md`）：失败必须清零；提醒逐条裁定——在用就登记进清单，不用就清理。
6. **落账**：常规技能增删改**不需要人工写日志**（派生表由脚本生成，对账输出就是记录）；只有体系级改动（新增/下线分发目标、判定语义变化）才要在 LLMWiki 的 `log.md` 记一条。本仓库没有 `log.md`。

## 成功标准

- 声明自检 0 错：清单字段无缺失/拼错，登记表「所在目标」列只出现已声明的 token。
- 两端对账退出码 0：没有缺失、没有损坏、没有被顶替、没有同名冲突。
- **两端都同步过**：单端改动会让另一端报 `[MISS]`，不算完成。
- 提醒项被逐条裁定过，而不是被忽略。
- 派生表（README 目标一览与技能表、AGENTS.md 技能表）与实际一致，且由生成脚本产出而非人工枚举。
- 新增目标有**加载实证**：在工具里真的看到该技能，而不是只看文件在。无法在工具里复核时，退化口径是"经每个目标的链接能读到 `SKILL.md`"，并把工具内复核留作下一步。

## 停止规则

- 声明层读不到、或自检报错：停下报错，**不要**手工建链接绕过——那会造出对账看不见的状态。
- 要删除分发目标里的条目（尤其是工作区外的目录）：先打印待清理清单并等确认。`--retire <id>` 只打印、绝不删除，且**只认分发目标 id**——传技能名会报未知目标（退出码 2）；技能退役的预览是对账输出本身（`[BRK ]` 死链 / `[EXTRA]` 僵尸）。
- **不要信同步脚本的退出码或结尾那句"完成"**：它把对账的非 0 退出码降级为警告，生成本身崩溃时也照样打印成功。以对账输出为准。
- 工作树脏：同步脚本会拒绝运行。先让人处理提交，不要绕过守卫；生成派生表之后要提交，否则下一次同步会被自己挡住。
- 技能内容本身有问题（写法、结构、触发语）：转 `authoring-skills`，不要在这里改。
- 知识库正文（入库 / 查询 / lint）：转 `maintaining-llm-wiki`。
- 工具自带的技能管理器把条目物化或复活了：那是它自己的账，去它的界面里删；本体系只负责把自己的链接与手工副本补回来。

## 约束

体系硬规则（禁止无账拷贝、禁止向 junction 目标复制、自建不进第三方 CLI 锁文件、各平台第三方仓库层只能由 npx 写）见 `README.md`；整体结构与不变量见 `docs/architecture.md`；为什么这样定见 `docs/adr/`。

## 验证

改完必须跑 `python3 scripts/check_distribution.py`（两端各一次）并确认退出码 0，再跑 `python3 scripts/gen-skills-table.py` 刷新派生表（`--readme` 两端可跑；默认模式仅 WSL 可跑，见 `references/environment.md`）。

## References

- [references/workflows.md](references/workflows.md) — 各类操作（自建 / 第三方 / 手工技能、分发目标）的分步流程与清单
- [references/reconciliation.md](references/reconciliation.md) — 对账输出怎么读、判定分级、排查手册
- [references/environment.md](references/environment.md) — 真相源与来源类别、本机路径、平台前提
