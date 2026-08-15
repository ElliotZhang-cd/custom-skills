---
name: maintaining-llm-wiki
description: 维护 LLM Wiki 知识库（入库/查询/lint/派生同步/生命周期）。当用户提到“知识库”“入库”“ingest”“wiki”“处理文章”“检查/审计知识库”“基于知识库制作/总结/提炼内容”时使用。
---

# Maintaining LLM Wiki — 知识库维护

## 一句话

> LLM Wiki 是一套以 Markdown 为载体、LLM 为维护者、人类为监督者的知识管理模式：提前编译知识，而非临时检索合成。本 Skill 负责让 LLM 安全、一致、可溯源地把 raw 编译成结构化 wiki，并持续维护 index/log/质量。

## 适用边界

**做：**
- 入库：把新 raw 编译成或更新 wiki 页面
- 查询：基于 wiki 回答并标注 `[[wikilink]]` 来源
- Lint：机械 + 语义健康检查
- 派生同步：重建 index / tags / README
- 生命周期：重命名、废弃、归档、删除（需确认）
- 基于知识库制作 PPT / 报告 / 总结

**不做：**
- 不修改 raw 内容
- 不自动删除用户内容
- 不把临时聊天内容写入 wiki
- 当前不引入向量库 / 重检索

## 路径解析

- 知识库根目录：Windows `%USERPROFILE%\Documents\LLMWiki`；WSL `/mnt/c/Users/<Windows用户名>/Documents/LLMWiki`
- 若 skill 已合并至 `LLMWiki/skills/maintaining-llm-wiki`，脚本自动用相对路径定位根目录
- 脚本运行：WSL `python3 scripts/xxx.py`，Windows `python scripts\xxx.py`

## 硬约束

1. **raw 只读，且只存 Markdown** — 不修改、不删除 raw；非 Markdown 先转 Markdown 再入库
2. **用户内容不碰** — 删除/归档/重命名必须用户确认
3. **事实有来源** — 核心断言要链接到 raw 或外部 URL
4. **变更后更新 index + 追加 log** — 纯读操作除外
5. **页面必须结构化** — 有「一句话」≤100 字；entity 有 `entity_type`；synthesis 有 `coverage`
6. **禁止派生字段** — 不写 `updated` / `source_count`

## 工作流入口

| 操作 | 触发词 | 加载 |
|------|--------|------|
| Ingest | “入库”“ingest”“处理文章” | `references/ingest-workflow.md` |
| Query | 提问 / 分析 / 对比 | `references/query-workflow.md` |
| Lint | “检查”“lint”“审计” | `references/lint-workflow.md` |
| 派生同步 | 重建派生数据 | `scripts/wiki_sync.py` |
| 生命周期 | 重命名 / 废弃 / 归档 / 删除 | `references/ingest-workflow.md` + `references/lint-workflow.md` |
| 安全 / 健康 | 密钥检查 / git 健康 | `scripts/check_secrets.py`、`scripts/check_repo.py` |

## 核心规则摘要

- index 简述从页面「一句话」自动提取，不手工维护
- 页面格式：标题 → 一句话 → 要点 → 相关 → 来源
- 相关链接 ≥2 为建议；少于 2 报 `[I]`，不强制
- `contested: true` 页面由 lint 列出，等待人类裁决
- 外部 URL 默认尽量保存 raw Markdown 副本
- 完全过时页面移入 `_archive/`；仍可参考的标 `status: deprecated`
- 每次完整 lint 必须输出语义检查报告
- 新会话首次操作前先读 `README.md` / `index.md` / `log.md`

## 质量标准

- [ ] `lint_check.py` 0 ERROR
- [ ] 页面符合 `references/note-format.md`
- [ ] 一句话可解析且 ≤100 字
- [ ] `entity_type` / `coverage` 完整
- [ ] `sources` 与正文来源段一致
- [ ] Ingest 完稿有来源边界汇报
- [ ] 变更已写 log，且已提交

## Gotchas

- raw 不引入 frontmatter；来源 URL 写在 wiki `sources` 或 raw 正文首部
- 禁止手写 index 摘要；由 `gen_index_tables.py` 从「一句话」生成
- 不要为凑相关链接数制造弱关联
- 不要凭模型记忆写页面；必须基于 raw/URL，并汇报来源边界
- 脚本要双平台可用：路径用正斜杠，使用 Python 标准库
- 删除/归档前必须展示影响范围并等用户确认

## References

- `references/pitfalls.md` — 必读踩坑
- `references/note-format.md` — 页面格式 / 蒸馏 / 链接规则
- `references/ingest-workflow.md` — 入库流程
- `references/query-workflow.md` — 查询 / 回存
- `references/lint-workflow.md` — lint 流程与报告
- `references/log-format.md` — 日志格式

## 协同进化

遇到不适用或更优模式 → 向用户提议 → 用户同意后更新 SKILL.md / references / scripts → log.md 记录：
`## [日期] lint | SKILL.md — 更新了X规则`

