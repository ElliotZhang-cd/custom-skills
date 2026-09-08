---
name: analyzing-cognitive-functions
description: Analyzes 8-function cognitive scores (Fi, Ni, Fe, Ti, Te, Ne, Se, Si) and generates client-ready HTML personality reports with MBTI type inference, personality portrait, and growth advice — plus couple compatibility reports. Also exports a reusable score JSON. Use when the user provides 8-function scores (copied score text or results JSON), or asks for 荣格/八维/认知功能/人格分析, 恋爱适配, 情侣分析, mbti 报告.
---

# Analyzing Cognitive Functions — 荣格八维人格分析与恋爱适配

## Goal

把来访者提供的 8 项认知功能分数，解读成一份「来访者看得懂、咨询师可核对」的 HTML 报告 + 一份可复用的得分 JSON，并在对话中向咨询师输出【咨询师备注】。读者是无心理学基础的年轻人：语言直观、形象、一次读懂（画像与语言规范见 `references/writing-style.md` §1）。MBTI 类型只是窄标签：仅用于快速定位，类型学局限的固定说明照录 `references/writing-style.md` §2.3。

## 角色与产物

用户是**心理咨询师**；报告的读者是**来访者**（无心理学基础）。每次分析产出三样东西：

1. **报告 HTML**（终端产品，100% 来访者视角，大白话，零术语）→ 保存为文件
2. **得分 JSON**（`mbti_<用户代号>.json`，供后续双人分析、复测、跨 skill 复用）→ 与 HTML 同目录
3. **咨询师备注**（2026-09-09 起精简：固定只含 作答质量、v2 分差提示——其余分析细节一律不进备注，详见 Phase 4 精简决定）→ 只在对话中汇报，不写进任何文件；咨询师要求时才另存

**输入**：「复制分数」文本或「导出结果 JSON」+ 用户另行提供的来访者代号。解析规则见 `references/input-parsing.md`。

**输出路径**：默认用户桌面 `~/Desktop/MBTI/`；用户另行指定时从其指定。

## Workflow

```
任务进度（复制此清单并逐项勾选）：
- [ ] Phase 0: 输入解析与质量检查
- [ ] Phase 1: 核心分析（轴结构 → 类型）
- [ ] Phase 2: 生成报告 HTML + 得分 JSON
- [ ] Phase 3: 验证（lint 脚本 + JSON 校验 + 浏览器渲染检查）
- [ ] Phase 4: 交付 + 对话内咨询师备注
```

### Phase 0: 输入解析与质量检查

1. 识别输入形式（结果 JSON / 复制分数文本），按 `references/input-parsing.md` §1 解析并回显，经用户确认后才可继续
2. 归一化为固定顺序 `Ne, Ni, Fe, Fi, Te, Ti, Se, Si`（规则见 `references/input-parsing.md` §2），随后执行质量检查（规则见 `references/scoring-algorithm.md` §3）：完整性 → 十分制护栏 → 扁平剖面检测 → 作答质量模式
3. 获取/确认**用户代号**（规则见 `references/input-parsing.md` §3）；代号缺失或目标目录已有同名文件 → 按 Stop rules 停下反问
4. 确认人数：1 人 → 单人报告；2 人 → 单人报告 ×2 + 双人报告，**双方数据齐全为硬前置**；仅一方数据 → 按 Stop rules 降级（规则见 `references/couple-report.md` §0）

### Phase 1: 核心分析

本 skill 的 reference 阅读表（各 Phase 通用）：

| 分析 | 规则文件 | 何时读 |
|------|---------|--------|
| 输入解析 + 代号规则 + 得分 JSON | `references/input-parsing.md` | 每次必读 |
| 轴结构分析 + MBTI 类型推断（窄标签） | `references/scoring-algorithm.md` | 每次必读 |
| 双人逐功能对照 / 四条轴光谱 / 怎么搭 / 边界（JS 数据驱动） | `references/couple-report.md` | 仅双人时读（降级场景也读其 §0） |
| 通俗化语言规范（命名库/禁用词/固定文本块/语气总纲） | `references/writing-style.md` | 每次必读 |
| HTML 结构/组件/打印样式 | `references/html-templates.md` | 生成报告前读 |

关键要求：
- 类型推断输出**前两名候选**，呈现于 01 章候选类型表；排序按量化打分表（`references/scoring-algorithm.md` §2.3）执行
- 荣格解读落在 02 章四条轴，冠名不得归荣格本人（冠名声明见 `references/scoring-algorithm.md` 文首）；8 位置原型仅以附录「角色」列白话近似呈现（`references/writing-style.md` §2.2），原型名不进正文

### Phase 2: 生成报告 HTML + 得分 JSON

- **单人报告**：章节结构（hero + 01–07 章 + 附录得分明细 + footer）、视觉件、组件 CSS、打印样式严格照录 `references/html-templates.md` §1–§4；唯一视觉事实源 = `examples/mbti_sample.html`；卡框类与已废弃章件禁用——出现即 FAIL（废弃清单见 html-templates §2.7）
- **语言与深度**：全部按 `references/writing-style.md`——语气总纲（最高优先级）、读者画像（§1）、比喻纪律（§4.1）、术语零容忍与不给机制解释（R7/R8）、证据标签退出正文（ev-tag 已退出）、语言件规则（§10）、深度规范（张力由 02 章承载，单人 **2800–4000 字**，§5）；固定文本块（hero lede / 01 章末标签句 / 02·04·05·06 章引言 / 05 三句句式 / 07 边界声明 / footer 收尾句）**照录，不得改写**（§9；「05 三句句式」定义见 §10.7）
- **双人报告**：JS 数据驱动版；结构/数据契约（`A`/`B` 对象）/文案/伦理口径照录 `references/couple-report.md`，组件与视觉规格见 `references/html-templates.md` §5，成品样例 `examples/mbti_sampleA_sampleB.html`；**不判合分**、证据标签退出正文
- **文件命名**（详情见 `references/input-parsing.md` §3–4）：单人 `mbti_<代号>.html` + `mbti_<代号>.json`；双人 `mbti_<A>_<B>.html` + 两份单人次 JSON（v2 规则同 §3）；保存到默认输出路径（见「角色与产物」）

### Phase 3: 验证（反馈循环，不通过则修复后重来）

1. 运行 lint：`python scripts/lint_report.py <报告文件路径>`。检查项完整清单见 `references/html-templates.md` §4.3（单人）/ §5.3（双人）；有 FAIL 项 → 修复 → 重新 lint，直到全部 PASS。改过 lint 或 CSS 后，先对两个基线样例回归（`examples/mbti_sample.html` 单人、`examples/mbti_sampleA_sampleB.html` 双人，均须 PASS）再出新报告
2. JSON 校验：得分 JSON 可解析、`scores` 8 键齐全且顺序为 `Ne,Ni,Fe,Fi,Te,Ti,Se,Si`、`sorted` 为完整 8 项且降序、与报告中的分数一致
3. 浏览器渲染检查：打开 HTML 确认视觉件（雷达形状 / 柱状图数值 / 天平倾角=分高端在下 / caption 分支 / hairline 表格）渲染正常、锚点可跳转、打印预览无组件断裂且纸纹不打印（注意浏览器缓存——用带 `?v=时间戳` 的地址强制刷新）
4. 正文字数抽查（单人 2800–4000 字，writing-style §5）
5. 语气总纲抽查：无说教/奉承、好消息未夸大、坏消息未回避、比喻一眼能解（writing-style §1/§4.1）
6. 全部通过才允许交付

### Phase 4: 交付 + 咨询师备注

在对话中向咨询师汇报（模板；**2026-09-09 用户决定精简，旧七节模板作废勿再用**）：

```
【咨询师备注】（未写入报告文件）
- 作答质量：正常 / 异常模式说明
- v2 分差提示（仅 -v2 时）：旧新分数变化超过 8 分的功能项（启发式提示，用于留意重测波动，不是统计判断）
```

> **备注只含上述两项（2026-09-09 用户决定）**：分析层其余内容（类型打分过程细节、证据分级、阴影面/压力模式、依恋等）一律不进备注——其中依恋、阴影面/压力模式、证据三级标签已从 skill 退役（见各 reference），类型打分细节不汇报。咨询师单次点名需要某项时按需单出，不进常规备注。

## Success criteria

全部满足才算完成：
1. lint 全 PASS（`scripts/lint_report.py`）
2. 得分 JSON schema 与键顺序校验通过，且与报告分数一致
3. 浏览器渲染检查通过（雷达/柱状/天平/表格可见、锚点可跳、打印无断裂）
4. 语气总纲抽查通过：无说教/奉承句式、好消息未夸大、坏消息未回避；比喻全部一眼能解（比喻收缩原则 §4.1）
5. 正文字数 2800–4000（单人）

## Stop rules

遇到以下情况**停下询问，不擅自继续**：
- 输入数据缺项/超界/解析失败 → 退回要求重发
- 输入里没有用户代号 → 停下问一句让用户填写，绝不自动编
- 目标目录已有同代号旧文件 → 问「加 -v2 还是覆盖」；选 -v2 时在咨询师备注报告旧新分数变化超过 8 分的功能项（启发式提示，用于留意重测波动，不是统计判断）
- 十分制疑似（8 项全 ≤10）→ 反问确认
- 扁平剖面（全距 <10）→ 建议重测，所有推断降权
- 双人场景仅一方数据 → 降级单人报告 + 一节"从你这方看到的关系模式"，禁止推测缺席方
- 来访者对类型/关系模式结论有异议 → 以来访者反馈为准，调整报告

## References

- `references/input-parsing.md` — 输入格式解析、归一化顺序、用户代号规则、得分 JSON schema
- `references/scoring-algorithm.md` — 轴结构分析、类型推断矩阵与打分表、冠名声明、输入质量检查
- `references/couple-report.md` — 双人报告：定位与数据契约、章节结构、文案与伦理口径
- `references/writing-style.md` — 语气总纲、命名表与四条轴讲法、比喻纪律、固定文本块、语言件规则
- `references/html-templates.md` — 单人/双人报告结构与视觉件规格、lint 检查项清单
