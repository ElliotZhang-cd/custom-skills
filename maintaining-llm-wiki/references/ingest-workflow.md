> 当前约定，与用户共同迭代中。如遇不适用情况，向用户提议修改。

# Ingest 入库流程

## 步骤

1. **捕获来源**
   - 外部 URL / 文本 → 尽量保存为 raw Markdown。
   - 非 Markdown 资料 → 先转 Markdown 再入库。
   - raw 不引入 frontmatter；来源 URL 写在 wiki `sources` 或 raw 正文首部。
   - 无法保存 raw 的外部 URL → 在来源段注明“未存档”。

2. **读源** → 画逻辑链/画像骨架（见 `references/note-format.md` 蒸馏规范 1）→ 简述核心 takeaways（2-3 句）→ 用户说“直接处理”时跳过确认。

3. **定位** → 类型判定 + 先 grep 去重；默认“先更新，后新建”；比对相关页已有断言，冲突按矛盾流程处理。

4. **写页面** → 按 `references/note-format.md` 创建；确保「一句话」≤100 字；entity 填 `entity_type`，synthesis 填 `coverage`；frontmatter `sources` 填 `[]` 占位，由 `scripts/sync_sources.py` 生成。

5. **完稿来源边界汇报** → 明确说明：
   - 哪些核心内容直接来自 raw/URL
   - 哪些是必要的背景补充
   - 哪些是原创观察/综合分析
   - 无来源支撑的核心断言必须补来源或删除。

6. **交叉链接** → 只对强关联建链（横纵分类法，见 `references/note-format.md`「链接规则」）；新链必须能回答“纵向还是横向”并通过跳转增益测试；目标页相关段满 10 条时单向自动豁免；每页「相关」≤10 条。

7. **收尾写入** → 运行 `scripts/gen_index_tables.py` 重建三表 + 原始资料表 → 运行 `scripts/wiki_sync.py`（sync_sources + rebuild_tags + update README）→ 追加 `log.md`。

8. **git 提交** → `git add -A && git diff --cached --stat` → 确认变更符合预期后 `git commit -m "[ingest] 标题"`。

## 处理异常

- **矛盾**：机械矛盾（口径/数字/标题不一致）→ 直接修复 + log 记录；语义矛盾（来源观点冲突）→ 不覆盖，保留双方 + frontmatter `contested: true` + 告知用户。
- **同 URL 重入库**：先与 `git show HEAD:raw/对应文件` 比对，有差异先报告。
- **不完整**：标注「待补充」+ `status: incomplete`，不强下结论。
- **删除/归档/重命名**：必须用户确认，并展示影响范围。

## 验收标准

- ✅ 页面符合 `references/note-format.md`
- ✅ 页面符合蒸馏规范：核心内容全覆盖、逻辑链完整、自包含，「一句话」≤100 字且可解析
- ✅ 完稿有来源边界汇报
- ✅ `entity_type` / `coverage` 完整
- ✅ sources 由 sync_sources 生成；index + log + README 已同步
- ✅ `wiki_sync` 无 diff + `lint_check` 零 ERROR
- ✅ 规则未覆盖的情形 → 停下，向用户说明现状与选项，等确认后再继续
