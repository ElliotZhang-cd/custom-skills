---
name: analyzing-bigfive
description: 使用 BFI-2（Big Five Inventory-2）维度与子维度分数做大五人格分析，生成来访者视角 HTML 报告。当用户提供 5 维度 + 15 子维度分数（含 z/等级/M/SD），或要求 BFI-2 报告、大五人格分析、人格剖面分析、压力/职业/人际模式预测、伴侣大五匹配时使用。输入即已评分结果，本 skill 不负责计分
---

# AnalyzingBigfive — BFI-2 大五人格分析与恋爱适配

## 角色与产物

用户是**心理咨询师**；报告的读者是**来访者**（无心理学基础）。每次分析产出两样东西：

1. **报告 HTML**（终端产品，100% 来访者视角，大白话，零术语壁垒）→ 保存为文件
2. **咨询师备注**（低置信度结论、阈值边界项、作答质量、会谈核实建议）→ 只在对话中汇报，不写进任何文件

**量表**：Big Five Inventory-2 中文修订版（BFI-2），60 题，5 维度 × 3 子维度/维度
**输入边界**：本 skill 的入口点是**已经算好的评分结果**——5 维度总分 + 15 子维度分（含原始分 / z 分 / 等级 / 常模 M / SD 中的任意子集，越完整越好）；可附年龄、性别、关系背景。**本 skill 不负责从原始 60 题答题计分**——原始答卷请先用外部评分工具出分，再调起本 skill
**输出路径**：**所有 HTML 报告默认保存到 Windows 桌面**（WSL 路径 `/mnt/c/Users/elliot/Desktop/`）；用户另行指定时从其指定

## 工作流

```
任务进度（复制此清单并逐项勾选）：
- [ ] Phase 0: 输入解析与质量检查
- [ ] Phase 1: 核心分析（维度→子维度矛盾→剖面模式）
- [ ] Phase 2: 生成报告 HTML
- [ ] Phase 3: 验证（lint + 浏览器检查）
- [ ] Phase 4: 交付 + 咨询师备注
```

### Phase 0: 输入解析与质量检查

1. 提取 5 维度 + 15 子维度分数。**裸分数无标签时，默认顺序为：外向性、宜人性、尽责性、负性情绪（方向待 step 2 确认）、开放性**（BFI-2 标准输出顺序），但**必须回显解析结果并经用户确认后才可继续**
2. **第 4 域方向检测与翻转**（规则见 `references/scoring-interpretation.md` §1.2）：检查输入第 4 域 label——若为 BFI-2 原始方向（负性情绪/神经质/N/Neuroticism），**必须将该域及焦虑/抑郁/易变 3 个子维度的 z 分全部取反**，label 改为"情绪稳定性"；翻转后回显确认。这一步不做，后续每份报告都会出现 chart/正文符号翻转（A001 即为此 bug）
3. 质量检查：
   - 完整性：5 维度 + 15 子维度齐全，z 分在合理范围（-3 ~ +3）
   - 扁平剖面：全维度 |z| ≤ 0.3 → 降权提示"作答可能不够认真，结论仅供参考"
   - 极端应答：全维度 z 全正或全负且 |z| > 1 → 咨询师备注中警告社会赞许性可能
   - 子维度内部矛盾：同一维度下三子维度 z 极差 > 2 → 标记该维度需谨慎解读（规则见 `references/facet-analysis.md` §2）
4. 确认人数：1 人 → 单人报告；2 人 → 单人报告 ×2 + 双人报告。**双人报告必须双方数据齐全**

### Phase 1: 核心分析

按顺序执行，规则全部在 reference 文件中：

| 分析 | 规则文件 | 何时读 |
|------|---------|--------|
| 维度解释 + 等级描述 + 子维度矛盾分析 | `references/scoring-interpretation.md` | 每次必读 |
| 15 子维度含义 + 矛盾组合解读表 | `references/facet-analysis.md` | 每次必读 |
| 职业匹配 + 压力应对 + 人际关系模式 | `references/applied-analysis.md` | 单人必读 |
| 伴侣匹配度 + 冲突模式 + 满意度 + 沟通风格 | `references/couple-dynamics.md` | 仅双人时读 |
| 通俗化语言规范 + 固定文本块 + 禁用词 | `references/writing-style.md` | 每次必读 |
| HTML 结构/组件/打印样式/图表 | `references/html-templates.md` | 生成报告前读 |

关键要求：
- 子维度矛盾**必须分析**（规则见 `references/facet-analysis.md` §2），如"情绪敏感性总分高但易变子维度低" → 专门解读
- 双人报告基于 Karney & Bradbury (1995) 脆弱-应激-适应模型 + Gottman 高风险组合
- 报告正文提及常模来源（美国 Soto & John, 2017）并提示文化差异

### Phase 2: 生成报告 HTML

- 章节结构、图表、组件 CSS、打印样式：严格按 `references/html-templates.md`
- 语言：严格按 `references/writing-style.md`——学术名+白描命名、去 AI 味、证据三级标签
- 固定文本块（阅读指南/谦卑段落/局限声明）**照录，不得改写**；双人报告另加伦理声明（见 `references/couple-dynamics.md` §7）
- 文件命名：`bfi2_report_YYYYMMDD_编号.html` / `bfi2_couple_YYYYMMDD_编号.html`，保存到 Windows 桌面

### Phase 3: 验证（反馈循环，不通过则修复后重来）

1. 运行 lint：`python3 scripts/lint_report.py <报告文件路径>`
   - 检查：禁用词（含全文档禁止的"咨询师/会谈/咨询中"）、固定文本块（阅读指南/局限声明/谦卑段）、必填容器（meta-header/guide-box/toc/summary-card/chart-box/bar-container/facet-grid/riasec-badge/ev-tag）、meter-fill CSS、disclaimer、**维度 z 分一致性**（每个维度在标题/雷达图注释/仪表条三处必须一致，防 chart/正文符号翻转）
   - 有 FAIL 项 → 修复 → 重新 lint，直到全部 PASS
2. 浏览器渲染检查：打开 HTML 确认雷达图/仪表条可见、速览卡完整、目录锚点可跳转、打印预览无组件断裂
3. 全部通过才允许交付

### Phase 4: 交付 + 咨询师备注

在对话中向咨询师汇报（模板）：

```
【咨询师备注】（未写入报告文件）
- 最显著特征：……
- 子维度矛盾项：……
- 数据质量：正常 / 异常模式说明
- 阈值边界敏感项：……
```

## 常见陷阱

- 遗漏子维度矛盾：只看总分不看子维度差异 → 报告失去精准度，来访者觉得"说得不够像我"
- 术语裸用：首次出现专业名词不附白描 → 读者卡壳
- 图表数据与正文不一致：雷达图 z 分和文字描述对不上 → 信任度崩塌
- 双人报告只有一方数据：仍按双人模板写 → 必须降级处理或等待另一方数据

## References

- `references/scoring-interpretation.md` — 维度解释规则、等级描述模板、子维度矛盾分析、常模文化提示
- `references/facet-analysis.md` — 15 子维度含义、矛盾组合解读表
- `references/applied-analysis.md` — 职业匹配(RIASEC)、压力应对(Lazarus)、人际关系模式
- `references/couple-dynamics.md` — 相似-吸引效应、Gottman 风险组合、满意度预测、沟通风格
- `references/html-templates.md` — CSS 变量、组件类、图表实现、报告结构、输出与验证规范
- `references/writing-style.md` — 学术名+白描命名表、去 AI 味规则、禁用词表、证据标签、固定文本块

## Examples

- `examples/report_sample.html` — 单人报告范式（**合成数据 SAMPLE-01**，非真实来访者，用于结构参考与 lint 通过基线）
