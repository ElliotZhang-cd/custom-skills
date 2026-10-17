# 自建与第二个来源用链接分发，第三方在各面是真实副本

自建技能与 `maintaining-llm-wiki` 在所有分发目标上一律是**链接**（WSL 两级符号链接、Windows junction），指向 clone 与 LLMWiki 源目录；第三方技能在各面上是**真实副本**——WSL 侧由 skills CLI 直接落盘到存储面，Windows 侧由 CLI 物化到它认识的 agent 目录，认识不到的面（`dsh` / `workbuddy`）则人工复制并由 `manual-skills.md` 登记。

## Considered Options

- **全部用链接**：自建可以（源头在 git，链接就是唯一事实），第三方不行——它由 `npx skills` 管理，CLI 自己会往各 agent 目录物化真实副本，用链接等于跟它的物化机制抢同一批路径；且 `dsh` / `workbuddy` 不在 CLI 的 agent 表里，没有"CLI 会物化"这回事，链接也没有可指的稳定来源。
- **全部用拷贝**（2026-09-03 v6.1 之前的 robocopy）：改名/退役后残留无人清理（08-21 列表僵尸事故），改动要两处三面复制。
- **链接 + 副本混合**（选定）：自建只有一份，免疫副本漂移；第三方接受副本漂移，用登记表 + 对账点名来管。

## Consequences

- **自建技能绝不进入 skills CLI 锁文件**：对自建跑 `npx skills update` 会把链接换成 GitHub 拷贝并覆盖本地修改。这是本决定的直接约束，不是一个独立决定。
- 严禁向 junction 目标 robocopy/复制（会把仓库复制进自己）。
- 第三方的副本漂移只能靠「对账点名 + 人工裁决」发现，没有自动修复。
- 第三方存储面**按平台各有一份**（WSL `~/.agents/skills`、Windows `%USERPROFILE%\.agents\skills`，见 `docs/adr/0004`）；面里的条目是真实目录，由 CLI 维护。
- 工具自带的市场机制可以覆盖或顶替我们的链接——这正是 `[STALE]` 判定存在的原因。
