# analyzing-bigfive

基于 BFI-2（Big Five Inventory-2 中文修订版）维度与子维度分数做大五人格分析，生成来访者视角 HTML 报告。使用者是心理咨询师，读者是无心理学基础的年轻读者。**v3（2026-09-07）起单人报告为数据驱动模板**：固定骨架（`templates/report-template.html`）+ 一个 `REPORT` 数据块，暖纸色封面/雷达/百分位游标条视觉，全篇零术语、画面化文案。**双人（恋人）报告为 v3 关系工具书**：`templates/couple-report-template.html`（十章，讲差异翻译与相处协议，不评匹配分；规范见 `couple-template.md`）。

## 触发

用户提供 5 维度 + 15 子维度的**原始分**（来自 bfi2_interactive.html 复制/导出；单人一份或双人两份），或要求 BFI-2 报告、大五人格分析、人格剖面分析、伴侣大五差异工具书（v3 单人报告无职业/压力/人际独立章节）。

## 结构

```
analyzing-bigfive/
├── SKILL.md                        # 工作流与规则入口（agent 读这个）
├── README.md                       # 本文件（人类维护者导航）
├── templates/
│   ├── report-template.html        # v3 单人模板骨架（CSS/JS/图表固定，只换 REPORT 数据块）
│   └── couple-report-template.html # v3 双人模板骨架（十章关系工具书，浏览器端计算，换 P 分数 + COUPLE_CONTENT）
├── scripts/
│   ├── compute_scores.py           # 原始分 → z/百分位/五档/刻度；--couple 出 Δz/选桥/共鸣复算
│   └── lint_report.py              # 质量闸门（单人=注入值复算；双人=浏览器端契约+NORM对齐+选桥复算+双人禁词）
├── references/
│   ├── html-templates.md           # 单人：生成流程、REPORT schema、七章结构、输出与验证
│   ├── couple-template.md          # 双人：十章结构、COUPLE_CONTENT schema、选桥/共鸣契约、专属语气与安全边界
│   ├── design-spec.md              # 单/双共用：三层语义色板、五段百分位带、图形编码、打印、禁区
│   ├── writing-style.md            # 语气、句式骨架、禁词表、弱护栏规范
│   ├── interpretation-library.md   # 分数模式→文案素材库（初稿，待咨询师终审）
│   ├── scoring-interpretation.md   # 维度定义、五档百分位、方向规则、常模与文化提示
│   ├── facet-analysis.md           # 15 子维度含义、矛盾组合解读表
│   └── bfi2_norms_cn.json          # 中国常模数据（唯一常模真相源）
├── examples/
│   ├── bfi2_sample.html            # v3 单人基线（新版单人 lint PASS）
│   └── bfi2_sampleA_sampleB.html   # v3 双人基线（新版双人 lint PASS）
└── evals/evals.json                # 6 个回归用例（方向翻转/询问清单/双人/扁平/极端）
```

## 真相源链路

1. **原始分**：由 bfi2_interactive.html 产生（本 skill 不做 60 题计分）。
2. **单人 z/百分位**：`scripts/compute_scores.py` 读 `references/bfi2_norms_cn.json` 计算，注入 `REPORT`；lint 复算比对，不一致 FAIL。
3. **双人 z/百分位/Δz/选桥/共鸣**：模型只填原始分到 `P`，由双人模板内嵌 NORM 表**浏览器端计算**（`meta.norm` 声明用了哪套人群）；`compute_scores.py --couple` 供 Phase 0 回显、lint 复算选桥集合与 NORM 表逐值对齐 JSON。
4. **方向约定**：第 4 域一律按「情绪稳定性」方向（输入为交互页导出，脚本自动取 `scores.stability`、禁用 `scores.raw`）；焦虑/抑郁/易变子维度恒为本义方向（高分 = 更敏感）。
5. **档位**：百分位五档——远低 <10 / 偏低 <35 / 中间 <65 / 偏高 <90 / 远高 ≥90（scoring-interpretation §2.1）。
6. **视觉**：一切以 `design-spec.md` 为准；两份模板 `:root` 色值须一致（五维身份色单双共用），改模板需同步 design-spec 并重跑四条基线 lint。

## 版本沿革

- **v3（2026-09-07，当前）**：单人报告改为数据驱动模板（固定骨架 + `REPORT` 数据块）；双人改为十章关系工具书（只翻译差异，不评匹配分）。v2 的应用章素材（`references/applied-analysis.md`）与双人规则（`references/couple-dynamics.md`）随之停用，2026-09-08 起两个文件已删除。

## 本机专属配置（换机器需改）

SKILL.md 一律用可移植写法，本机对应关系：

| 可移植写法（SKILL.md 中） | 本机实际路径 |
|---|---|
| `~/Desktop`（默认报告输出目录） | `C:/Users/elliot/Desktop` |
| bfi2_interactive.html（计分输入来源页面） | `C:/Users/elliot/Desktop/relations/data/bfi2_interactive.html` |

## 明确不做

见 SKILL.md「Out of scope」：不从原始答题计分、不做心理诊断与治疗建议、不用于高利害决策（招聘/选拔不用；双人工具书不评匹配分、不判"合不合/要不要继续"）、不做职业决策结论。
