# analyzing-bigfive

基于 BFI-2（Big Five Inventory-2 中文修订版）维度与子维度分数做大五人格分析，生成来访者视角 HTML 报告（单人 / 双人伴侣适配）。使用者是心理咨询师，读者是无心理学基础的来访者。

## 触发

用户提供 5 维度 + 15 子维度的**原始分**（来自 bfi2_interactive.html 复制/导出），或要求 BFI-2 报告、大五人格分析、人格剖面分析、压力/职业/人际模式分析、伴侣大五匹配。

## 结构

```
analyzing-bigfive/
├── SKILL.md                        # 工作流与规则入口（agent 读这个）
├── README.md                       # 本文件（人类维护者导航）
├── references/
│   ├── scoring-interpretation.md   # 原始分→z 计算、方向规则、等级分档、常模来源
│   ├── facet-analysis.md           # 15 子维度含义、矛盾组合解读表
│   ├── applied-analysis.md         # 职业倾向（RIASEC 参考）、压力应对、人际关系
│   ├── couple-dynamics.md          # 双人报告：相似度、高风险组合、伦理声明
│   ├── html-templates.md           # 报告 CSS/图表/章节结构/输出规范
│   ├── writing-style.md            # 通俗化写作规范、禁用词、证据标签、固定文本块
│   └── bfi2_norms_cn.json          # 中国常模数据（唯一常模真相源）
├── scripts/lint_report.py          # 报告质量闸门（四锚点 z 一致性等）
├── examples/bfi2_sample.html       # 报告范式与 lint 通过基线
└── evals/evals.json                # 6 个回归用例（方向翻转/询问清单/双人/扁平/极端）
```

## 真相源链路

1. **原始分**：由 bfi2_interactive.html 产生（本 skill 不做 60 题计分）。
2. **z 分**：skill 按 `references/scoring-interpretation.md` §1.2 用内置中国常模计算；输入中的 z/等级/M/SD 一律忽略。
3. **方向约定**：第 4 域按「情绪稳定性」方向（ES 输入直接算、负性情绪输入确认后取反）；焦虑/抑郁/易变子维度恒为本义方向（高分 = 更敏感）。
4. **等级**：按 §2.1 五档（-0.5 归"中等偏低"，+0.5 归"中"）。

## 本机专属配置（换机器需改）

- 报告输出目录：`C:/Users/elliot/Desktop/relations/BFI2/`（Windows、正斜杠）
- 计分输入来源页面：`C:/Users/elliot/Desktop/relations/data/bfi2_interactive.html`

## 明确不做

见 SKILL.md「Out of scope」：不从原始答题计分、不做心理诊断、不给职业决策结论、不做 MBTI 类型学、不用于招聘/婚恋决策、不做多语言。
