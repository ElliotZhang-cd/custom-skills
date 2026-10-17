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
- 本 skill 住在 custom-skills 仓库；脚本按 `$LLMWIKI_ROOT` → 平台默认路径定位 wiki 根目录
- 脚本运行：WSL `python3 scripts/xxx.py`，Windows `python scripts\xxx.py`

## 硬约束

1. **raw 只读，且只存 Markdown** — 不修改、不删除 raw
2. **用户内容不碰** — 删除/归档/重命名必须用户确认
3. **事实有来源** — 核心断言要链接到 raw 或外部 URL
4. **变更后更新 index + 追加 log** — 纯读操作除外
5. **页面必须结构化** — 有「一句话」≤100 字；entity 有 `entity_type`；synthesis 有 `coverage`
6. **禁止派生字段** — 不写 `updated` / `source_count`

## 停止规则

判断依据：出错成本是否可逆、影响面是否可控、信息是否充分。只有三类情况必须停下问用户：

1. **不可逆或影响面大的写操作** — 删除 / 归档 / 重命名 / 覆盖，以及批量修复多页面（含 push / 对外发布）：展示影响范围，等确认后执行
2. **来源间语义冲突** — 观点 / 断言互斥：保留双方 + 标 `contested: true`，按既定处置执行并告知用户，不自行选边（机械不一致如数字 / 口径 / 标题属格式修复，直接修并记 log）
3. **规则盲区** — 现有规则未覆盖的情形：说明现状与选项，等确认；禁止自行发明规则

其余情况（纯读、跑脚本、重建派生数据、单页格式修复）在 git 可回滚前提下直接做，做完汇报。

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
- 相关链接建议横纵强关联；入链 = 0 的真岛页报 `[I]`（入链 1-2 属常态，非缺陷）
- `contested: true` 页面由 lint 列出，等待人类裁决
- 外部 URL 默认尽量保存 raw Markdown 副本
- 完全过时页面移入 `_archive/`；仍可参考的标 `status: deprecated`
- 新会话首次操作前先读 `README.md` / `index.md` / `log.md`

## 质量标准

格式 / 结构 / 一致性由 `lint_check.py` + `wiki_sync.py` 机械强制，不在此列。以下三项脚本管不了，必须人工自检：

- [ ] Ingest 完稿有来源边界汇报（哪些来自 raw / URL，哪些是模型推断）
- [ ] 完整 lint 输出语义检查报告（细则见 `references/lint-workflow.md`）
- [ ] 变更已写 log，且已 commit

## Gotchas

- raw 不引入 frontmatter；来源 URL 写在 wiki `sources` 或 raw 正文首部
- 禁止手写 index 摘要；由 `gen_index_tables.py` 从「一句话」生成
- 不要为凑相关链接数制造弱关联
- 不要凭模型记忆写页面；必须基于 raw/URL，并汇报来源边界
- 脚本要双平台可用：路径用正斜杠，使用 Python 标准库

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

