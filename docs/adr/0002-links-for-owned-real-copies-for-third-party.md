# 自建与第二个来源用链接分发，第三方在 Windows 用真实副本

自建技能与 `maintaining-llm-wiki` 在所有分发目标上一律是**链接**（WSL 两级符号链接、Windows junction），指向 clone 与 LLMWiki 源目录；第三方技能在 Windows 各目标是**真实副本**（由 `manual-skills.md` 登记），在 WSL 存储面则是 skills CLI 直接落盘的真实目录。

## Considered Options

- **全部用链接**：Windows 需要一个统一的第三方存储面才可指，而那个面正是 ADR-0004 禁止存在的 `~/.agents/skills`；且第三方由 CLI 管理，链接会被 `npx skills update` 换成拷贝。
- **全部用拷贝**（2026-09-03 v6.1 之前的 robocopy）：改名/退役后残留无人清理（08-21 列表僵尸事故），改动要两处三面复制。
- **链接 + 副本混合**（选定）：自建只有一份，免疫副本漂移；第三方接受副本漂移，用登记表 + 对账点名来管。

## Consequences

- **自建技能绝不进入 skills CLI 锁文件**：对自建跑 `npx skills update` 会把链接换成 GitHub 拷贝并覆盖本地修改。这是本决定的直接约束，不是一个独立决定。
- 严禁向 junction 目标 robocopy/复制（会把仓库复制进自己）。
- 第三方的副本漂移只能靠「对账点名 + 人工裁决」发现，没有自动修复。
- 工具自带的市场机制可以覆盖或顶替我们的链接——这正是 `[STALE]` 判定存在的原因。
