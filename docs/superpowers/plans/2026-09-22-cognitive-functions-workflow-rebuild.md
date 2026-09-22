# analyzing-cognitive-functions 工作流重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用新的荣格八派六步分析法整段替换 `analyzing-cognitive-functions` skill 的方法论层，并按七章新结构重建报告产出层，同时清掉全部墓碑/历史遗留/冗余声明。

**Architecture:** skill 包位于 `C:\Users\elliot\custom-skills\analyzing-cognitive-functions\`（`~\.zcode\skills\` 下为符号链接）。方法论收进 `SKILL.md`（理论地基 + 六步 + 映射表），`references/scoring-algorithm.md` 整文件删除；`writing-style` / `html-templates` / `couple-report` / `input-parsing` 四个 reference 按新口径清理重写；`lint_report.py` 重写为新报告的验收门；两份 `examples/` 基线样例按新七章重建。报告七章一一映射六条"能得出的结论" + 边界声明。

**Tech Stack:** Markdown（skill 文档）、Python 3（lint 校验脚本）、静态 HTML + 内联 SVG/CSS/JS（报告模板与样例）、git（`C:\Users\elliot\custom-skills` 仓库）。

---

## 已定共识（grill 会话 11 项决策，实施不得偏离）

| # | 决策 |
|---|---|
| D1 | 全面一致性清理：新方法论是唯一来源，与之重复或矛盾的旧表述一律删除/改写 |
| D2 | 文风：六步流程用祈使体；保留改变产出行为的内容（结论措辞规范、"不能得出"边界、语气人设）。报告人设 = 冷静、直接、不说教、不奉承，敢说真话的朋友：好消息不夸大、坏消息不回避，分析中立、建议时站在用户一侧，宁可一时不舒服也不误导；中文、口语但克制 |
| D3 | 精简后的方法论全部内嵌 `SKILL.md`；**删除新手陷阱整节、删除指南完整实例**；只留理论地基 + 六步 + 映射表 |
| D4 | 不做数据体检（满分/自评/状态不收）；输入仍是两种既有格式；**skill 内不出现测试页路径或名称** |
| D5 | 删新指南第 0 步；输入层校验保留（解析回显确认、完整性、十分制护栏、代号/重名）；扁平剖面与作答质量检查并入第 1 步形态识别 |
| D6 | 报告按六条结论重建 7 章：01 类型与八维栈 / 02 形状与分化 / 03 能量分布 / 04 压力与退行 / 05 人际与投射 / 06 个体化路径 / 07 边界声明 + 附录 |
| D7 | 噪声带 = **分差 3 分以内不构成可靠差异**（百分制字面 3 分）；梯队内名次不解读 |
| D8 | 输出形态分层：能锁格 → 单一类型 + 八格对位校验；锁不住（前两名 ≤3 分且都能当主导）→ 并列两套合法栈 + 明说"主导未定"，不引入打分/排名机制 |
| D9 | 两解场景就地写"两种可能 + 自查问题"，06 章尾集中一份「回到自己身上核对」清单 |
| D10 | 双人报告纳入改造：逐人六步定栈 + 差异翻译 + 相处协议 + 「互为触发点」；保留红线（不判合分、倍数读数、对称视角、单边数据禁推断） |
| D11 | lint 分类处置：防伤害类保留；旧组件黑名单合并去重保留（回归防御）；纯化石全删（"不是缺陷"豁免 hack、changelog 注释、"参考底稿"引用、样例编号） |

## 文件结构（改后）

```
analyzing-cognitive-functions/
├── SKILL.md                        # [重写] 方法论内嵌 + Workflow + Stop rules
├── README.md                       # [改] 删外部路径、修计数
├── references/
│   ├── input-parsing.md            # [改] 删测试页引用、去重复括注、source 中性化
│   ├── writing-style.md            # [重写] 人设总纲 + 规则 + 词表 + 固定文本块
│   ├── html-templates.md           # [重写] 新七章规格 + 单源化
│   ├── couple-report.md            # [改] 六步定栈 + 触发点块 + 删墓碑
│   └── (scoring-algorithm.md       # [删除] 内容并入 SKILL.md)
├── scripts/
│   ├── lint_report.py              # [重写] 新检查集
│   └── (__pycache__/               # [删除] 构建产物)
├── examples/
│   ├── mbti_sample.html            # [重建] 新七章 + 新数据
│   └── mbti_sampleA_sampleB.html   # [重建] 速写卡 + 触发点块 + 新数据
└── evals/evals.json                # [重写] 5 条新用例
```

**样例新数据（两份样例共用，百分制）**

| | Ni | Fe | Ti | Se | Ne | Fi | Te | Si | 判定 |
|---|---|---|---|---|---|---|---|---|---|
| A（单人样例 / 双人 A） | 78 | 72 | 64 | 58 | 47 | 41 | 33 | 26 | INFJ（Ni+Fe 锁格，八格全 ✓） |
| B（双人 B） | 80(Se) | 74(Ti) | 61(Fe) | 55(Ni) | 44(Si) | 39(Te) | 31(Fi) | 25(Ne) | ESTP（Se+Ti 锁格，八格全 ✓） |

B 行按 B 自己的栈读：Se 80 / Ti 74 / Fe 61 / Ni 55 / Si 44 / Te 39 / Fi 31 / Ne 25。两组都是干净阶梯（相邻差 ≥6），对位校验全 ✓，样例走"判定高度可信"路径。

---

### Task 1: 重写 SKILL.md

**Files:**
- Modify: `analyzing-cognitive-functions/SKILL.md`（整文件替换，110 行 → 约 190 行）

- [ ] **Step 1: 用以下内容整文件重写 SKILL.md**

````markdown
---
name: analyzing-cognitive-functions
description: Analyzes 8-function cognitive scores (Fi, Ni, Fe, Ti, Te, Ne, Se, Si) and generates client-ready HTML personality reports with MBTI type inference, personality portrait, and growth advice — plus couple relationship reports (差异翻译与相处协议, no compatibility scoring). Also exports a reusable score JSON. Use when the user provides 8-function scores (copied score text or results JSON), or asks for a 荣格八维/八维/认知功能 report, MBTI 报告, or 恋爱适配/情侣分析 based on such scores. Boundary: 荣格八维/MBTI 认知功能分数的解读与报告；只接受「复制分数」文本或「导出结果 JSON」两种输入（不负责从原始答题计分）；不覆盖其他人格测评框架（如大五人格，归 analyzing-bigfive）。
---

# Analyzing Cognitive Functions — 荣格八维人格分析与恋爱适配

## Goal

把来访者提供的 8 项认知功能分数，解读成一份「来访者看得懂」的 HTML 报告 + 一份可复用的得分 JSON。八维分数是能量分布的剖面图，不是能力清单；MBTI 四字母是参考地图，不是身份判决。

## 角色与产物

- **用户** = 提供分数的咨询师（或测试者本人）；**读者** = 来访者（无心理学基础，看报告是为了理解自己）。
- 产物：
  - **单人 HTML**（`mbti_<用户代号>.html`）→ 输出目录 `~/Desktop/MBTI/`
  - **得分 JSON**（`mbti_<用户代号>.json`，供双人分析、复测、跨 skill 复用）→ 与 HTML 同目录
  - **咨询师备注**（对话内输出，不写入报告文件）
  - 双人场景：两份单人产物 + 一份 `mbti_<A>_<B>.html`

## Workflow

- **Phase 0 — 输入解析与质量检查**
  1. 识别输入形式（结果 JSON / 复制分数文本），解析并**回显解析结果，经用户确认后才可继续**（顺序错则整份报告全错）。规则见 `references/input-parsing.md`。
  2. 归一化为固定顺序 `Ne, Ni, Fe, Fi, Te, Ti, Se, Si`；完整性检查（8 项齐全）；**十分制护栏**：8 项全部 ≤10 → 不静默处理，停下反问是否为十分制量表。
  3. 用户代号：代号缺失或目标目录已有同名文件 → 停下反问。
  4. 人数确认：2 人 → 单人报告 ×2 + 双人报告，**双方数据齐全为硬前置**。

- **Phase 1 — 核心分析（六步）**
  每次必读 `references/writing-style.md`。按下文「分析方法论」六步执行，产出：类型判定（或并列）、八格对位表、形状与分化、能量分布、压力退行、人际投射、个体化路径。

- **Phase 2 — 生成报告**
  单人结构：hero + 01–07 章 + 附录得分明细 + footer（骨架见 `references/html-templates.md`）。唯一视觉事实源 = `examples/mbti_sample.html`。固定文本块**照录，不得改写**。卡框类与禁用件出现即 FAIL。双人用 JS 数据驱动版，**不判合分**。命名：`mbti_<用户代号>.html` / `mbti_<A>_<B>.html`。

- **Phase 3 — 验证**
  `python scripts/lint_report.py <报告.html>` 循环直到全 PASS；JSON 校验（可解析、8 键齐全、顺序正确、与报告分数一致）；浏览器渲染检查（SVG 图件、天平倾角=分高端在下、打印样式）；语气抽查（对照 writing-style 语气总纲）。全部通过才允许交付。

- **Phase 4 — 交付 + 咨询师备注**
  【咨询师备注】（未写入报告文件）
  - 作答质量：正常 / 异常模式说明
  - v2 分差提示（仅 -v2 时）：旧新分数变化超过 8 分的功能项（启发式提示，用于留意重测波动，不是统计判断）
  备注只含上述两项。

## 分析方法论

读一台发动机的功率曲线，不是贴标签：看哪个功能在出力、哪个拖着不动、彼此怎么传动。结论说「能量放在哪里、哪里没被点亮」，不说「这个人属于哪一类」。

### 理论地基

1. **八维 = 态度 × 功能**。态度：外倾(e)朝向客体，内倾(i)朝向主体。功能：判断（T/F，下判断）与知觉（S/N，收信息）。2×4 = 8。两轴独立：Ti 与 Te 都高 = 态度未分化，是合法形态，不是数据错误。
2. **对立与补偿**。换到同一条轴上的另一功能、同时翻转态度 = 对立功能。意识态度越偏向一端，无意识越向另一端补偿——对立对是同一枚硬币的两面。

   | 功能 | 对立 |
   |---|---|
   | Ni | Se |
   | Ne | Si |
   | Ti | Fe |
   | Te | Fi |

3. **Beebe 八格**。荣格只讲主导、辅助、劣势；Beebe 扩展为八格：

   | 位次 | 原型 | 白话 | 分数预期 |
   |---|---|---|---|
   | 1 | 英雄 Hero | 你的主场、自我认同 | 最高 |
   | 2 | 好父母 Good Parent | 帮助和支撑别人的手 | 次高 |
   | 3 | 永恒少年 Puer/Puella | 玩得开心但不太负责的部分 | 中段 |
   | 4 | 阿尼玛/阿尼姆斯 Anima | 软肋，也是门 | 偏低，常最低 |
   | 5 | 对立人格 Opposing | 被反对时的自我防御 | 中低 |
   | 6 | 批判父母 Critical Parent | 苛责自己和他人的尺子 | 中低 |
   | 7 | 欺骗者 Trickster | 会带沟里的「聪明」 | 低 |
   | 8 | 恶魔 Demon | 压力最大时的破坏性出口 | 通常最低 |

   **锁定规则**：1↔4 互为对立，2↔3 互为对立；5 = 1 的同功能反态度，6 = 2 的，7 = 3 的，8 = 4 的。第 1 位给定 → 八格全锁，整个剖面只有 16 种合法形态。

### 硬约束

- **噪声带**：分差 ≤3 分不构成可靠差异。读梯队（分数接近、链式归组的一片），不读名次；梯队内先后不解读。
- **配对法则（定辅助）**：辅助必须与主导**不同轴（一判断、一知觉）且态度相反**。第二高分不合格 → 跳过，从合法候选里取最高。

  | 主导 | 合法辅助 | 类型 |
  |---|---|---|
  | Ni | Te / Fe | INTJ / INFJ |
  | Si | Te / Fe | ISTJ / ISFJ |
  | Ne | Ti / Fi | ENTP / ENFP |
  | Se | Ti / Fi | ESTP / ESFP |
  | Ti | Se / Ne | ISTP / INTP |
  | Fi | Se / Ne | ISFP / INFP |
  | Te | Si / Ni | ESTJ / ENTJ |
  | Fe | Si / Ni | ESFJ / ENFJ |

- **镜像自检**：主栈四功能态度全翻转 = 另一类型的主栈（Ni-Fe-Ti-Se 翻转为 Ne-Fi-Te-Si = ENFP）。5~8 位不符合镜像序列 → 类型判定可能错了。
- 8 个原型名均须进正文，每个首次出现配白话；八格扩展冠名 Beebe，不归荣格本人。

### 六步流程

**第 1 步：排序并读形状。** 先归梯队（≤3 分链式归组），再认形态：
- 尖塔型（一个极高、其余平滑递减）：主导分化清晰、自我认同稳固，健康但可能窄。
- 双峰型（两个最高分 ≤3 分）：同功能反态度（如 Ni/Ne）→ **态度未分化**，身份困惑常见；不同轴（如 Ni/Fe）→ 主辅齐飞，理想。
- 高原型（≥4 个功能挤在同一梯队）：两解——未分化（还没找到主场、易随环境变形）vs 社会化良好但自我认同稀薄（什么场合都能应付、答不上「你是谁」）。就地给两种可能 + 自查问题。
- 塌陷型（八项普遍低，如全部 ≤30；或全部 ≥85 且全距 <10）：优先怀疑答题防御、敷衍应答或耗竭状态，建议重测，所有推断降权——不是「空白人格」。
- 反常型（第 4 位或 5~8 位分数不低）：走第 5 步偏离 B 读法。

**第 2 步：定主导 = 最高分。** 警惕崇拜功能污染（填的是「我想成为的样子」）。交叉验证 → 自查问题：空闲时自发干什么？能量在什么时候回升？

**第 3 步：配对法则定辅助。** 不取简单第二高。查映射表，从合法候选里取最高 → 主导 + 辅助即锁定类型（如 Ni + Fe = INFJ）。

**第 4 步：镜像补全八格。** 按锁定规则排出 5~8 位，理论栈与实测分并排写出。

**第 5 步：校验。** 正常趋势 1 > 2 > 3 > 4 ≳ 5 ≈ 6 > 7 > 8，允许的偏离要解释而不是忽略：
- **偏离 A（第 3 位超过第 2 位）**：把「玩乐/兴趣」当主要出口，常见于刚成年、职业未定型、主业窒息的人。高于辅助往往意味着责任回避——更愿待在玩得转的地方，而不是扛辅助该扛的事。分差越贴近噪声带，措辞越弱。
- **偏离 B（第 4 位分数不低）**：两解——劣势功能的膨胀（被它「附身」：突然狂热投入健身、感官刺激、物质消费，用 Se 逃 Ni 的重压之类）vs 误判（把崇拜的功能填高了）。就地给两种可能 + 自查问题。
- 镜像自检不过 → 回到第 2/3 步重定。
- **输出形态**：能锁格（主导唯一、辅助合法）→ 单一类型 + 对位校验（✓/≈/✗，八格全 ✓ 可写「判定高度可信」）；锁不住（前两名 ≤3 分且都可当主导）→ 并列两套合法栈、明说「主导未定」，配自查问题。不引入任何打分、排名、解释成本机制。

**第 6 步：读动力。** 分数是症状，动力才是病灶：
- 辅助在**支撑**主导，还是在**打架**（Ni 极高、Fe 极低 = 有洞见但不可理喻）？
- 第 6 位的高低 = 内在批判者的音量（偏高 → 对自己苛刻、也苛责别人）。
- 第 8 位是压力下的**退行预警**，不是弱点：开始高频使用第 8 位功能 = 已进入退行。

### 结论口径

**能得出**（报告七章各承载其一）：类型与八维栈 / 形状与功能分化 / 能量分布（回血与耗竭）/ 压力下的退行形态 / 人际投射与冲突机制 / 个体化路径（最低那格 = 成长空间最大，它是通往自性的门）。

**不能得出**（07 章边界声明承载）：不是能力测评（高分 ≠ 能力强）；不是诊断（分不开结构与状态）；不预测行为（类型是倾向不是剧本）；不能替代亲身验证。

**措辞**：结论说「能量放在哪里/哪里没被点亮」，不说「你就是 X 型的人」；四字母是地图不是身份证；坏消息不回避、好消息不夸大；人的目标是成为完整的自己，不是成为一个类型。

## Success criteria

1. `scripts/lint_report.py` 对交付报告全 PASS。
2. 得分 JSON 校验通过（可解析、8 键齐全、顺序正确、与报告分数一致）。
3. 浏览器渲染检查通过（图件、天平倾角=分高端在下、打印样式）。
4. 语气抽查通过：结论句全部是能量口径，无类型判决句式、无评价词。

## Stop rules

- 输入缺项 / 代号缺失 / 目标目录同名 → 停下反问。
- 8 项全部 ≤10（十分制疑点）→ 停下反问。
- 2 人但只有一方数据 → 不生成双人报告（降级单人 + 「从你这方看到的关系模式」，禁止推断缺席一方）。
- 来访者对结论有异议 → 停下核对，不硬辩护。

## References

- `references/input-parsing.md` — 两种输入格式解析、归一化、代号规则、得分 JSON schema
- `references/writing-style.md` — 语气总纲、硬性规则、命名表、固定文本块、禁用词表
- `references/html-templates.md` — 单人/双人报告结构、设计令牌、视觉件规格
- `references/couple-report.md` — 双人报告口径、数据契约、章节结构、红线
- `scripts/lint_report.py` — 交付前校验
````

- [ ] **Step 2: 验证残留清零**

Run: `grep -n -E "scoring-algorithm|测试页|8function_interactive|新手|踩的坑" "C:\Users\elliot\custom-skills\analyzing-cognitive-functions\SKILL.md"`
Expected: 0 处

Run: `grep -c "启发式提示" "C:\Users\elliot\custom-skills\analyzing-cognitive-functions\SKILL.md"`
Expected: 1（唯一保留处在 Phase 4）

- [ ] **Step 3: Commit**

```bash
cd /c/Users/elliot/custom-skills && git add analyzing-cognitive-functions/SKILL.md && git commit -m "feat(cognitive-functions): 方法论层换血为六步锁格法，报告七章映射六条结论"
```

---

### Task 2: 重写 references/writing-style.md

**Files:**
- Modify: `analyzing-cognitive-functions/references/writing-style.md`（整文件替换，245 行 → 约 120 行）

- [ ] **Step 1: 用以下内容整文件重写 writing-style.md**

````markdown
# Writing Style — 措辞与固定文本

## 1. 语气总纲（人设）

冷静、直接、不说教、不奉承。像一个真正为用户着想且敢说真话的朋友：好消息不夸大，坏消息不回避；分析时保持中立，提建议时坚定站在用户一侧。宁可让用户一时不舒服，也不让用户被误导。语言：中文，口语但克制。

## 2. 命名表

| 功能 | 正文名 |
|---|---|
| Ne | 外倾直觉 |
| Ni | 内倾直觉 |
| Fe | 外倾情感 |
| Fi | 内倾情感 |
| Te | 外倾思考 |
| Ti | 内倾思考 |
| Se | 外倾感觉 |
| Si | 内倾感觉 |

八位置原型白话（首次出现配白话，原型名可进正文）：

| 位次 | 原型名 | 白话 |
|---|---|---|
| 1 | 英雄 | 你最自然、最拿手、最认同自己的部分 |
| 2 | 好父母 | 你照顾、支撑别人的那双手 |
| 3 | 永恒少年 | 放松时才玩得起来、孩子气、也容易在这里受伤的部分 |
| 4 | 阿尼玛/阿尼姆斯 | 最费力、最想回避，也是最可能带你长大的门 |
| 5 | 对立人格 | 被人反对时冒出来的防御姿态 |
| 6 | 批判父母 | 内心那个挑剔的声音 |
| 7 | 欺骗者 | 压力下自以为聪明、容易把你带沟里的把戏 |
| 8 | 恶魔 | 压力最大时才出现、破坏性最强的出口 |

## 3. 硬性规则

- **R1** 第二人称「你」，口语但克制；一句一个意思。
- **R2** 结论句式必须是能量口径：「能量放在哪里 / 哪里没被点亮 / 哪头更常用 / 哪头更费力」。禁类型判决句式（「你就是 X 型的人」）。
- **R3** 推测必须带标记（「可能 / 往往 / 常见于」）；两解场景给两种可能 + 自查问题，不硬选一种写成定论。
- **R4** 禁用评价词：优势、劣势、优点、缺点、强项、短板、好坏；描述功能高低一律用「更常用 / 更费力 / 主场 / 不常用」，不出现「强端/弱端」。（固定文本块中的「能力强」属否定句式「分数高不等于能力强」，照录不受此限。）
- **R5** 报告正文不出现「咨询师 / 会谈 / 访谈」字样（读者是本人）；「访谈区分」一律转译为自查问题。
- **R6** 分析层词汇零容忍：正文不出现「梯队 / 断层 / 分数分层 / 尖塔型 / 双峰型 / 高原型 / 塌陷型 / 反常型 / inflation」等，用白话（「最前面几项几乎不分先后」「八项普遍偏低」「后面断崖式掉下去」）。
- **R7** 不写机制空转（「这是因为你的认知结构导致」）；说现象和代价，不装作有因果证据。

## 4. 分数叙述规则

- 分数在正文的叙述任务：判断哪头更常用、哪头更费力，以及整体形态。
- 禁逐项分数罗列旁白（「八项都在 44–57」「差距不大」式）。
- 允许整体形态的白话描述（服务于 02 章），如「最前面的三项挤在一起，后面断崖式掉下去」。
- 轴 caption 按分差三档（|差| = 轴两端分差）：
  - ≤3 →「两者接近——这条轴没有明显的赢家」
  - 4–11 →「更常露面的是 X，但 Y 也在场」
  - ≥12 →「这条轴上更常用的是 X，Y 是明显更费力的一头」
- 双人读数用倍数表述（「Ni 是 Se 的 1.57 倍」），不用分差绝对值。

## 5. 禁用词表（lint 按此机械投影）

| 禁 | 替换 / 说明 |
|---|---|
| 优势 / 劣势 / 优点 / 缺点 / 强项 / 短板 / 缺陷 | 更常用 / 更费力 / 主场 / 不常用；「缺陷」→「不足」 |
| 梯队 / 断层 / 分数分层 | 白话：「几乎不分先后」「明显掉队」 |
| 尖塔型 / 双峰型 / 高原型 / 塌陷型 / 反常型 | 白话形态描述 |
| Fi-Ni loop / 内循环 / 情感失语类术语 | 禁止出现 |
| 你就是太…（句式） | 禁止出现（防定性伤害） |
| 以你的经历为准（整句） | 禁止出现（防敷衍话术） |
| 神经质 / 情绪稳定性 | 不涉及（大五归 analyzing-bigfive） |
| 合不合 / 要不要继续 | 双人报告禁区 |

比喻收缩：全篇比喻 ≤3 处；允许词汇：电量 / 充电 / 能量、罗盘 / 自我罗盘 / 价值罗盘。

## 6. 防伤害

- 禁止灾难化预测（「你这样下去会…」「这段关系注定…」）。
- 压力/退行内容写成预警 + 护栏建议，不写成宿命。
- 摩擦写成「差异 + 可操作解法」，不指责任何一方。

## 7. 固定文本块（照录，不得改写）

- hero lede：「荣格八维理论——提供对意识运作机理的深层内在解释力」
- 01 章末：「别把任何标签当身份证。」
- 04 章标题：「你的盲区：并非不足，是成本」
- 05 章引言：「你付出的和你想要的，经常不是同一种东西」
- 06 章引言：「对成年人来说，守住你最常用的功能，回报远高于死磕最不常用的那一格」
- 07 边界声明五条：
  1. 这份报告不是能力测评：分数高不等于能力强，它与智商、情商和任何绩效无关。
  2. 不是诊断工具：它分不开人格结构与状态起伏，低分可能是压抑、未开发，也可能是健康的谦逊。
  3. 不能预测行为：类型是倾向，不是剧本；你的选择永远大于这份地图。
  4. 不能替代亲身验证：所有推断都要放回你自己的经历里核对（清单见 06 章尾）。
  5. 类型是理解人的辅助工具，不是人本身；人的目标是成为完整的自己，不是成为一个类型。
- footer：「……不构成临床诊断。数据是快照，不是宿命；类型是地图，不是领土。」
- 双人固定块见 `references/couple-report.md`（三条照录）。
````

- [ ] **Step 2: 验证**

Run: `grep -n -E "定稿|正典|参考底稿|解禁|不设独立张力小节|跨阵营翻译官" "C:\Users\elliot\custom-skills\analyzing-cognitive-functions\references\writing-style.md"`
Expected: 0 处（墓碑清零）。

Run: `grep -c "冷静、直接、不说教、不奉承" "C:\Users\elliot\custom-skills\analyzing-cognitive-functions\references\writing-style.md"`
Expected: 1

- [ ] **Step 3: Commit**

```bash
cd /c/Users/elliot/custom-skills && git add analyzing-cognitive-functions/references/writing-style.md && git commit -m "refactor(cognitive-functions): writing-style 换为能量口径词系+人设总纲，固定块改五条边界"
```

---

### Task 3: 重写 references/html-templates.md

**Files:**
- Modify: `analyzing-cognitive-functions/references/html-templates.md`（整文件替换，238 行 → 约 130 行）

- [ ] **Step 1: 用以下内容整文件重写 html-templates.md**

````markdown
# HTML Templates — 报告结构与视觉件

唯一视觉事实源 = `examples/mbti_sample.html`（双人 = `examples/mbti_sampleA_sampleB.html`）。设计令牌、组件 CSS、打印样式与其一致；改任何视觉规则前先看样例实际长什么样。

## 1. 设计令牌与全局（保持现状，不改）

纸感设计令牌、hero 86vh、680px 列宽（双人 720px）、hairline 表格（无外框、无竖线、无底色、无圆角）、打印样式逐字保持。功能色 `var(--ni)` 等八色沿用：颜色永远属于功能，不属于人。

## 2. 单人报告结构（hero + 01–07 + 附录 + footer，章节恰 7 个）

**hero**：`.kicker`「Jungian Cognitive Functions · 人格坐标报告」+ 定位句 h1 + `.lede` 固定句 + 雷达（形状只表示相对高低）。

**01 · 类型与八维栈**（承载：类型与八维栈）
- 关键词总表（`table.lt`）：功能 · 分数 · 栈位（原型名 + 白话）· 一句话画像。行序按分数降序；不设排名列，不出现「全维最高/第二」类名次标签。
- 柱状图（精确分数，0–100 标尺）。
- 类型判定块：
  - 锁格成功：`<h3>最接近的类型：INFJ（仅供参考）</h3>` + 栈序一行（Ni-Fe-Ti-Se｜Ne-Fi-Te-Si）+ 对位校验摘要（八格全 ✓ 可写「判定高度可信」）。
  - 锁不住：`<h3>主导未定：两套合法栈（仅供参考）</h3>` + 并列两栈 +「主导未定」明示 + 自查问题。
- 章末固定句「别把任何标签当身份证。」

**02 · 形状与分化**（承载：形状与功能分化）
- 整体形态白话描述（禁形态学名）+ 哪几项几乎不分先后（白话，禁「梯队」）。
- 分化程度：主导能独立工作、不被其他功能干扰 = 分化好；分数糊成一团 = 分化差。
- 两解场景（高原型：未分化 vs 社会化良好）就地写两种可能 + 自查问题。

**03 · 能量分布**（承载：能量分布 + 主辅协作）
- 四条轴（轴序固定：Se-Ni / Si-Ne / Te-Fi / Ti-Fe），每轴：`.beam` 天平图（分高端在下）→ `table.duo-t` 两端对照（「更常用的一头 / 它的代价」列名）→ [`table.pc-t` 双弱对照] → `.scene` 场景块。
- caption 按分差三档（writing-style §4）。
- 双弱判定 = 两端实测分均列全维后三位。
- 主辅是支撑还是打架（如 Ni 高 Fe 低 = 有洞见但不可理喻式落差）。
- 末尾放「什么场合最值钱」回血场合表（原 03 章内容并入此处）。

**04 · 压力与退行**（承载：压力退行 + 偏离 B）
- 标题照录「你的盲区：并非不足，是成本」。
- 第 4 位：两解（被劣势「附身」的膨胀 vs 误判）+ 自查问题。
- 第 6 位：内在批判者的音量（偏高 → 对自己苛刻、也苛责别人）。
- 第 8 位：退行预警（高频出现 = 已进入退行）+ 外部护栏建议。

**05 · 人际与投射**（承载：人际冲突机制）
- 引言照录「你付出的和你想要的，经常不是同一种东西」。
- 投射机制段：劣势与阴影最容易被投射到别人身上、引发强烈情绪。
- `div.relg` rel 四键（你给出的 / 你索取的 / 你的摩擦点 / 关系里的你）+ 兼容地图（白话，不判合分）+ 三句句式。

**06 · 个体化路径**（承载：个体化）
- 引言照录「对成年人来说，守住你最常用的功能，回报远高于死磕最不常用的那一格」。
- 发展建议表：每行 = 方向（守常用 / 点亮不常用）+ 具体做法（含频次/场景）。最低那格 = 成长空间最大的门。
- 偏离 A 若出现：写责任回避信号与要练的功课（扛起辅助该扛的事），措辞随分差弱化。
- 章尾固定小节**「回到自己身上核对」**：汇总全部待验证项（崇拜污染、两解场景、锁格存疑）为自查问题清单。

**07 · 边界声明**：五条照录（writing-style §7）。

**附录 得分明细**：8 行 × 5 列（功能 · 分数 · 栈位 · 原型白话 · 对位 ✓/≈/✗）。角色列按判定栈位取（锁格法下即唯一栈位；并列时两栈分列）。✓ = 实测梯队与理论位次段位一致（1–2 位在最高两梯队、3–4 位居中、5–8 位低位）；≈ = 跨一档；✗ = 明显错位。

**footer**：`.disc` 临床句照录。

## 3. 视觉件分工

雷达管形状总览（相对高低）/ 柱状图管精确分数 / 天平图管四条轴（分高端在下）/ 表格件管内容 / scene 管收束。一图一职，互不复读。

## 4. 双人报告

见 `references/couple-report.md`（结构：hero + 00–05 + footer；数据契约 JS、光谱图、四象限矩阵不变）。颜色规则（实心 = A、空心 = B；颜色属于功能不属于人）以 couple-report §1 为准。

## 5. lint 对照

结构件计数、固定句、禁用件黑名单以 `scripts/lint_report.py` 为准；旧组件名单只存在于代码黑名单，本文档不再罗列。
````

- [ ] **Step 2: 验证**

Run: `grep -n -E "旧件|禁用，出现即 FAIL：01–08|刻意设计|当前口径" "C:\Users\elliot\custom-skills\analyzing-cognitive-functions\references\html-templates.md"`
Expected: 0 处（招魂名录与改动叙事清零）。

Run: `grep -c "一图一职" "C:\Users\elliot\custom-skills\analyzing-cognitive-functions\references\html-templates.md"`
Expected: 1（重复声明去重）

- [ ] **Step 3: Commit**

```bash
cd /c/Users/elliot/custom-skills && git add analyzing-cognitive-functions/references/html-templates.md && git commit -m "refactor(cognitive-functions): html-templates 重建为七章骨架，删除旧件名录与重复声明"
```

---

### Task 4: 修改 references/input-parsing.md

**Files:**
- Modify: `analyzing-cognitive-functions/references/input-parsing.md`（精确编辑 7 处）

- [ ] **Step 1: 删除测试页引用与外部任务旁白（L3 整段）**

原文：

```markdown
本地测试页 `8function_interactive.html`（70 题交互计分，百分制 0-100，题库与计分公式见 `soulstation_8function_70.json`）能产出两种数据格式。本 skill 的输入**仅接受这两种格式** + 用户另行提供的代号，不接受其他来源的裸分数。若任务需要读取测试页或题库文件本身（如核对计分公式、修改测试页），先校验文件存在；不存在时停下询问用户，不臆造其内容。
```

替换为（保留输入口径语义，删测试页/题库引用与段尾外部任务旁白整句）：

```markdown
输入仅接受「结果 JSON」与「复制分数文本」两种格式 + 用户另行提供的代号，不接受其他来源的裸分数。
```

- [ ] **Step 2: 三处「测试页」字样中性化（L15/L35/L72）**

原文：

```markdown
### 1.1 结果 JSON（`8function_results.json`，测试页「导出结果 JSON」按钮产出）
```

替换为：

```markdown
### 1.1 结果 JSON（`8function_results.json`，「导出结果 JSON」按钮产出）
```

原文：

```markdown
### 1.2 复制分数文本（测试页「复制分数」按钮产出）
```

替换为：

```markdown
### 1.2 复制分数文本（「复制分数」按钮产出）
```

原文：

```markdown
- 代号由用户在输入时另行提供（测试页产出的数据不含代号）
```

替换为：

```markdown
- 代号由用户在输入时另行提供（分数数据不含代号）
```

- [ ] **Step 3: 删除 v2 提示的重复免责括注（L76）**

原文：

```markdown
（启发式提示，用于留意重测波动，不是统计判断）
```

替换为：删除该括注，句子其余部分（含「报告**与本次**分数变化超过 8 分的功能项」前缀）原样保留。

（该括注唯一保留处在 SKILL.md Phase 4。）

- [ ] **Step 4: 得分 JSON 的 source 字段中性化（L87 示例块 + L102 规则行）**

原文：

```markdown
  "source": "8function_interactive.html",
```

替换为：

```markdown
  "source": "荣格八维测试",
```

原文：

```markdown
- `source`：固定 `8function_interactive.html`
```

替换为：

```markdown
- `source`：固定「荣格八维测试」
```

- [ ] **Step 5: 验证**

Run: `grep -n -E "8function_interactive|soulstation|测试页|启发式提示" "C:\Users\elliot\custom-skills\analyzing-cognitive-functions\references\input-parsing.md"`
Expected: 0 处

- [ ] **Step 6: Commit**

```bash
cd /c/Users/elliot/custom-skills && git add analyzing-cognitive-functions/references/input-parsing.md && git commit -m "chore(cognitive-functions): input-parsing 删外部路径与重复括注，source 字段中性化"
```

---

### Task 5: 修改 references/couple-report.md

**Files:**
- Modify: `analyzing-cognitive-functions/references/couple-report.md`（编辑 6 处）

- [ ] **Step 1: §0 机制行追加逐人六步定栈**

原文（约 L19）：

```markdown
机制为「逐功能对照；每条轴看『各自自比偏向』（A 用本人两端之比、B 用本人两端之比，互不换算）」
```

替换为：

```markdown
每人先按 SKILL.md 六步定栈（00 速写卡承载各自的定栈结论），再逐功能对照；每条轴看「各自自比偏向」（A 用本人两端之比、B 用本人两端之比，互不换算）
```

- [ ] **Step 2: 00 速写卡规格补充定栈结论（§2 的 00 行）**

原文（约 L43）：

```markdown
00 PORTRAITS 速写卡×2 + 三处错位预告
```

替换为：

```markdown
00 PORTRAITS 速写卡×2（每卡含六步定栈结论：类型 + 栈序 + 一句话能量画像）+ 三处错位预告
```

- [ ] **Step 3: 在 03 章结构行后新增「互为触发点」块（§2，约 L51「03 亲密关系」行之后）**

插入：

```markdown
  - **互为触发点**（03 章内固定块）：对照双方的第 4/6/8 位撞上对方哪一格。读法：一方最费力的一格恰是对方主场 → 摩擦是翻译成本、分工是资源；一方的第 8 位对上对方的高位 → 退行时最容易误读对方，写成预警 + 护栏，不写成宿命。
```

- [ ] **Step 4: 删除改动叙事（约 L105）**

原文：

```markdown
新双人报告**不设独立伦理框**——伦理口径由封面定位句、05 边界声明、页脚临床句共同承载
```

替换为：

```markdown
伦理口径由封面定位句、05 边界声明、页脚临床句共同承载；三条照录块必须出现
```

- [ ] **Step 5: 删除「刻意设计」旁白（约 L62）**

原文：

```markdown
用内联 `<script>` 数据驱动，这是双人「换数据即生成」的刻意设计（§1 复现要点）
```

替换为：

```markdown
用内联 `<script>` 数据驱动（换数据即生成）
```

（`html-templates.md` 中同款括注已随 Task 3 整文件重写消失，无需再改。）

- [ ] **Step 6: 颜色规则去重（约 L127）**

删除 §中重复的「颜色永远属于功能，不属于人」「实心 = A、空心 = B」句，只保留 §1（约 L62 所在节）一处。若 §1 无此句，则保留在删除后最先出现的一处、删其余，全文件计数 = 各 1。

- [ ] **Step 7: 验证**

Run: `grep -n -E "刻意设计|不设独立伦理框" "C:\Users\elliot\custom-skills\analyzing-cognitive-functions\references\couple-report.md"`
Expected: 0 处

Run: `grep -c "互为触发点" "C:\Users\elliot\custom-skills\analyzing-cognitive-functions\references\couple-report.md"`
Expected: ≥1

- [ ] **Step 8: Commit**

```bash
cd /c/Users/elliot/custom-skills && git add analyzing-cognitive-functions/references/couple-report.md && git commit -m "feat(cognitive-functions): 双人报告接入六步定栈与互为触发点，删改动叙事"
```

---

### Task 6: 重写 scripts/lint_report.py + 删除 scoring-algorithm.md 与 __pycache__

**Files:**
- Modify: `analyzing-cognitive-functions/scripts/lint_report.py`（整文件替换）
- Delete: `analyzing-cognitive-functions/references/scoring-algorithm.md`
- Delete: `analyzing-cognitive-functions/scripts/__pycache__/`（整个目录）

- [ ] **Step 1: 用以下内容整文件重写 lint_report.py**

````python
#!/usr/bin/env python3
"""交付前校验：python lint_report.py <report.html>

单人/双人口径自动判定（含 renderBeam / renderHeroRadar / 「双人（恋人）」即双人）。
全部检查 PASS 退出码 0，否则 1。禁用词表与 references/writing-style.md §5 保持同步。
"""

import re
import sys
from pathlib import Path

# 与 writing-style §5 同步的禁用词（机械投影）
FORBIDDEN_WORDS = [
    "优势", "劣势", "优点", "缺点", "强项", "短板", "缺陷",
    "断层", "分数分层",
    "尖塔型", "双峰型", "高原型", "塌陷型", "反常型",
    "Fi-Ni loop", "内循环",
    "神经质", "情绪稳定性",
    "你就是太", "以你的经历为准",
]

# 旧组件黑名单（回归防御：只在旧版出现过的件名；合并去重后的唯一名单）
FORBIDDEN_LEGACY = [
    "summary-card", "epigraph", "chapter-head", "chapter-sub",
    "fnchart", "axis-fill", "combo-card", "type-cards",
    "fit-fill", "fit-", "person-card", "chip-row",
    "p1-tag", "--p1-color", "meta-header", "ev-tag",
]

SINGLE_REQUIRED = [
    "Jungian Cognitive Functions · 人格坐标报告",
    "荣格八维理论——提供对意识运作机理的深层内在解释力",
    "别把任何标签当身份证",
    "你的盲区：并非不足，是成本",
    "你付出的和你想要的，经常不是同一种东西",
    "对成年人来说，守住你最常用的功能，回报远高于死磕最不常用的那一格",
    "不是能力测评",
    "不是诊断工具",
    "不能预测行为",
    "不能替代亲身验证",
    "类型是理解人的辅助工具，不是人本身",
    "回到自己身上核对",
    "类型是地图，不是领土",
]

COUPLE_REQUIRED = [
    "Jungian Cognitive Functions · 双人（恋人）分析报告",
    "互为触发点",
    "这不是合盘判决书",
    "关系是做出来的，不是算出来的",
    "类型是地图，不是领土",
]


def is_couple(html: str) -> bool:
    return ("renderBeam" in html) or ("renderHeroRadar" in html) or ("双人（恋人）" in html)


def check(html: str) -> list:
    problems = []
    couple = is_couple(html)

    for w in FORBIDDEN_WORDS:
        if w in html:
            problems.append(f"[禁用词] {w}")
    for w in FORBIDDEN_LEGACY:
        if w in html:
            problems.append(f"[旧件] {w}")

    required = COUPLE_REQUIRED if couple else SINGLE_REQUIRED
    for s in required:
        if s not in html:
            problems.append(f"[缺固定句] {s}")

    # 类型判定块：锁格成功或锁不住并列，至少其一
    if not couple and ("最接近的类型" not in html) and ("主导未定" not in html):
        problems.append("[缺结构] 类型判定块（最接近的类型 / 主导未定）")

    if couple:
        sections = re.findall(r'<section id="s([0-5])"', html)
        if sorted(set(sections)) != ["0", "1", "2", "3", "4", "5"]:
            problems.append(f"[结构] 双人章节应为 s0–s5，实得 {sorted(set(sections))}")
    else:
        sections = re.findall(r'<section id="s([1-7])"', html)
        if sorted(set(sections)) != ["1", "2", "3", "4", "5", "6", "7"]:
            problems.append(f"[结构] 单人章节应为 s1–s7，实得 {sorted(set(sections))}")
        if "附录" not in html:
            problems.append("[缺结构] 附录得分明细")

    if "@media print" not in html:
        problems.append("[缺结构] 打印样式")
    return problems


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python lint_report.py <report.html>")
        return 2
    html = Path(sys.argv[1]).read_text(encoding="utf-8")
    problems = check(html)
    print(f"口径: {'双人' if is_couple(html) else '单人'}")
    if problems:
        print(f"FAIL（{len(problems)} 项）")
        for p in problems:
            print(" -", p)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
````

- [ ] **Step 2: 删除 scoring-algorithm.md 与 __pycache__**

```bash
cd /c/Users/elliot/custom-skills/analyzing-cognitive-functions && rm references/scoring-algorithm.md && rm -rf scripts/__pycache__
```

- [ ] **Step 3: 冒烟验证（对旧样例应 FAIL，证明检查生效）**

Run: `python "C:\Users\elliot\custom-skills\analyzing-cognitive-functions\scripts\lint_report.py" "C:\Users\elliot\custom-skills\analyzing-cognitive-functions\examples\mbti_sample.html"`
Expected: FAIL（旧样例缺新固定句、含「优势/缺陷」等禁用词、附录列不符）——失败信息中应能看到 `[缺固定句]` 与 `[禁用词]` 条目。

- [ ] **Step 4: Commit**

```bash
cd /c/Users/elliot/custom-skills && git add -A analyzing-cognitive-functions/scripts analyzing-cognitive-functions/references && git commit -m "refactor(cognitive-functions): lint 重写为新检查集，删除 scoring-algorithm 与构建产物"
```

---

### Task 7: 重建 examples 两份基线样例

**Files:**
- Modify: `analyzing-cognitive-functions/examples/mbti_sample.html`
- Modify: `analyzing-cognitive-functions/examples/mbti_sampleA_sampleB.html`

两份样例共用 Task 头部给出的数据（A：Ni78/Fe72/Ti64/Se58/Ne47/Fi41/Te33/Si26 = INFJ；B：Se80/Ti74/Fe61/Ni55/Si44/Te39/Fi31/Ne25 = ESTP）。**CSS、打印样式、双人 JS 引擎不改字节**；只换数据、章节结构与文案。

- [ ] **Step 1: 运行图表坐标生成器，保存输出备贴**

```bash
python - <<'EOF'
import math
A = {"Ni":78,"Fe":72,"Ti":64,"Se":58,"Ne":47,"Fi":41,"Te":33,"Si":26}
B = {"Se":80,"Ti":74,"Fe":61,"Ni":55,"Si":44,"Te":39,"Fi":31,"Ne":25}
ORDER = ["Ne","Ni","Fe","Fi","Te","Ti","Se","Si"]  # 雷达顺时针序（与现样例一致）

def radar(scores, cx=190, cy=190, r=140):
    pts = []
    for i, k in enumerate(ORDER):
        ang = -math.pi/2 + 2*math.pi*i/8
        rr = r * scores[k] / 100
        pts.append(f"{cx + rr*math.cos(ang):.1f},{cy + rr*math.sin(ang):.1f}")
    return " ".join(pts)

def beams(scores):
    out = {}
    for x, y in [("Se","Ni"), ("Si","Ne"), ("Te","Fi"), ("Ti","Fe")]:
        if scores[x] >= scores[y]:
            out[f"{x}-{y}"] = f"{x} 是 {y} 的 {scores[x]/scores[y]:.2f} 倍"
        else:
            out[f"{x}-{y}"] = f"{y} 是 {x} 的 {scores[y]/scores[x]:.2f} 倍"
    return out

print("A radar:", radar(A))
print("B radar:", radar(B))
for k, v in beams(A).items(): print("A", k, v)
for k, v in beams(B).items(): print("B", k, v)
EOF
```

预期输出（可直接使用，粘贴时以此为准）：

```
A radar: 190.0,124.2 267.2,112.8 290.8,190.0 230.6,230.6 190.0,236.2 126.6,253.4 108.8,190.0 164.3,164.3
B radar: 190.0,155.0 244.4,135.6 275.4,190.0 220.7,220.7 190.0,244.6 116.7,263.3 78.0,190.0 146.4,146.4
A Se-Ni Ni 是 Se 的 1.34 倍
A Si-Ne Ne 是 Si 的 1.81 倍
A Te-Fi Fi 是 Te 的 1.24 倍
A Ti-Fe Fe 是 Ti 的 1.12 倍
B Se-Ni Se 是 Ni 的 1.45 倍
B Si-Ne Si 是 Ne 的 1.76 倍
B Te-Fi Te 是 Fi 的 1.26 倍
B Ti-Fe Ti 是 Fe 的 1.21 倍
```

（以上为实际运行输出；若 Python 版本导致舍入差异，以实际输出为准。）

- [ ] **Step 2: 单人样例章节迁移（mbti_sample.html）**

按下表迁移现有 `section`，wrapper（`<section id>`/`.sec-num`/CSS 类）保留原字节，内部内容按右列处置：

| 旧 | 新 | 处置 |
|---|---|---|
| s1 01 · OVERVIEW 总览 | s1 01 · TYPE & STACK 类型与八维栈 | 关键词总表 4 行换为 8 行（列：功能·分数·栈位·一句话，删「全维最高/第二」标签）；柱状图数据换新（Step 1 的 A 值，柱高 = 分数 ×1.6px）；类型判定块按 Step 3 整块替换 |
| （无） | s2 02 · SHAPE 形状与分化 | 整章按 Step 3 新块插入 |
| s2 02 · YOUR TRADE-OFFS 四条轴 | s3 03 · ENERGY 能量分布 | id/sec-num/h2 改；四个 `.beam` SVG 的倾角与表值按 Step 1 更新；caption 按三档重写（Ni-Se 20 分、Ne-Si 21 分 → 明显档；Fi-Te 8 分、Fe-Ti 8 分 → 中间档）；轴三加双弱表（Fi/Te 均列全维后三位）；末尾加「什么场合最值钱」表（旧 s3 内容改写为回血场合后移入） |
| s3 03 · STRENGTHS 优势 | （并入 s3 末尾） | 表头「你的优势:什么场合最值钱」改为「什么场合让你回血」；表内「优势/最值钱」字样按词表替换 |
| s4 04 · BLIND SPOTS 盲区 | s4 04 · STRESS & REGRESSION 压力与退行 | 标题换固定句「你的盲区：并非不足，是成本」；内容整章按 Step 3 新块替换（第 4/6/8 位读法 + 偏离 B 两解） |
| s5 05 · INTIMATE 亲密关系 | s5 05 · PEOPLE & PROJECTION 人际与投射 | id/sec-num/h2 改；`div.relg` 四键内容按 INFJ 重写；章首插入投射机制段（Step 3） |
| s6 06 · GROWTH 发展建议 | s6 06 · INDIVIDUATION 个体化路径 | 引言换固定句；建议表按 INFJ 重写；章尾插入「回到自己身上核对」清单（Step 3） |
| s7 07 · 边界声明 | s7 07 · 边界声明 | 4 条换 5 条照录（Step 3） |
| 附录得分明细 | 同位保留 | 改 5 列（功能·分数·栈位·原型白话·对位），8 行按 INFJ 栈位，全 ✓ |

- [ ] **Step 3: 单人样例新块（逐字贴入）**

类型判定块（替换旧 `<h3>最接近的类型…` 表格整段）：

````html
<h3>最接近的类型：INFJ（仅供参考）</h3>
<table>
  <tr><td>栈序</td>
    <td><span class="fn" style="color:var(--ni)">Ni</span> → <span class="fn" style="color:var(--fe)">Fe</span> → <span class="fn" style="color:var(--ti)">Ti</span> → <span class="fn" style="color:var(--se)">Se</span>
    <span style="color:var(--muted)">｜阴影 </span><span class="fn" style="color:var(--ne)">Ne</span> → <span class="fn" style="color:var(--fi)">Fi</span> → <span class="fn" style="color:var(--te)">Te</span> → <span class="fn" style="color:var(--si)">Si</span></td></tr>
  <tr><td>对位</td><td><span class="hl">八格全部对位吻合，判定高度可信</span></td></tr>
</table>
````

02 章整章（插入为 `<section id="s2">`）：

````html
<section id="s2">
  <div class="sec-num">02 · SHAPE & DIFFERENTIATION</div>
  <h2>你的分布形状：分化得清不清楚</h2>
  <p class="lead">八个分数画出来是一座平滑下降的阶梯：最前面的 <span class="fn" style="color:var(--ni)">Ni</span> 和 <span class="fn" style="color:var(--fe)">Fe</span> 一骑当先（彼此差 6 分，有先后但同属顶层），之后 <span class="fn" style="color:var(--ti)">Ti</span>、<span class="fn" style="color:var(--se)">Se</span> 依次递减，没有挤成一团的平原，也没有反常的隆起。这是主导功能分化清晰的形状——你的自我认同稳固，代价是可能偏窄。</p>
  <p class="muted">分化程度：你的最高一项能独立站出来，不被其他功能搅动——分化得好。哪些项几乎不分先后：中间段 <span class="fn" style="color:var(--ne)">Ne</span> 47 与 <span class="fn" style="color:var(--fi)">Fi</span> 41 只差 6 分、<span class="fn" style="color:var(--fi)">Fi</span> 与 <span class="fn" style="color:var(--te)">Te</span> 差 8 分，读的时候不必给它们排先后。</p>
</section>
````

04 章整章（替换旧 s4 内容）：

````html
<section id="s4">
  <div class="sec-num">04 · STRESS & REGRESSION</div>
  <h2>你的盲区：并非不足，是成本</h2>
  <p class="lead">以下每一项都不是「你不行」，而是「你做这件事，要比别人多花力气」。诚实的读法是给它们配一套省力的做法，而不是逼自己变成别人。</p>
  <table>
    <tr><td>第 4 位 <span class="fn" style="color:var(--se)">Se</span> 58</td>
        <td>不算低——结合 <span class="fn" style="color:var(--ni)">Ni</span> 高达 78，更像 <span class="fn" style="color:var(--ni)">Ni</span> 太重、<span class="fn" style="color:var(--se)">Se</span> 在反弹：可能间歇性用感官刺激（暴食、刷手机、极限体验）逃离直觉的重压。另一种可能是把「活在当下」这个理想自我填高了。回想最近半年：有没有突然狂热投入某项感官体验的阶段？你空闲时自发做的事，更像「预感」还是「感受」？</td></tr>
    <tr><td>第 6 位 <span class="fn" style="color:var(--fi)">Fi</span> 41</td>
        <td>内心的挑剔声音不算大——你苛责自己时多半借用 <span class="fn" style="color:var(--ti)">Ti</span> 的逻辑外壳（「这不合理」），而不是价值审判（「我不配」）。</td></tr>
    <tr><td>第 8 位 <span class="fn" style="color:var(--si)">Si</span> 26</td>
        <td>压力下的预警位：极端压力时你会彻底抛弃身体感与过往经验——忘记吃饭睡觉、重复犯同一个错、与现实脱钩。出现这些信号 = 已经进入退行。护栏：把吃饭睡觉交给日历提醒，重大决定强制回看上次同类决定的记录。</td></tr>
  </table>
</section>
````

05 章投射机制段（插在 s5 的 `.lead` 之后、`div.relg` 之前）：

````html
<p class="muted">先说一个机制：最容易点燃你情绪的，往往不是别人做错了什么，而是他们身上带着你被排除在自我认同之外的那部分——你的软肋和阴影，最容易被你看见在别人身上。下面这些模式，与其说是「你和对方的差别」，不如说是「你和自己没和解的部分」在借对方出场。</p>
````

06 章章尾自查清单（插在 s6 末尾）：

````html
<h3>回到自己身上核对</h3>
<p class="muted">这份报告里有几处推断，只有你能验证。带着下面的问题回看自己的经历，答案比报告更重要。</p>
<table class="lt">
  <tr><td>第 2 步的主导判定</td><td>你空闲时自发干什么？做什么事的时候，时间过得最快、做完能量反而回升？（用来验证 <span class="fn" style="color:var(--ni)">Ni</span> 是主导，还是「想成为的样子」）</td></tr>
  <tr><td>第 4 位不算低</td><td>最近半年有没有突然狂热投入感官体验的阶段？（膨胀与误判的分界线）</td></tr>
</table>
````

07 章五条边界（替换旧 4 条，逐字）：

````html
<ol class="disc">
  <li>这份报告不是能力测评：分数高不等于能力强，它与智商、情商和任何绩效无关。</li>
  <li>不是诊断工具：它分不开人格结构与状态起伏，低分可能是压抑、未开发，也可能是健康的谦逊。</li>
  <li>不能预测行为：类型是倾向，不是剧本；你的选择永远大于这份地图。</li>
  <li>不能替代亲身验证：所有推断都要放回你自己的经历里核对（清单见 06 章尾）。</li>
  <li>类型是理解人的辅助工具，不是人本身；人的目标是成为完整的自己，不是成为一个类型。</li>
</ol>
````

- [ ] **Step 4: 单人样例其余字串替换**

- 关键词总表行（8 行）：按 A 数据降序 Ni 78 / Fe 72 / Ti 64 / Se 58 / Ne 47 / Fi 41 / Te 33 / Si 26，列值格式 `<功能> <分数> · <原型名+白话>`，删「全维最高/全维第二/居中/全维最低」标签。
- 雷达多边形 `points` → Step 1 的 `A radar` 值；柱状图 8 根柱高 = 分数 ×1.6（160px 满分）。
- 页脚：删「示例样本 SAMPLE-02（数据取自参考底稿）」→「示例样本」。
- 全文禁用词清零（grep Task 6 的 `FORBIDDEN_WORDS` 逐个确认）。

- [ ] **Step 5: 双人样例改造（mbti_sampleA_sampleB.html）**

1. 内联 JS 数据契约：`const A = {...}` 换 A 值、`const B = {...}` 换 B 值（键名结构不变）。
2. 00 速写卡两张：`fn-points`/`desc`/`mbti-ref` 按定栈结论重写——A：`Ni 78（内倾直觉·英雄）· Fe 72（外倾情感·好父母）` + 画像「用『将会怎样』看现在，再把人和事照顾到」+ `mbti-ref`：`定栈 <strong>INFJ</strong>（八格对位吻合，仅供参考）`；B：`Se 80（外倾感觉·英雄）· Ti 74（内倾思考·好父母）` + 画像「先接住眼前的事实，再用内在逻辑筛一遍」+ `定栈 <strong>ESTP</strong>`。
3. 03 章插入**互为触发点**块（`.lead` 之后）：

````html
<h3>互为触发点：你们最容易误读对方的地方</h3>
<table>
  <tr><td>A 的第 4 位 <span class="fn" style="color:var(--se)">Se</span> ↔ B 的第 1 位</td><td>A 最费力的一格，正是 B 的主场：A 逃避的感官现实，B 天生就在里面。摩擦是翻译成本——B 拉你回到当下时不是在打断你；分工是资源——落地的事交给 B 的眼睛。</td></tr>
  <tr><td>B 的第 4 位 <span class="fn" style="color:var(--ni)">Ni</span> ↔ A 的第 1 位</td><td>B 最费力的一格，正是 A 的主场：A 已经在看三步之外，B 还停在眼前的事实。A 的预判 B 接不住时，别读成唱反调——那只是对方的费力点。</td></tr>
  <tr><td>A 的第 8 位 <span class="fn" style="color:var(--si)">Si</span></td><td>极端压力下 A 会彻底忘记身体感与日程（忘吃饭、重复犯错），而 B 的 <span class="fn" style="color:var(--si)">Si</span> 只是不常用。预警：看到 A 开始不睡觉不吃饭，那是退行信号，不是不在乎你。护栏：日历和提醒由 B 托住。</td></tr>
</table>
````

4. 四条轴光谱读数句按 Step 1 的倍数值重写（A：Ni 是 Se 的 1.34 倍 / Ne 是 Si 的 1.81 倍 / Fi 是 Te 的 1.24 倍 / Fe 是 Ti 的 1.12 倍；B：Se 是 Ni 的 1.45 倍 / Si 是 Ne 的 1.76 倍 / Te 是 Fi 的 1.26 倍 / Ti 是 Fe 的 1.21 倍）。
5. 四象限分类表：「都强/都弱/A 强 B 弱/B 强 A 弱」→「都常用/都不常用/A 带 B/B 补 A」；按 A/B 新数据重分配各象限功能（A 高位 Ni/Fe/Ti/Se；B 高位 Se/Ti/Fe/Ni → 共识区 Fe·Ti·Se·Ni 需按实测差重算贴线与错位项，写法沿用现样例句式）。
6. 页脚删「SAMPLE-PAIR-01」编号字样。
7. 05 章边界三条照录块保留，第一句确认含「这不是合盘判决书」。

- [ ] **Step 6: 验证循环**

Run: `python "C:\Users\elliot\custom-skills\analyzing-cognitive-functions\scripts\lint_report.py" "C:\Users\elliot\custom-skills\analyzing-cognitive-functions\examples\mbti_sample.html"`
Expected: PASS

Run: `python "C:\Users\elliot\custom-skills\analyzing-cognitive-functions\scripts\lint_report.py" "C:\Users\elliot\custom-skills\analyzing-cognitive-functions\examples\mbti_sampleA_sampleB.html"`
Expected: PASS

浏览器打开两份样例：天平分高端在下、雷达/柱状图与数据一致、打印预览正常。

- [ ] **Step 7: Commit**

```bash
cd /c/Users/elliot/custom-skills && git add analyzing-cognitive-functions/examples && git commit -m "feat(cognitive-functions): 两份基线样例按七章重建为 INFJ/ESTP 锁格示范"
```

---

### Task 8: 重写 evals/evals.json + 更新 README.md

**Files:**
- Modify: `analyzing-cognitive-functions/evals/evals.json`（整文件替换）
- Modify: `analyzing-cognitive-functions/README.md`（编辑 2 处）

- [ ] **Step 1: 用以下内容整文件重写 evals.json**

````json
[
  {
    "name": "单人锁格成功",
    "input": "百分制分数 Ni78 Fe72 Ti64 Se58 Ne47 Fi41 Te33 Si26 + 代号「示例」",
    "expect": "按六步锁格输出 INFJ 单一类型 + 八格对位校验；七章齐全；结论句全部能量口径；07 章五条边界照录；06 章尾含「回到自己身上核对」"
  },
  {
    "name": "锁不住并列",
    "input": "百分制分数 Fi68 Ni67 Fe52 Ti50 Te46 Si40 Se38 Ne35 + 代号「并列」",
    "expect": "前两名 ≤3 分且都可当主导 → 01 章输出「主导未定」+ 并列两套合法栈（Fi 主导栈 / Ni 主导栈）+ 自查问题；不出现打分、排名、解释成本；全文无「梯队/断层」叙事"
  },
  {
    "name": "高原型两解",
    "input": "百分制分数 Ni55 Fe53 Ti52 Se51 Ne50 Fi49 Te48 Si47 + 代号「扁平」",
    "expect": "02 章给高原型两解（未分化 vs 社会化良好）+ 自查问题；推断措辞降权；06 章尾清单包含对应待验证项"
  },
  {
    "name": "双人缺一方",
    "input": "只有 A 的分数，要求出双人报告",
    "expect": "拒绝生成双人报告；降级为单人 + 「从你这方看到的关系模式」一节；禁止推断缺席一方任何心理特征"
  },
  {
    "name": "双人全流程",
    "input": "A（Ni78 Fe72 Ti64 Se58 Ne47 Fi41 Te33 Si26）+ B（Se80 Ti74 Fe61 Ni55 Si44 Te39 Fi31 Ne25）各带代号",
    "expect": "两份单人报告 + 双人 mbti_A_B.html；00 速写卡含各自定栈结论；03 章含「互为触发点」；倍数读数；全文不判合分、无「合不合/要不要继续」"
  }
]
````

- [ ] **Step 2: README.md 两处编辑**

原文（约 L23）：

```markdown
`scripts/lint_report.py` — 交付前 lint（单人口径 35 项 / 双人口径专项）
```

替换为：

```markdown
`scripts/lint_report.py` — 交付前 lint（检查项以脚本为准，单人/双人口径自动判定）
```

原文（约 L33）：

```markdown
**测试数据来源**：本地测试页 `~/Desktop/relations/data/8function_interactive.html`（70 题交互计分，百分制 0-100）；题库与计分公式见同目录 `soulstation_8function_70.json`。
```

替换为：

```markdown
**测试数据**：百分制 0–100 的 8 项功能分 + 用户代号。
```

（保留 README 中「改 lint/CSS 后先回归基线样例」的维护者指令——它只在 README 出现一次。）

- [ ] **Step 3: 验证**

Run: `python -c "import json;json.load(open(r'C:\Users\elliot\custom-skills\analyzing-cognitive-functions\evals\evals.json',encoding='utf-8'));print('json ok')"`
Expected: `json ok`

Run: `grep -n -E "8function_interactive|soulstation|35 项" "C:\Users\elliot\custom-skills\analyzing-cognitive-functions\README.md"`
Expected: 0 处

- [ ] **Step 4: Commit**

```bash
cd /c/Users/elliot/custom-skills && git add analyzing-cognitive-functions/evals analyzing-cognitive-functions/README.md && git commit -m "test(cognitive-functions): evals 换新五用例，README 删外部路径与过时计数"
```

---

### Task 9: 终验（全包一致性）

**Files:** 只读检查 + 必要时回修。

- [ ] **Step 1: lint 双样例全 PASS**

```bash
cd /c/Users/elliot/custom-skills/analyzing-cognitive-functions && python scripts/lint_report.py examples/mbti_sample.html && python scripts/lint_report.py examples/mbti_sampleA_sampleB.html
```
Expected: 两个 PASS

- [ ] **Step 2: 墓碑全包 grep 自查**

```bash
cd /c/Users/elliot/custom-skills/analyzing-cognitive-functions && grep -rn -E "参考底稿|定稿|SAMPLE-0|刻意设计|不设独立|解禁|8function_interactive|soulstation|scoring-algorithm|解释成本|奥卡姆|前两名候选" --include="*.md" --include="*.py" --include="*.json" . | grep -v "docs/"
```
Expected: 0 处

- [ ] **Step 3: 新口径关键词到位**

```bash
cd /c/Users/elliot/custom-skills/analyzing-cognitive-functions && grep -c "3 分" SKILL.md && grep -c "回到自己身上核对" SKILL.md references/html-templates.md examples/mbti_sample.html && grep -c "互为触发点" references/couple-report.md examples/mbti_sampleA_sampleB.html
```
Expected: 每项 ≥1

- [ ] **Step 4: 符号链接与 references 清单一致**

Run: `ls "C:\Users\elliot\.zcode\skills\analyzing-cognitive-functions\references"`
Expected: 恰 4 个文件（input-parsing / writing-style / html-templates / couple-report），无 scoring-algorithm.md。

- [ ] **Step 5: 终提交**

```bash
cd /c/Users/elliot/custom-skills && git add -A analyzing-cognitive-functions && git commit -m "chore(cognitive-functions): 全包墓碑清零终验通过"
```

---

## 覆盖对照（决策 → 任务）

| 决策 | 落点 |
|---|---|
| D1 全面清理 | Task 2/3 整文件重写、Task 4/5 精确删、Task 6 黑名单去重、Task 9 Step 2 全包 grep |
| D2 文风人设 | Task 2 §1 语气总纲（人设原文入文）；R2/R3/R4 结论口径 |
| D3 内嵌+删实例/陷阱 | Task 1（无实例、无新手陷阱节）；scoring-algorithm 删除在 Task 6 |
| D4 不提测试页 | Task 4 Step 1/3、Task 8 Step 2 |
| D5 删第 0 步+并入形态识别 | Task 1 Phase 0（只留输入校验）+ 第 1 步形态识别（塌陷型吸收作答质量） |
| D6 七章重建 | Task 1 结论口径、Task 3 §2、Task 7 迁移表 |
| D7 3 分噪声带 | Task 1 硬约束、Task 2 §4 三档、Task 7 caption |
| D8 分层输出 | Task 1 第 5 步输出形态、Task 3 类型判定块、Task 6 lint 检查、Task 8 用例 2 |
| D9 就地两解+汇总清单 | Task 1 第 2/5 步、Task 3 §2、Task 7 新块 |
| D10 双人改造 | Task 5、Task 7 Step 5、Task 8 用例 5 |
| D11 lint 分类处置 | Task 6（防伤害留、黑名单并、化石删） |

## 实施勘误记录（2026-09-22 执行时按文件实际文本校准）

- **Task 4**：「原文」引用已按 input-parsing.md 实际文本校准为 7 处编辑（见正文 Step 1–4）。
- **Task 5**：原步骤的「原文」为探索报告转录、与 couple-report.md 实际文本有出入，执行以下述 11 处逐字清单为准（含两处执行时新发现的旧方法论残留：「标签走第一候选」「排名」列）：
  1. `- **机制**：逐功能对照；每条轴看「各自自比偏向」（A 用本人两端之比、B 用本人两端之比，互不换算）` → 前缀加 `每人先按 SKILL.md 六步定栈（00 速写卡承载各自的定栈结论），再逐功能对照`
  2. `00 PORTRAITS   两张速写卡（各取每人最突出 2 功能 + 一句话 + MBTI 参考）` → `00 PORTRAITS   两张速写卡（各含六步定栈结论：类型 + 栈序 + 一句话能量画像，尾行 MBTI 参考）`
  3. `03 亲密关系` 行后接 `               + 互为触发点（第 4/6/8 位互撞对照表）`（15 空格续行）
  4. 锚点行后插入「**互为触发点（03 章内固定块）**」规格段（第 4/6/8 位互撞读法）
  5. `新双人报告**不设独立伦理框**——伦理口径由封面定位句、05 边界声明、页脚临床句共同承载` → `伦理口径由封面定位句、05 边界声明、页脚临床句共同承载；三条照录块必须出现`
  6. `## 5. 伦理与边界口径（体现在 05 边界声明 + footer，无独立伦理框）` → `## 5. 伦理与边界口径`
  7. `——这是双人「换数据即生成」的刻意设计（§1 复现要点）。` → `（换数据即生成）。`
  8. `（颜色只属于功能）` 括注删除（§6 表行）
  9. `每人「最接近 X（仅供参考）」` → `每人「定栈 X（仅供参考）」`
  10. `学术名 + 排名` → `学术名 + 栈位`；`（标签走第一候选，与单人同口径）` → `（标签走定栈结论，与单人同口径）`
  11. 删除 ev-tag 化石禁令整行（`- **证据标签**：…`）
- **执行补充（审查时发现）**：
  12. writing-style §4 补双弱 caption 固定句：双弱轴（两端实测分均列全维后三位）用「这条轴两头都偏弱——它不是你的主场。」，不走三档。
  13. Task 7 单人样例天平几何规则：横梁两端垂直偏移 h = min(24, round(2.2 × |分差|)) px（分高端下沉、低端上浮）；四轴分差 Ni-Se 20 / Ne-Si 21 / Fi-Te 8 / Fe-Ti 8；轴三（Fi-Te）双弱，照旧样例双弱梁画法。
