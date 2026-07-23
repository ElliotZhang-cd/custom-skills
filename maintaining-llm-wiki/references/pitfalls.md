# 踩坑记录（信噪比最高，操作前必读）

> 从真实失败中积累。记录新踩坑后，审视是否需要修改 SKILL.md 或 references/ 来预防同类问题。
> **新增踩坑需用户审批后才写入。**

## 已验证的踩坑

| 日期 | 问题 | 根因 | 预防机制 |
|------|------|------|---------|
| 2026-06-24 | sources 数组策略来回三次才确定 | 规则模糊，每次遇到差异都要重新判断 | sources 与来源段一一对应，纯机械规则（**已由 sync_sources.py 脚本强制**） |
| 2026-07-14 | syntheses 要点没有 ### 分组 | 没分析原文逻辑结构就开始罗列 | 动笔前先画逻辑链；自检后汇报偏差 |
| 2026-07-14 | 自检清单被跳过 | 清单太长，执行成本高 | 4项以内；改为"汇报偏差"而非硬性阻断 |
| 2026-07-14 | 要点每条超过2句话 | 没有区分"标签"和"解释" | 强制 `**标签**：解释` 格式 |
| 2026-07-14 | SKILL.md 过于臃肿 | 把所有规则塞进一个文件，违背渐进式披露 | 拆到 references/ 按需加载 |
| 2026-07-14 | 过度约束格式 | 违背 Karpathy "optional and modular" 原则 | 所有格式降级为"当前约定"，明确 co-evolve |
| 2026-07-14 | description 不是触发条件 | 模型无法判断是否该加载 skill | description 改为触发词列表 |
| 2026-07-20 | source_count/updated 根除后两次回潮 | "已根除"规则只写进 log.md 历史档案，ingest 上下文不可见，LLM 被 Obsidian 先验自动补全 | 禁止规则写在生成点（note-format.md 模板注释），不靠 checklist（**已由 lint_check.py 脚本绊线**） |
| 2026-07-21 | edit 工具 oldString 在 frontmatter 与正文重复时误匹配 | frontmatter 的 `sources:` 行与正文「来源」段含相同 URL，replace 命中 frontmatter，污染 YAML | 编辑前 grep oldString 全文确认唯一性；优先使用更长上下文锚定 |
| 2026-07-23 | git clone/push 超时，但 curl 能访问 GitHub | 环境变量 `HTTPS_PROXY` 存在，git-remote-https 不自动继承代理；直连 GitHub 不可达 | git 命令显式 `-c http.proxy=$HTTPS_PROXY -c https.proxy=$HTTPS_PROXY` |
