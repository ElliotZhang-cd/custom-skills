---
name: maintaining-llm-wiki
description: 维护 LLM Wiki 知识库（入库/查询/lint/派生同步）。When the user mentions "知识库", "入库", "ingest", "wiki", "处理文章", or asks to add sources to the LLM Wiki, queries wiki content, requests to check/lint the wiki, or asks to 基于/从知识库制作、整理、总结、提炼内容（如根据知识库生成 PPT/报告/总结）。
---

# Maintaining LLM Wiki — 知识库维护

## 📍 路径解析规则（双平台自识别）

- **知识库根目录**：Windows `%USERPROFILE%\Documents\LLMWiki`（如 `C:\Users\elliot\Documents\LLMWiki`）；WSL 转 `/mnt/c/Users/<Windows用户名>/Documents/LLMWiki`
- **脚本**（scripts/*.py）：默认自动识别平台与根目录（共享 `scripts/wiki_paths.py`），零配置；也可显式传 `[wiki_root]` 覆盖
- **运行脚本**：在 skill 目录下执行——WSL 用 `python3 scripts/xxx.py`，Windows 用 `python scripts\xxx.py`

## 🔒 硬约束（4条，不可违反）

1. **raw/ 现有文件只读** — 现有文件不修改、不删除；允许新增（ingest 原始资料、日志归档）
2. **用户内容不碰** — 不修改、不删除
3. **事实有来源** — 链接到 raw/ 或外部 URL
4. **变更后更新 index + 追加 log** — 纯读操作除外

## 工作流入口（按需加载 details）

|操作|触发词|加载文件|
|-|-|-|
|**Ingest**|"入库""ingest""处理文章"|`references/ingest-workflow.md`|
|**Query**|提问/分析/对比|`references/query-workflow.md`|
|**Lint**|"检查""lint""审计"|`references/lint-workflow.md`|
|**派生同步**|重建派生数据|`scripts/wiki_sync.py`（= sync_sources + rebuild_tags）|
|**索引重建**|index 三表/原始资料表乱序或漏登|`scripts/gen_index_tables.py`（三表骨架自动，简述列 LLM 补写）|

> 备注：知识库有 GitHub remote（origin）。本机 `~/.gitconfig` 已配置 `http(s).proxy = http://127.0.0.1:7890`，直接 push/pull 即可；跑不通时可能的解法：显式 `-c http.proxy=<代理地址> -c https.proxy=<代理地址>`（注意 shell 的 `$HTTPS_PROXY` 通常为空，`-c http.proxy=$HTTPS_PROXY` 传空值会覆盖 .gitconfig 有效代理导致失败，代理地址要写实际值）；commit 为本地操作，无需代理。

## 🔁 协同进化（co-evolve）

操作中遇到规则不适用、或发现更优模式 → **向用户提议修改** → 用户同意后更新 SKILL.md 或 references/ 文件 → log.md 记录：
`## [日期] lint | SKILL.md — 更新了X规则`

> 当前 references/ 中的约定是**起点，不是终点**。根据领域和偏好与用户共同迭代。

## 必读（操作前）

`references/pitfalls.md` — 信噪比最高的踩坑记录

## 风格

简体中文，简洁专业，专有名词保留原文。

