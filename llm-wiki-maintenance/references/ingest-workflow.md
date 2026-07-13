> 当前约定，与用户共同迭代中。如遇不适用情况，向用户提议修改。

# Ingest 入库流程

## 步骤

1. **读源** → 简述核心 takeaways（2-3 句）→ 用户说"直接处理"时跳过确认
2. **确定类型** → 概念 `concepts/` | 实体 `entities/` | 综述 `syntheses/`
3. **加载模板** → `references/note-format.md` 中的当前约定格式
4. **创建页面** → 按格式写，先 grep 去重
5. **自检** → 对照 `references/pitfalls.md` 中的常见错误模式检查
6. **汇报偏差** → 向用户报告自检发现的问题（如有），由用户决定是否修正
7. **交叉链接** → grep 跨页关键词 → 已有页面「相关」段添加 `[[wikilink]]`
8. **更新索引** → index.md 对应表格 + 标签索引
9. **追加日志** → log.md（格式见 `references/log-format.md`）
10. **git 提交** → `git add -A && git diff --cached --stat` → 确认后 `git commit -m "[ingest] 标题"`

## 处理异常

- **矛盾**：不覆盖，保留双方 + frontmatter `contested: true` + 告知用户
- **不完整**：标注「待补充」+ `status: incomplete`，不强下结论
