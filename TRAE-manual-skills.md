# TRAE 手动安装 Skill 清单

> 记录 Windows TRAE 全局技能目录 `C:\Users\elliot\.trae-cn\skills\` 中「手动安装」的 skill —— 即非 `sync-windows.bat` 自建分发、非 TRAE 内置/市场来源。目的：给 v4 对账体系覆盖不到的「手动第三方」区建账。

| 名字 | 来源 | 一句话介绍 | 更新时间 |
|---|---|---|---|
| grilling | github.com/mattpocock/skills | 可复用拷问原语（设计树 + 分轮问 frontier），被 grill-me / grill-with-docs 依赖 | 2026-08-23 |
| grill-me | github.com/mattpocock/skills | 拷问式访谈打磨计划/设计（内部调用 grilling） | 2026-08-23 |
| domain-modeling | github.com/mattpocock/skills | 构建打磨项目领域模型（CONTEXT.md/ADR），grill-with-docs 的依赖 | 2026-08-23 |
| grill-with-docs | github.com/mattpocock/skills | 拷问式访谈 + 顺带产出 ADR 和术语表（编排 grilling + domain-modeling） | 2026-08-23 |
| handoff | github.com/mattpocock/skills | 把当前对话压缩成交接文档 | 2026-08-23 |
| teach | github.com/mattpocock/skills | 在工作区内多会话教你新技能/概念 | 2026-08-23 |
| to-questionnaire | github.com/mattpocock/skills | 把答不了的决策转成问卷给别人填 | 2026-08-23 |
| wait-what | github.com/mattpocock/skills | 消息没落地时停止并用统一语言重述 | 2026-08-23 |
| writing-for-agents | github.com/mattpocock/skills | 给 agent 写文档（skills/AGENTS.md/CLAUDE.md） | 2026-08-23 |
| Humanizer-zh-main | humanizer-zh（具体仓库待确认） | 去除文本 AI 生成痕迹 | 2026-08-23 23:13 |

> 依赖说明：`grill-me` → `grilling`；`grill-with-docs` → `grilling` + `domain-modeling`。其余 skill 的引用文件（如 `teach` 的 `MISSION-FORMAT.md`、`writing-for-agents` 的 `SKILL-MECHANICS.md`、`domain-modeling` 的 `CONTEXT-FORMAT.md`）为其目录内文件，随目录整体复制，非独立 skill。
>
> 注：`grill-me`、`grilling` 此前已有 2026-08-12 散装版，本次（2026-08-23）随整套覆盖升级。