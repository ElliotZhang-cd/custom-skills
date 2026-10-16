---
name: syncing-skills
description: 让每个 agent 平台加载到的技能列表与真相源保持一致：新增/改名/退役技能、登记或下线分发目标、手工第三方技能入账与恢复、跨端同步、对账与偏差排查。不评审技能内容的写法与结构（转 authoring-skills），不处理知识库正文（转 maintaining-llm-wiki）。当用户提到「某个工具里看不到某技能」「技能没生效」「对账不绿 / MISSING / STALE」「加一个新平台」「换了工具」「技能分发」「各平台技能列表对不齐」时使用。
---

# Syncing Skills

## 目标

让人在每个 agent 平台上看到的技能列表与真相源一致，并把「不一致」变成可判定、可复现的输出。

输入是**已经写好的技能包**——内容质量不归本技能管。本技能管的是：它落到哪、怎么分发、怎么对账、怎么退役。

## 工作流

1. **先判定输入属于哪一类**（四类来源与两个真相源见 `references/environment.md`）：
   - 自建技能的新增 / 改名 / 退役 → `references/workflows.md` 「技能」
   - agent 平台的新增 / 下线 → `references/workflows.md` 「分发目标」
   - 手工第三方技能的入账 / 恢复 → `references/workflows.md` 「手工技能」
   - 只是「对不齐 / 没生效」 → `references/reconciliation.md`
2. **先改声明层，再动投影层**：读 `scripts/distribution-targets.json`（声明有哪些目标、各自期望什么）与 `manual-skills.md`（手工技能的账），然后才动目录。
3. **两端各同步一次**：Windows 跑 `sync-custom-skills.bat`，WSL 跑 `bash scripts/sync-wsl.sh`。两者都做：脏树守卫 → `pull --ff-only` → 建链接/清死链接 → 刷新派生表 → 对账。push 只让另一端"可以拉"，不会让它自动生效。
4. **读对账结论**（判定分级与排查手册见 `references/reconciliation.md`）：失败必须清零；提醒逐条裁定——在用就登记进清单，不用就清理。
5. **落账**：`README.md` 的目标一览与技能表由生成脚本产出，不要手改；`log.md` 追加一条当日记录。

## 成功标准

- 声明自检 0 错：清单字段无缺失/拼错，账本「所在目标」列只出现已声明的 token。
- 两端对账退出码 0：没有缺失、没有损坏、没有被顶替、没有同名冲突。
- 提醒项被逐条裁定过，而不是被忽略。
- 派生表（README 目标一览与技能表、AGENTS.md 技能表）与实际一致，且由生成脚本产出而非人工枚举。
- 新增目标有**加载实证**：在工具里真的看到该技能，而不是只看文件在。

## 停止规则

- 声明层读不到、或自检报错：停下报错，**不要**手工建链接绕过——那会造出对账看不见的状态。
- 要删除分发目标里的条目（尤其是工作区外的目录）：先打印待清理清单并等确认。`--retire <id>` 只打印、绝不删除。
- 工作树脏：同步脚本会拒绝运行。先让人处理提交，不要绕过守卫。
- 技能内容本身有问题（写法、结构、触发语）：转 `authoring-skills`，不要在这里改。
- 知识库正文（入库 / 查询 / lint）：转 `maintaining-llm-wiki`。
- 工具自带的技能管理器把条目物化或复活了：那是它自己的账，去它的界面里删；本体系只负责把自己的链接与手工副本补回来。

## 约束

体系硬规则（禁止无账拷贝、禁止向 junction 目标复制、自建不进第三方 CLI 锁文件、Windows 不重建 `.agents/skills`）见 `README.md`；为什么这样定见 `docs/adr/`。

## 验证

改完必须跑 `python3 scripts/check_distribution.py`（两端各一次）并确认退出码 0，再跑 `python3 scripts/gen-skills-table.py` 刷新派生表（`--readme` 两端可跑；默认模式仅 WSL 可跑，见 `references/environment.md`）。

## References

- [references/workflows.md](references/workflows.md) — 四类操作的分步流程与清单
- [references/reconciliation.md](references/reconciliation.md) — 对账输出怎么读、判定分级、排查手册
- [references/environment.md](references/environment.md) — 真相源与来源类别、本机路径、平台前提
