---
name: analyzing-cognitive-functions
description: Analyzes 8-function cognitive scores (Fi, Ni, Fe, Ti, Te, Ne, Se, Si) and generates client-ready HTML personality reports — post-Jungian typology analysis (Jung's four functions × two attitudes, developed into the 8-function score model and eight-position stack by Myers-era typology and Beebe; not Jung's own original formulation) with MBTI type inference, attachment inference (transitional module), personality portrait, growth advice — plus couple compatibility reports. Also exports a reusable score JSON. Use when the user provides 8-function scores from the local interactive test page (copied score text or results JSON), or asks for 荣格/八维/认知功能/人格分析, 依恋类型, 恋爱适配, 情侣分析, mbti 报告.
---

# Analyzing Cognitive Functions — 荣格八维人格分析与恋爱适配

## Goal

以**荣格八维理论为地基**：四条功能轴（感知轴＝实感/直觉，判断轴＝思考/情感）＋ 内倾/外倾态度 ＋ 八位置原型（Beebe），把来访者的测试分数解读成一份「来访者看得懂、咨询师可核对、可证伪」的 HTML 报告 + 一份可复用的得分 JSON。**冠名说明**：荣格本人只提出四种功能（感觉/直觉/思考/情感）× 两种态度（内倾/外倾）；本 skill 使用的"八维"——八个功能的分数框架、16 型功能栈与八位置原型——是荣格之后的发展（迈尔斯等人的类型学实践、Beebe 的八位置原型），并非荣格本人原创，报告中不得将八功能模型表述为荣格本人的原始模型。**MBTI 类型只是窄标签**：仅用于快速定位，并明示类型学的局限，不作为报告的组织框架。依恋推断为过渡模块（证据地位见 `references/attachment-inference.md`）。

## 角色与产物

用户是**心理咨询师**；报告的读者是**来访者**（无心理学基础）。每次分析产出三样东西：

1. **报告 HTML**（终端产品，100% 来访者视角，大白话，零术语）→ 保存为文件
2. **得分 JSON**（`mbti_<用户代号>.json`，供后续双人分析、复测、跨 skill 复用）→ 与 HTML 同目录
3. **咨询师备注**（低置信度结论、阈值边界项、作答质量、会谈核实建议）→ 只在对话中汇报，不写进任何文件；咨询师要求时才另存

**测试数据来源**：本地测试页 `/c/Users/elliot/Desktop/relations/data/8function_interactive.html`（70 题交互计分，百分制 0-100）；题库与计分公式见同目录 `soulstation_8function_70.json`。本 skill 不使用其他来源的分数。

**输入**：测试页产出的两种格式之一（「复制分数」文本 / 「导出结果 JSON」）+ 用户另行提供的来访者代号。解析规则见 `references/input-parsing.md`。

**输出路径**：默认 `/c/Users/elliot/Desktop/relations/MBTI/`（Git Bash 路径）；用户另行指定时从其指定。

## Workflow

```
任务进度（复制此清单并逐项勾选）：
- [ ] Phase 0: 输入解析与质量检查
- [ ] Phase 1: 核心分析（轴结构 → 类型 → 依恋）
- [ ] Phase 2: 生成报告 HTML + 得分 JSON
- [ ] Phase 3: 验证（lint 脚本 + JSON 校验 + 浏览器渲染检查）
- [ ] Phase 4: 交付 + 对话内咨询师备注
```

### Phase 0: 输入解析与质量检查

1. 识别输入形式（结果 JSON / 复制分数文本），按 `references/input-parsing.md` §1 解析并回显，经用户确认后才可继续
2. 归一化为固定顺序 `Ne, Ni, Fe, Fi, Te, Ti, Se, Si`（规则见 §2），随后执行质量检查（规则见 `references/scoring-algorithm.md` §3）：完整性 → 十分制护栏 → 扁平剖面检测 → 作答质量模式
3. 获取/确认**用户代号**：没提供 → 停下反问；目标目录已有同名文件 → 问「加 -v2 还是覆盖」（规则见 `references/input-parsing.md` §3）
4. 确认人数：1 人 → 单人报告；2 人 → 单人报告 ×2 + 双人报告。**双人报告必须双方数据齐全**，仅一方数据时降级处理（规则见 `references/couple-dynamics.md` §0.1）

### Phase 1: 核心分析

按顺序执行，规则全部在 reference 文件中：

| 分析 | 规则文件 | 何时读 |
|------|---------|--------|
| 输入解析 + 代号规则 + 得分 JSON | `references/input-parsing.md` | 每次必读 |
| 轴结构分析 + MBTI 类型推断（窄标签） | `references/scoring-algorithm.md` | 每次必读 |
| 依恋类型推断（恋爱/家庭双领域） | `references/attachment-inference.md` | 每次必读 |
| 双人八维度/天赋/阶段/冲突/风险 | `references/couple-dynamics.md` | 仅双人时读 |
| 通俗化语言规范（命名库/禁用词/固定文本块/语气总纲） | `references/writing-style.md` | 每次必读 |
| HTML 结构/组件/打印样式 | `references/html-templates.md` | 生成报告前读 |

关键要求：
- 报告第 1 章：降序条形图给「分数模样」，功能速览网格给每个维度的解释；四条轴的倒向与含义放报告第 3 章，配**三轴极性图**＋假设场景（`html-templates.md` §2.3）
- 类型推断输出**前两名候选 + 主观置信度**（不得用"概率"），附「类型只是名字」固定说明（`writing-style.md` §2.3）；排序按量化打分表（`scoring-algorithm.md` §2.3）执行；偏离只述现象、不编归因（`scoring-algorithm.md` §2.4）
- 荣格解读（报告第 3 章，核心章）用 **8 位置原型白话框架**（`writing-style.md` §2.2），🔶 标注并声明"理论模型、无实证常模"；正文不出现原型名
- 依恋推断必须区分**恋爱关系 vs 父母/家人**两个领域；分数落在阈值 ±3 边界上的结论必须标注"对分数波动敏感"；Fe 低时并列替代解释（`attachment-inference.md` §1.1）

### Phase 2: 生成报告 HTML + 得分 JSON

- 章节结构（11 部分，含原型章与成长方向章，各章 h2 后带一句话结论框）、视觉件（降序条形图 / 功能速览网格 / 三轴极性图 / 排位剖面图 / 依恋象限图 / 类型栈表）、组件 CSS、打印样式：严格按 `references/html-templates.md` §2-3
- 语言：严格按 `references/writing-style.md`——语气总纲（最高优先级）、术语零容忍（R7）与不给机制性解释（R8）、学术名+白描、功能轴与 8 原型大白话、具体化形式多样、去 AI 味规则、证据三级标签
- 深度：严格按 `references/writing-style.md` §5——功能互动动力学、核心张力、误解全过程场景分解；单人报告 6000-8500 字
- 固定文本块（阅读指南/伦理声明/谦卑段落/局限声明）**照录，不得改写**
- 文件命名（详情见 `references/input-parsing.md` §3-4）：单人 `mbti_<代号>.html` + `mbti_<代号>.json`；双人 `mbti_<A>_<B>.html` + 两份单人次 JSON（v2 时 `mbti_<代号>-v2.*`），保存到 `/c/Users/elliot/Desktop/relations/MBTI/`

### Phase 3: 验证（反馈循环，不通过则修复后重来）

1. 运行 lint：`python3 scripts/lint_report.py <报告文件路径>`
   - 检查：正文裸功能代码、禁用词（含统计措辞：显著/概率/证实/证明/必然）、固定文本块、证据标签、meter-fill CSS、速览卡、打印样式；双人报告额外检查非预测承诺与伦理声明
   - 有 FAIL 项 → 修复 → 重新 lint，直到全部 PASS
2. JSON 校验：得分 JSON 可解析、`scores` 8 键齐全且顺序为 `Ne,Ni,Fe,Fi,Te,Ti,Se,Si`、与报告中的分数一致
3. 浏览器渲染检查：打开 HTML 确认视觉件（速览网格/象限图/表格）渲染正常、速览卡完整、目录锚点可跳转、打印预览无组件断裂
4. 全部通过才允许交付

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

## Success criteria

全部满足才算完成：
1. lint 全 PASS（`scripts/lint_report.py`）
2. 得分 JSON schema 与键顺序校验通过，且与报告分数一致
3. 浏览器渲染检查通过（图表可见、锚点可跳、打印无断裂）
4. 报告 ✅🔶⚪ 标签实际数量与附录统计一致
5. 语气总纲抽查通过：无说教/奉承句式、好消息未夸大、坏消息未回避

## Stop rules

遇到以下情况**停下询问，不擅自继续**：
- 输入数据缺项/超界/解析失败 → 退回要求重发
- 输入里没有用户代号 → 停下问一句让用户填写，绝不自动编
- 目标目录已有同代号旧文件 → 问「加 -v2 还是覆盖」；选 -v2 时在咨询师备注报告旧新分数变化超过 8 分的功能项（启发式提示，用于留意重测波动，不是统计判断）
- 十分制疑似（8 项全 ≤10）→ 反问确认
- 扁平剖面（全距 <10）→ 建议重测，所有推断降权
- 双人场景仅一方数据 → 降级单人报告 + 一节"从你这方看到的关系模式"，禁止推测缺席方
- 来访者对类型/依恋结论有异议 → 以来访者反馈为准，调整报告

## 测评指导语（咨询师可直接发给来访者）

> 请按你**日常的真实状态**作答，不要按你希望自己成为的样子来答。没有对错好坏之分。尽量一次做完，中间不要隔太久。做完后点结果页的**「复制分数」**或**「导出结果 JSON」**，把内容发给我即可。

## 实践注记（给咨询师）

- 报告中的 ⚪ 级结论（依恋方向）可用 **ECR-R 短版**验证升级；来访者提供 ECR-R 实测分时实测优先（休眠钩子见 `references/attachment-inference.md` §4.3）
- 如会谈涉及情绪困扰或需要大五人格画像，另行安排 BFI-2 实测（归 `analyzing-bigfive` skill，与本报告无关）
- 依恋推断是过渡模块：ECR-R 实测数据源引入后将迁移为独立依恋分析 skill（迁移注记见 `references/attachment-inference.md` 文末）

## References

- `references/input-parsing.md` — 两种输入格式解析、归一化（固定顺序）、代号规则、得分 JSON schema
- `references/scoring-algorithm.md` — 轴结构分析（四条合法轴）、16 型功能栈、Beebe 原型位置（白话列）、类型推断量化打分表、输入质量检查
- `references/attachment-inference.md` — 功能→依恋映射（证据地位声明）、双领域规则、替代解释、阈值边界敏感规则、休眠钩子
- `references/couple-dynamics.md` — 八维度评分、关系天赋、阶段/冲突/风险/解决办法模板、伦理声明
- `references/writing-style.md` — 语气总纲、学术名+白描命名表、去 AI 味规则、深度规范、禁用词表、证据标签、固定文本块
- `references/html-templates.md` — CSS 变量、组件类、视觉件规范（功能速览网格/依恋象限图/类型栈表）、报告结构（11 部分）、输出与验证规范
