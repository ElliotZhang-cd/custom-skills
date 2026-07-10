---
name: llm-wiki-maintenance
description: Use when the user mentions 知识库 or knowledge-base/knowledge base or llm-wiki/llm wiki.
---

# LLM Wiki 维护

知识库根目录：`C:\Users\elliot\Documents\LLMWiki`（操作时转 `/mnt/c/...`，`\` → `/`）

Karpathy 三层 Wiki：`raw/`（只读来源）→ `wiki/`（concepts/ entities/ syntheses/）→ 本文件（schema）。

## 1. 路径映射

AGENTS.md 内路径为 Windows 格式。所有文件操作前先转写：
```
C:\ → /mnt/c/
\   → /
```
示例：`C:\Users\elliot\Documents\LLMWiki\wiki\concepts\rag.md` → `/mnt/c/Users/elliot/Documents/LLMWiki/wiki/concepts/rag.md`

## 2. 会话感知

本会话**首次** wiki 操作 → 读 `index.md` + `log.md` (tail -5) 建立上下文。
同会话再次触发 → 跳过，直接进入操作。

## 3. 目录结构 + 硬约束

```
raw/（只读）         → configs/  logs/  reference/  webpages/  projects/
wiki/（读写）         → concepts/  entities/  syntheses/
index.md（内容目录）   |  log.md（操作日志）
```

1. **raw/ 只读** — 不修改、不删除 raw/ 中的任何文件
2. **用户创建的内容不碰** — 不修改、不删除
3. **事实性声称必须有来源** — 链接到 raw/ 文件或外部 URL
4. **文件变更后更新 index.md + 追加 log.md** — 纯读操作（简单查询）除外

## 4. Ingest（入库）★ 高频

触发："入库""处理""加入知识库""ingest"

1. 读源 → 简述核心 takeaways（2-3 句）→ 确认理解方向。用户说"直接处理"/"批量处理"时跳过确认
2. 创建/更新 wiki 页面：
   - 概念 → `concepts/`  |  工具/人物/组织 → `entities/`  |  对比/综述 → `syntheses/`
   - 新页面先 grep 去重。格式见 §7
3. 更新 `index.md` 对应表格 + 标签索引
4. grep 跨页关键词 → 已有页面「相关」段添加 `[[wikilink]]`
5. 追加 `log.md`（格式见 §8）
6. `git -C /mnt/c/Users/elliot/Documents/LLMWiki add -A && git -C ... diff --cached --stat`，确认后 `git -C ... commit -m "[ingest] 标题"`

**矛盾：** 不静默覆盖，保留双方 + frontmatter `contested: true` + 告知用户。
**不完整信息：** 标注「待补充」+ frontmatter `status: incomplete`，不强下结论。
**URL 源：** 先抓取内容（见 §9 子代理调度），再入库。

> 完成前确认：git diff 变更范围 | 未改 raw/ 或原始内容 | 新页面 grep 去重 | index 已更新 | wikilink 双向 | log 已追加

## 5. Query（查询）★ 中频

触发：提问/分析/对比（默认行为）

1. 读 `index.md` → grep 定位 → 深入阅读相关页面
2. 回答标注 `[[wikilink]]` 来源
3. **回存规则：**
   - 多源综合/对比分析/新发现 → 简述摘要 → 用户确认 → 写入 wiki → 执行 Ingest 步骤 3-6
   - 简单事实查询 → 不回存
   - 边界情况 → 快速确认

> 完成前确认：同上验证门

## 6. Lint（健康检查）★ 低频

触发："检查""lint""审计""健康检查"

读取 `references/lint-guide.md`，按其中的批量原则 + 6 项检查表执行。
报告末尾追加「建议方向」。**不自动删除任何内容。** 修复前需用户确认。
发现矛盾按 §4 矛盾处理执行。

> 完成前确认：同上验证门 + 工具调用参数中无 `C:\` 残留

## 7. 笔记格式（精简）

正文固定 5 节（顺序不可调换）：

| 顺序 | 章节 | 要求 |
|------|------|------|
| 1 | `# 标题` | 清晰具体 |
| 2 | `## 一句话（费曼摘要）` | 引用块，≤200 字。类比/比喻解释核心思想 |
| 3 | `## 要点` | 分条列出，每条一句话 |
| 4 | `## 相关` | `[[wikilink]]` + 一句关联说明，≥2 条 |
| 5 | `## 来源` | 链接到 raw/ 文件或外部 URL |

文件命名：kebab-case 英文（`agent-harness.md`），专有名词保留大小写（`Hermes-Agent.md`）。

> 完整 frontmatter 模板（含可选字段 `contested`/`status`/`updated`/`source_count`）、命名示例、自检清单 → `references/note-format.md`

## 8. 日志格式

```
## [YYYY-MM-DD] type | 标题
- 摘要：一句话概述
- 创建页面：`wiki/...`（如有）
- 更新页面：`...`（如有）
- 标签：#tag1 #tag2
```

操作类型：`ingest` | `query` | `lint`。按时间顺序追加在对应日期末尾。

> log.md 超过 500 行时：最旧条目移至 `raw/logs/archive-YYYY-MM.md`，主文件保留最近 30 条。归档后在 index.md 原始资料表添加归档文件条目。

## 9. 子代理调度

| 条件 | 策略 |
|------|------|
| wiki < 100 页 | Lint 直接执行（当前 ~42 页） |
| wiki ≥ 100 页 | Lint 各检查项并行子代理 |
| 任意规模 · 全文搜索 | 1 子代理 grep，只返回匹配摘要 |
| URL 抓取入库 | 1 子代理抓取 + 摘要，主会话写入 wiki |

## 10. 协同进化

操作中观察到摩擦点或更优模式 → 向用户提议改进 → 用户同意后更新本文件 → log.md 记录：
`## [日期] lint | SKILL.md — 更新了X规则`

## 11. 风格

简体中文。简洁专业，无废话。专有名词保留原文。代码块标注语言。

## 12. 参考文件索引

| 文件 | 何时读 |
|------|--------|
| `references/lint-guide.md` | 用户说"检查"/"lint"/"审计"/"健康检查" |
| `references/note-format.md` | 创建新页面需完整 frontmatter 模板 / 自检时 |
| `references/pitfalls.md` | 操作出错 / 准备记录新踩坑时 |

日常操作不需 references/。
