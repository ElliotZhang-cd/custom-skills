---
name: analyzing-cognitive-functions
description: Analyzes Jungian 8-function cognitive scores (Fi, Ni, Fe, Ti, Te, Ne, Se, Si) and generates client-ready HTML personality reports — MBTI type inference, Big Five bridge (internal analysis step, not an entry trigger), attachment inference, personality portrait, growth advice — plus couple compatibility reports. Use when the user provides 荣格八维/认知功能/八维 scores or MBTI test results (e.g. from soulstation.club/8function), or asks for 人格分析, 依恋类型, 恋爱适配, 情侣分析, 荣格分析.
---

# Analyzing Cognitive Functions — 认知功能人格分析与恋爱适配

## 角色与产物

用户是**心理咨询师**；报告的读者是**来访者**（无心理学基础）。每次分析产出两样东西：

1. **报告 HTML**（终端产品，100% 来访者视角，大白话，零术语）→ 保存为文件
2. **咨询师备注**（低置信度结论、阈值边界项、作答质量、会谈核实建议）→ 只在对话中汇报，不写进任何文件；咨询师要求时才另存

**测试数据来源**：`https://soulstation.club/8function/do70`（百分制 0-100）
**输入**：8 个功能分数（Fi, Ni, Fe, Ti, Te, Ne, Se, Si），可附年龄、性别、关系背景、自报 MBTI/依恋类型
**输出路径**：**所有 HTML 报告默认保存到 Windows 桌面**（WSL 路径 `/mnt/c/Users/elliot/Desktop/`）；用户另行指定时从其指定

## 工作流

```
任务进度（复制此清单并逐项勾选）：
- [ ] Phase 0: 输入解析与质量检查
- [ ] Phase 1: 核心分析（分层 → 类型 → 大五 → 依恋）
- [ ] Phase 2: 生成报告 HTML
- [ ] Phase 3: 验证（lint 脚本 + 浏览器渲染检查）
- [ ] Phase 4: 交付 + 对话内咨询师备注
```

### Phase 0: 输入解析与质量检查

1. 提取 8 项功能分数。**裸分数无功能标签时，默认顺序为 Se, Si, Ne, Ni, Te, Ti, Fe, Fi**（soulstation 输出格式），但**必须回显解析结果并经用户确认后才可继续**——顺序错则整份报告全错
2. 质量检查（规则见 `references/scoring-algorithm.md` §3）：完整性（8 项齐全、0-100）→ 十分制护栏（全 ≤10 时反问）→ 扁平剖面检测（全距 <10 → 建议重测、推断降权）→ 作答质量模式（极端应答/敷衍 → 咨询师备注中警告）
3. 确认人数：1 人 → 单人报告；2 人 → 单人报告 ×2 + 双人报告。**双人报告必须双方数据齐全**，仅一方数据时降级处理（规则见 `references/couple-dynamics.md` §0.1）

### Phase 1: 核心分析

按顺序执行，规则全部在 reference 文件中：

| 分析 | 规则文件 | 何时读 |
|------|---------|--------|
| 梯度分层 + MBTI 类型推断 | `references/scoring-algorithm.md` | 每次必读 |
| 大五桥接 + 交叉验证 + SDT/Gross | `references/bigfive-bridge.md` | 每次必读 |
| 依恋类型推断（恋爱/家庭双领域） | `references/attachment-inference.md` | 每次必读 |
| 双人八维度/天赋/阶段/冲突/风险 | `references/couple-dynamics.md` | 仅双人时读 |
| 通俗化语言规范（命名库/禁用词/固定文本块） | `references/writing-style.md` | 每次必读 |
| HTML 结构/组件/打印样式 | `references/html-templates.md` | 生成报告前读 |

关键要求：
- 类型推断输出**前两名候选 + 主观置信度**（不得用"概率"），必须承认解释难点
- 依恋推断必须区分**恋爱关系 vs 父母/家人**两个领域；分数落在阈值 ±3 边界上的结论必须标注"对分数波动敏感"
- 大五只走维度级桥接（E-I/S-N/T-F/J-P），**报告只写四个维度；神经质与八维无桥接，默认不涉及**（休眠能力见 `references/bigfive-bridge.md` §3.5）

### Phase 2: 生成报告 HTML

- 章节结构、图表（雷达图/平衡条/剖面图/象限图/类型栈图）、组件 CSS、打印样式：严格按 `references/html-templates.md` §2-3
- 语言：严格按 `references/writing-style.md`——学术名+白描命名（弃用比喻名）、具体化形式多样、去 AI 味规则、证据三级标签（✅🔶⚪）
- 深度：严格按 `references/writing-style.md` §5——功能互动动力学、核心张力、误解全过程场景分解；单人报告 7000-9000 字
- 固定文本块（阅读指南/伦理声明/谦卑段落/局限声明）**照录，不得改写**
- 文件命名：`report_YYYYMMDD_来访者编号.html` / `couple_report_YYYYMMDD_来访者编号.html`（用编号不用真名），保存到 Windows 桌面

### Phase 3: 验证（反馈循环，不通过则修复后重来）

1. 运行 lint：`python3 scripts/lint_report.py <报告文件路径>`
   - 检查：正文裸功能代码、禁用词、固定文本块缺失、meter-fill CSS、disclaimer
   - 有 FAIL 项 → 修复 → 重新 lint，直到全部 PASS
2. 浏览器渲染检查：打开 HTML 确认柱状图/评分条可见、速览卡完整、目录锚点可跳转、打印预览无组件断裂
3. 全部通过才允许交付

### Phase 4: 交付 + 咨询师备注

在对话中向咨询师汇报（模板）：

```
【咨询师备注】（未写入报告文件）
- 类型推断：第一候选 XX（置信度 X%）vs 第二候选 XX（X%）；主要疑点：……
- 阈值边界敏感项：……（重测可能翻转的结论）
- 作答质量：正常 / 异常模式说明
- 建议会谈中核实：1. …… 2. ……
- 来访者反馈整合：若来访者对类型/依恋有异议，以反馈为准并调整报告
```

## 测评指导语（咨询师可直接发给来访者）

> 请按你**日常的真实状态**作答，不要按你希望自己成为的样子来答。没有对错好坏之分。尽量一次做完，中间不要隔太久。做完后把结果页截图或分数发给我即可。

## 实践注记（给咨询师）

报告中的 ⚪ 级结论（依恋方向）可用 **ECR-R 短版**验证升级。如会谈涉及情绪困扰议题，另行安排大五人格量表（该维度与八维无桥接，不进入本报告）。

## References

- `references/scoring-algorithm.md` — 梯度分层、16 型功能栈、Beebe 位置、类型推断算法、输入质量检查
- `references/bigfive-bridge.md` — 大五桥接矩阵、字母倾向计算、交叉验证、SDT/Gross 模板
- `references/attachment-inference.md` — 功能→依恋映射、双领域规则、阈值边界敏感规则
- `references/couple-dynamics.md` — 八维度评分、关系天赋、阶段/冲突/风险/解决办法模板、伦理声明
- `references/writing-style.md` — 学术名+白描命名表、去 AI 味规则、深度规范、禁用词表、证据标签、固定文本块
- `references/html-templates.md` — CSS 变量、组件类、五种图表实现、报告结构、输出与验证规范

## Examples

- `examples/report_v2_sample.html` — 单人报告结构范式（双镜头 + 速览卡 + 附录）
