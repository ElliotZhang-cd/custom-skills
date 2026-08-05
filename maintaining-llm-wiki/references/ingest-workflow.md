> 当前约定，与用户共同迭代中。如遇不适用情况，向用户提议修改。

# Ingest 入库流程

## 步骤

1. **读源** → 画逻辑链/画像骨架（见 `references/note-format.md` 蒸馏规范 1）→ 简述核心 takeaways（2-3 句）→ 用户说"直接处理"时跳过确认
2. **定位** → 类型判定 + 先 grep 去重；比对相关页已有断言，冲突即按矛盾流程处理（不覆盖，保留双方 + `contested: true` + 告知用户）
3. **写页面** → 按 `references/note-format.md` 创建（wikilink 规则见其顶部 ⛔ 提示）；新链 A→B 必须同时在 B 补回链；frontmatter `sources` 填 `[]` 占位，由 `scripts/sync_sources` 生成；完成后执行完稿核对，输出偏差汇报（蒸馏规范 4）
4. **交叉链接** → 只对强关联建链（横纵分类法，见 `references/note-format.md`「链接规则」）：新链必须能回答"纵向（实例/前提支撑/延伸）还是横向（同类/对比/互补）"，并过跳转增益测试；答不出关系 = 不建链。双向回链仅限强关联；目标页相关段满 10 条时单向自动豁免（cap 规则），未满时的单向由 lint 报告后补回链/删除/录特例。每页「相关」段 ≤10 条，超出砍最弱
5. **收尾写入** → 运行 `scripts/gen_index_tables.py` 重建三表 + 原始资料表（新页简述列标「待补简述」，顺手补写）→ 其他 index.md 内容 + log.md（格式见 `references/log-format.md`；日期取本地当天 ISO 日期，不凭记忆生成）
6. **派生同步** → 在 skill 目录运行 `scripts/wiki_sync.py`（WSL 用 `python3`，Windows 用 `python`；sync_sources + rebuild_tags，自动修复派生数据）
7. **git 提交** → `git add -A && git diff --cached --stat` → 确认变更符合预期后 `git commit -m "[ingest] 标题"`

## 处理异常

- **矛盾**：机械矛盾（口径/数字/标题不一致）→ 直接修复 + log 记录；语义矛盾（来源观点冲突）→ 不覆盖，保留双方 + frontmatter `contested: true` + 告知用户
- **同 URL 重入库**：先与 `git show HEAD:raw/对应文件` 比对，有差异先报告（漂移检测不建脚本，人工比对成本为零）
- **不完整**：标注「待补充」+ `status: incomplete`，不强下结论

## 验收标准

- ✅ 页面符合 `references/note-format.md`
- ✅ 页面符合蒸馏规范：核心内容全覆盖、逻辑链完整、自包含，「一句话」为定义锚点，核对偏差已汇报
- ✅ sources 由 sync_sources 生成；index + log 已同步
- ✅ wiki_sync 无 diff + lint_check 零 ERROR
- ✅ 规则未覆盖的情形 → 停下，向用户说明现状与选项，等确认后再继续
