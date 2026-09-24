---
name: analyzing-bigfive
description: 解读 BFI-2 的 5 维度 + 15 子维度原始分，产出给来访者阅读的 HTML 报告；不做诊断。当咨询师给出分数，或要求 BFI-2 报告、大五人格分析、人格剖面分析、伴侣大五差异工具书时使用。
---

# Analyzing Bigfive — BFI-2 大五人格分析

## Goal

用户是**心理咨询师**（唯一操作者）；报告的读者是**来访者**（无心理学基础的读者）。流程：来访者完成固定量表 → 计分平台输出固定格式的分数（文本或 JSON）→ 咨询师原样交给 LLM → 本 skill 据此分析。每次分析产出两样东西：

1. **报告 HTML**（终端产品，100% 来访者视角，零术语、全画面）→ 由数据驱动模板生成，保存为文件：单人 `templates/report-template.html`（七章结构）；双人（恋人）一律按 `references/couple-template.md`（十章关系工具书）
2. **咨询师备注**（第二个 register，见 Workflow 的分析框架）→ 只在对话中汇报给咨询师，不写进任何文件

## Workflow

### 分析框架（2 计算层 + 2 生成纪律 + 2 register）

本 skill 的全部工作按这个框架组织；`references/bigfive-theory.md` §10 给逐项白名单/黑名单。

**两个计算层**（从数字里算出来的，只有这两层）：

- **L1 常模层**（between-person）：这个人在同龄参照群体中的位置。数据 = score + 常模 M/SD → z/pct/档。回答"你在同龄人中什么位置"。**只回答位置，不回答好坏**；不作跨文化绝对判断。
- **L2 自比层**（within-person）：这个人内部 20 条目的相对格局。数据 = 同一人的分数排序 + 同域子维度极差。回答"你的内部格局与矛盾"。**不依赖常模，故对常模偏差免疫**；但也不能反推人群位置。

**两个生成纪律**（不拥有独立数据，是把 L1/L2 变成文字的方式）：

- **L3 组合纪律**：跨条目组合 → 优势/代价/张力。输入就是 L2 的输出（哪几条突出/背离）。**每条组合必须点名两个具体条目 + 档位**；数量由分数分布决定，不硬凑。
- **L4 推演纪律**：把 L3 的结论落到情境，**一律软措辞**。禁灾难化预测、禁个体概率推断、成长建议不承诺效果。

**两个 register**（同一批结论，两个读者能承受的"未加糖程度"不同）：

- **报告**（读者=来访者）：零术语、画面化、加糖。
- **咨询师备注**（读者=咨询师）：可含裸 z、不确定性与数据质量判断。**定义原则：凡在报告里被迫加糖或被迫沉默的，在这里说原话**——低信度子维度、社会赞许风险、常模选择的不确定性、阈值边界项、双人临界桥，都自动落进来（下表只是举例，不是全集）。

**L1 与 L2 是正交的两把尺子，缺一不可**；L3 建立在 L1/L2 上；L4 建立在 L1–L3 上；双人报告另加 **L5 关系层**（两人 L1–L3 + Δz → 共鸣/差异桥，不评匹配分）。

### 任务进度

```
任务进度（复制此清单并逐项勾选）：
- [ ] Phase 0: 输入解析与质量检查
- [ ] Phase 1: 核心分析（画像、组合、章节文案方向）
- [ ] Phase 2: 跑 compute + 填模板数据块
- [ ] Phase 3: 验证（lint + 必要时浏览器检查）
- [ ] Phase 4: 交付 + 咨询师备注
```

### Phase 0: 输入解析与质量检查

1. **缺失信息询问清单（一次性列出，不逐个追问）**：缺什么问什么，已有不重复问——
   ```
   开始前还差几项信息，请一起补齐：
   - 报告代号（如 zyh 或 A001；限 ASCII 字母/数字/连字符）：
   - 常模：a) 中国大学生（默认） b) 在职员工 c) 青少年（仅维度层稳妥） d) 不确定（需提供年龄，按年龄就近并注明局限）
   ```
   人数默认单人，不主动问；输入含**两份分数**或咨询师明示双人报告时才进入双人流程。
2. 解析输入并跑计算脚本（唯一数值执行器）：
   - 固定文本表 → 先转成扁平 JSON（第 4 域用中文键「情绪稳定性」或「负性情绪」，子维度用中文名即可）→ `python scripts/compute_scores.py --scores <file> [--norm …]`
   - JSON 含 `scores.stability` → `python scripts/compute_scores.py --export <file> [--norm …]`（自动取稳定性方向，忽略 `scores.raw`）
   - 回显解析结果与所用常模；正常输入无需等确认
3. **第 4 域方向**（细则 scoring-interpretation §1.2）：label「情绪稳定性」或取自 `scores.stability` → 直接用；label「负性情绪/神经质」→ **先回显确认再翻转**（禁止静默翻转）。焦虑/抑郁/易变子维度恒为本义方向
4. 质量检查（基于脚本输出的 z 表，阈值查 `thresholds.json`）：
   - 扁平剖面：全维度 |z| ≤ flat_profile_abs_z_max → 写入 `meta.qualityNote` 降权提示（01 章渲染），全篇按扁平策略撰写（interpretation-library §7），咨询师备注同步降权
   - 极端应答：全维度同向 |z| > extreme_responding_abs_z_gt → 备注警告社会赞许性（不入报告）
   - 同维度子维度 z 极差 ≥ facet_contradiction_spread_min → 标记矛盾维度（interpretation-library §2；落点在 02 章 line + 03 优盲卡，不单独成章）
5. 1 人 → 单人流程；2 人 → **双人流程**：见 `references/couple-template.md` §6。双方数据必须齐全（不齐则停）；非恋爱关系、或要求"是否合适"类判断 → 拒做

### Phase 1: 核心分析（产出"文案方向"，不写正文）

| 分析 | 规则文件 | 何时读 |
|------|---------|--------|
| 15 子维度含义 + 画面 + 矛盾组合表 | `references/interpretation-library.md` §1–§2 | 每次必读 |
| **分数模式 → 各章文案素材 + 扁平策略** | `references/interpretation-library.md` §3–§7 | 写文案前必读 |
| 语言、句式骨架、禁词 | `references/writing-style.md` | 每次必读 |
| 维度定义、方向细则、常模与文化提示 | `references/scoring-interpretation.md` | 方向/常模有疑问时按需 |
| **理论判据、可分析性白名单/黑名单** | `references/bigfive-theory.md` | 拿不准某结论该不该写/能不能推时按需 |
| 模板 schema 与生成流程 | `references/html-templates.md` | Phase 2 前必读 |
| 双人（关系工具书）规范 + schema | `references/couple-template.md`（+ `design-spec.md` 配色） | 仅双人 |

分析要点（内部结论，供写文案用）：
- 排出最突出/最靠后/内部矛盾最大的 3–4 条线（封面标签与 oneliner 的原料）；扁平剖面按 interpretation-library §7 走
- 从 interpretation-library §3 挑优势/代价组合：**数量由分数分布决定**——组合明显时 3–5 组，不明显时允许 2 组并加降级说明句；须真实对应该来访者档位，不硬凑
- 亲密/成长按 interpretation-library §4–§5 挑触发项
- 与样例画像雷同的组合，换切入角度重写（writing-style R7）

### Phase 2: 生成报告 HTML（模板填充，不手写代码）

1. 复制 `templates/report-template.html` → 目标文件（命名 `bfi2_{代号}.html`，代号重复则问 v2/覆盖）
2. 整块替换 `const REPORT = {...}`：数值全部取自 compute 输出（Stop rules「数值不手算」）；文案按 writing-style §4 句式骨架 + interpretation-library 素材撰写。**模板数据块自带示例数据（alias=zyh、date=2026-09-05 等），必须整块替换；只改一部分会被 lint 的「未替换模板示例」检查 FAIL**
3. 字段清单与 schema：html-templates §2；缺 lint 必查字段即返工——3 chips / 3 behaviors / 3+3+3 love / strengths·flaws·growth·faq 各 3–5（扁平剖面 strengths·flaws·growth 放宽为 2–5）
4. `es` 域必带 `note`（方向小注）；`meta.domain4Note/normLabel/normDetail` 按所选常模填写
5. 双人：按 `references/couple-template.md` §6 流程执行（复制 couple 模板 → 填 P 原始分 + COUPLE_CONTENT → lint 新版双人）

### Phase 3: 验证（不通过则修复重来）

1. `python scripts/lint_report.py <报告文件>` → `PASS: all checks passed（新版单人 / 新版双人）`；双人检查项清单见 couple-template.md §6
   - 新两条检查：①**模板一致性**——`<style>` 块与渲染层 JS 必须与 `templates/report-template.html` 逐字节一致（数据块之外一个字节都不许动）②**模板示例文案不得逐字复用**（数据块须整块替换；`partnerTitle`/`partnerCap`/`tags`/`meta` 豁免）
2. **浏览器检查仅在必要时做**：模板/脚本/lint 变更后首次生成、lint 报渲染类 FAIL、或换新环境首次交付。检查点清单：单人 html-templates §6.3，双人 couple-template.md §6.5；日常填充数据默认跳过（渲染层由基线回归守护）
3. 基线回归（改过模板/脚本/lint 时）：`python scripts/run_regression.py` → 四条基线全 PASS 才继续
4. 全部通过才允许交付

### Phase 4: 交付 + 咨询师备注

对话中汇报（不入文件）。**按原则写，不按清单凑**——凡在报告里被迫加糖或被迫沉默的，在这里说原话。常见落点举例（非全集）：

```
【咨询师备注】
- 最显著特征：……
- 子维度矛盾项：……
- 数据质量：正常 / 异常模式说明（社会赞许风险、作答风格）
- 阈值边界敏感项（pct 贴近档位切分点的条目）：……
- 低信度项：若来访者属青少年/低学历，点名哪些子维度 α 偏低、其结论仅作参考
- 常模选择的不确定性：按年龄/身份就近选择时，注明局限
- 双人时：临界桥说明（Δz 落在 boundary_bridge_dz 区间、贴桥阈值的面子标注"边界判断"）+ 双方作答质量对比（若一方扁平/极端，桥结论降权）
```

## Success criteria

**来访者体验是目标，科学性是约束；两者冲突时科学性优先。** 一份让来访者"被看见"但说错了的报告是伤害而非帮助——"被看见"可以被措辞技巧伪造，科学性不能。

交付前下列条件必须全部为真：

- 每条结论可追溯到具体分数与档位；推演一律软措辞（"可能/倾向于/常常"）
- 无"研究证实你如何如何"式伪引用；无诊断语气；分数不与价值挂钩
- Phase 3 全部通过：`lint_report.py` PASS；改过模板/脚本/lint 时四条基线回归 PASS
- 报告已保存到输出路径
- 咨询师备注已在对话中给出，未写进任何文件

## Stop rules（决策规则）

- **证据立场**：推测一律软化措辞；无文献出处不得写"研究证实"（不挂证据标签，护栏在措辞+模板固定免责，见 writing-style §7）
- **原理字段来源**：成长卡「原理：…」只允许复用 interpretation-library §5 库内既有原理句；库外组合不写原理（禁止即兴编造机制解释）
- **第 4 域方向**：负性方向输入先回显确认再翻转，禁止静默翻转（细则 scoring-interpretation §1.2）
- **代号/常模缺失**：Phase 0 清单补齐再继续
- **双人数据不齐 / 非恋爱关系 / 要匹配分**：不硬写双人报告（停，等另一方数据或拒做）
- **数值不手算**：唯一数值执行器 = compute_scores.py（单人注入）与双人模板浏览器端计算；两侧手填派生值 lint 必 FAIL
- **阈值不凭记忆**：扁平/矛盾/显著/双人的具体数值一律查 `references/thresholds.json`（单一真相源）；凭印象写错不报错，只会让结论默默走偏
- **常模数据内置**：唯一源 `references/bfi2_norms_cn.json`；双人换人群需同步换模板内 NORM 表并由 lint 逐值校验
- **数量诚实**：组合卡/成长卡宁缺毋滥，不足时用降级说明句，不硬凑（interpretation-library §3、§7）

## Context / Input

- **量表**：Big Five Inventory-2 中文修订版（BFI-2），60 题，5 维度 × 3 子维度/维度
- **输入契约**：固定格式的**文本表或 JSON**，含 5 维度 + 15 子维度**原始分**（1–5 条目均值刻度）；可附年龄、关系背景。输入中若带 z/等级/M/SD 列一律忽略（派生值规则见 Stop rules「数值不手算」）
- **输出路径**：默认 `~/Desktop`；用户指定时从其指定

## Constraints（边界 / Out of scope）

判据（第一性原理）：本 skill 只做一件事——把 BFI-2 原始分翻译成中文来访者报告（见 Goal）。凡这个目的不要求的加做能力、或仪器效度/咨询伦理不支撑的用途，一律拒做，不做折中。

- **不做心理诊断与治疗建议**——特质报告不是诊断；情绪困扰升级只走模板固定求助 callout
- **不用于高利害决策**——招聘/选拔不用；双人报告不评匹配分、不判"合不合/要不要继续"（工具书只翻译差异，婚恋"是否合适"类要求拒做）
- **不做职业决策结论**——报告无职业章；追问在对话中以"倾向参考"口径回答

## Gotchas（常见陷阱）

**真事故（必看）**：
- 手填/微调 z、pct → lint 复算直接 FAIL
- 阈值凭印象（如把扁平判据记成 0.5）→ 不报错，但扁平剖面被当成有张力写

**其余**：
- 把样例文案照搬给新来访者（R7）→ 句式同、措辞必须变
- **只改了数据块的一部分**：数字换了、标题/lead/FAQ 仍沿用模板示例原文 → lint「模板示例复用」FAIL（此前该守卫只查 alias+date+封面三项，太窄，已加宽）
- **动了数据块之外**（顺手改 CSS 或渲染层 JS）→ lint「模板一致性」FAIL；要改视觉必须先改模板再重生成
- REPORT 数据块里写注释 → lint JSON 解析失败（模板已注明）
- es 域忘填 `note` 小注、或正文出现"焦虑高=稳定"方向混用 → 180° 误读
- 改模板/脚本/lint 后没跑 `scripts/run_regression.py` → 所有新报告继承同一 bug
- 双人专属陷阱（往 P 塞 z/pct、手填桥名单等）见 couple-template.md §8

## References（文件索引）

**模板**
- `templates/report-template.html` — 单人模板骨架（CSS/JS/图表固定，见 html-templates）
- `templates/couple-report-template.html` — 双人模板骨架（十章关系工具书，浏览器端计算，见 couple-template）

**脚本**
- `scripts/compute_scores.py` — 原始分 → z/百分位/档位/刻度；`--scores` 扁平 JSON、`--export` 平台导出 JSON、`--couple` 出 Δz/选桥/共鸣复算（常模计算唯一执行器）
- `scripts/lint_report.py` — 质量闸门（单人=注入值复算；双人=浏览器端契约+NORM对齐+选桥复算+双人禁词）
- `scripts/run_regression.py` — 四条基线 lint 回归（改模板/脚本/lint 后必跑）

**参考**
- `references/scoring-interpretation.md` — 维度定义、五档分位、方向规则、常模与文化提示
- `references/interpretation-library.md` — 15 子维度含义+画面（§1）、同域矛盾表（§2）、跨条目组合（§3）、亲密（§4）、成长（§5）、封面（§6）、扁平策略（§7）
- `references/bigfive-theory.md` — **理论基石**：大五理论综述、可分析性白名单/黑名单、skill 规则的理论依据、幻觉清单
- `references/writing-style.md` — 语气、句式骨架、禁词表、弱护栏规范
- `references/html-templates.md` — 单人：生成流程、REPORT schema、七章结构、输出与验证
- `references/couple-template.md` — 双人：十章结构、COUPLE_CONTENT schema、选桥/共鸣契约、生成流程、专属语气与禁词、双人陷阱
- `references/design-spec.md` — **设计规范（以 `templates/report-template.html` 为真相源）**：色板（`:root` 层 + 硬编码层）、字体版式、组件清单与图形编码、各章节配色映射、响应式/动效/打印、禁区、已知语义冲突；双人增量见 §6
- `references/bfi2_norms_cn.json` — 中国常模（Zhang et al. 2022 Table 1，三样本），z 计算唯一数据源
- `references/thresholds.json` — **静默失效阈值的单一真相源**（扁平/矛盾/显著/双人 Δz/五档切分）

**样例**
- `examples/bfi2_sample.html` — 单人基线（模板骨架 + 另一套合成画像「hx」，lint 新版单人 PASS 基准；与模板内置示例数据不同，防止把模板示例当样例）
- `examples/bfi2_sampleA_sampleB.html` — 双人基线（= 双人模板 + 合成 COUPLE_CONTENT，lint 新版双人 PASS 基准）
