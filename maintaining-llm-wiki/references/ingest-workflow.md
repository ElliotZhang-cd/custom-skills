> 当前约定，与用户共同迭代中。如遇不适用情况，向用户提议修改。

# Ingest 入库流程

## 步骤

1. **读源** → 简述核心 takeaways（2-3 句）→ 用户说"直接处理"时跳过确认
2. **定位** → 类型判定 + 先 grep 去重；比对相关页已有断言，冲突即按矛盾流程处理（不覆盖，保留双方 + `contested: true` + 告知用户）
3. **写页面** → 按 `references/note-format.md` 创建（wikilink 规则见其顶部 ⛔ 提示）；新链 A→B 必须同时在 B 补回链；frontmatter `sources` 填 `[]` 占位，由 `scripts/sync_sources` 生成
4. **交叉链接** → grep 跨页关键词 → 已有页面「相关」段添加 `[[wikilink]]`，双向
5. **收尾写入** → 运行 `scripts/gen_index_tables.py` 重建三表 + 原始资料表（新页简述列标「待补简述」，顺手补写）→ 其他 index.md 内容 + log.md（格式见 `references/log-format.md`；日期取 `date +%F`，不凭记忆生成）
6. **派生同步** → `python3 scripts/wiki_sync.py`（sync_sources + rebuild_tags，自动修复派生数据）
7. **git 提交** → `git add -A && git diff --cached --stat` → 确认变更符合预期后 `git commit -m "[ingest] 标题"`

## 处理异常

- **矛盾**：不覆盖，保留双方 + frontmatter `contested: true` + 告知用户
- **不完整**：标注「待补充」+ `status: incomplete`，不强下结论

## 验收标准

- ✅ 页面符合 `references/note-format.md`
- ✅ sources 由 sync_sources 生成；index + log 已同步
- ✅ wiki_sync 无 diff + lint_check 零 ERROR
- ✅ 规则未覆盖的情形 → 停下，向用户说明现状与选项，等确认后再继续
