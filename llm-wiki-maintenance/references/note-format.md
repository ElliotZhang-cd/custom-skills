# 笔记格式完整模板

## Frontmatter

```yaml
---
type: concept | entity | synthesis
tags: [标签1, 标签2]
created: YYYY-MM-DD
sources: [raw/...]     # 与正文「来源」段一一对应（含外部 URL）
# 可选字段：
# updated: YYYY-MM-DD
# source_count: N
# contested: true（矛盾标记）
# contradictions: [页面slug列表]
# status: incomplete（信息不完整）
---
```

## 正文 5 节（固定顺序）

| # | 章节 | 要求 |
|---|------|------|
| 1 | `# 标题` | 清晰具体 |
| 2 | `## 一句话（费曼摘要）` | 引用块，≤200 字。用类比、比喻解释核心思想。假设读者是聪明的外行 |
| 3 | `## 要点` | 分条列出，每条一句话 |
| 4 | `## 相关` | `[[wikilink]]` + 一句关联说明，≥2 条 |
| 5 | `## 来源` | 链接到 raw/ 文件或外部 URL |

## 文件命名

kebab-case 英文（`agent-harness.md`），专有名词保留大小写（`Hermes-Agent.md`）。

## 自检清单

- [ ] frontmatter 完整且 source_count 与来源段一致
- [ ] 费曼摘要 ≤200 字，非标题复述
- [ ] 章节顺序正确（摘要 → 要点 → 相关 → 来源）
- [ ] 来源指向 raw/ 中实际存在的文件
- [ ] 相关段 ≥2 条 wikilink
- [ ] 无 AI 腔（中文："值得注意的是""总的来说""综上所述""毫无疑问""极大地"；英文："delve""moreover""furthermore"）
- [ ] 文件名符合命名约定（kebab-case 英文，专有名词保留大小写，不含中文）
