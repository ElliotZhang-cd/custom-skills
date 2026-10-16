# Windows 上不设 `~/.agents/skills` 存储面

Windows 侧不得重建 `%USERPROFILE%\.agents\skills`（2026-09-03 已删除）：桌面版 DSH 的 skill-filesystem 会按固定 rank 扫 `<agentsHome>/skills`（rank 500）并把内容当技能加载；该目录曾是 2026-07-03 的冻结快照，脱离管理近两个月才被发现，其中 `maintaining-llm-wiki` 是缺三个工作流文件的旧架构。

## Consequences

- 这个决定的载体是一个**不存在的目录**，从代码里读不出原因。任何好心人（人或 agent）看到"缺少统一存储面"都会顺手建回来，并把过时内容喂给模型——所以它必须留在 ADR 里，而不是只靠铁律的口口相传。
- WSL 侧的 `~/.agents/skills` 是**存储面**（第三方真实存放地），与 Windows 的同名目录是两回事，两者不要相互"对齐"。
- 由于这个面不存在，Windows 端对账的第三方池结构性地为空——这在子集语义下不咬人（Windows 目标声明的是 `manual`，不是 `thirdparty`）。
