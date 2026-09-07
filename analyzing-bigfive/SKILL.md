---
name: analyzing-bigfive
description: 基于 BFI-2（Big Five Inventory-2）维度与子维度分数做大五人格分析，生成来访者视角的 HTML 报告（单人报告；双人时为恋人关系工具书，只翻译差异与相处协议，不评匹配分；读者为无心理学背景的年轻读者）。当用户提供 5 维度 + 15 子维度原始分（单人一份或双人两份），或要求 BFI-2 报告、大五人格分析、人格剖面分析、伴侣大五差异工具书时使用。只接受原始分输入，不负责从 60 题原始答题计分
---

# AnalyzingBigfive — BFI-2 大五人格分析

## Goal

用户是**心理咨询师**；报告的读者是**来访者**（无心理学基础的年轻读者）。每次分析产出两样东西：

1. **报告 HTML**（终端产品，100% 来访者视角，零术语、全画面）→ 由数据驱动模板生成，保存为文件：单人 `templates/report-template.html`（七章结构），双人（恋人）`templates/couple-report-template.html`（十章关系工具书，规范见 `references/couple-template.md`）
2. **咨询师备注**（低置信度结论、阈值边界项、作答质量、会谈核实建议）→ 只在对话中汇报，不写进任何文件

## Context / Input

- **量表**：Big Five Inventory-2 中文修订版（BFI-2），60 题，5 维度 × 3 子维度/维度
- **输入边界**：入口是 **bfi2_interactive.html 的导出 JSON**（外部页面，不属本 skill，本机路径见 README「本机专属配置」；5 维度 + 15 子维度原始分，1–5 条目均值刻度）。可附年龄、关系背景。**不负责从 60 题原始答题计分**；输入中的 z/等级/M/SD 列一律忽略（派生值规则见 Stop rules「数值不手算」）
- **输出路径**：默认 `~/Desktop`；用户指定时从其指定

## Constraints

- **科学立场（双层解读）**：常模层=相对常模人群的位置（02 章游标条、分数表、档位标签）；自比层=自身 15+5 条目的相对强弱与内部矛盾（02 章文案、03 优盲）。两层缺一不可
- **呈现规范**：五档百分位（档位与阈值由 compute 脚本输出），规则见 `references/scoring-interpretation.md` §2.1

## Workflow

```
任务进度（复制此清单并逐项勾选）：
- [ ] Phase 0: 输入解析与质量检查
- [ ] Phase 1: 核心分析（画像、组合、章节文案方向）
- [ ] Phase 2: 跑 compute + 填模板数据块
- [ ] Phase 3: 验证（lint + 浏览器检查）
- [ ] Phase 4: 交付 + 咨询师备注
```

### Phase 0: 输入解析与质量检查

1. **缺失信息询问清单（一次性列出，不逐个追问）**：缺什么问什么，已有不重复问——
   - **代号**：单人 1 个（如 zyh / A001）；双人 2 个（文件名用，报告内以 A/B 相称）
   - **人数**：1 人 / 2 人（双人 → 关系工具书流程，见 couple-template.md）
   - **常模**：a) 中国大学生（默认）b) 在职员工 c) 青少年（仅维度层稳妥）d) 按年龄就近并注明
   模板：
   ```
   开始前还差几项信息，请一起补齐：
   - 报告代号（如 zyh 或 A001）：
   - 人数：1 人 / 2 人？
   - 常模：a) 中国大学生（默认）b) 在职员工 c) 青少年 d) 不确定（按年龄就近，注明局限）
   ```
2. 输入一律为 bfi2_interactive.html 导出 JSON（单人 20 项；双人 40 项，两份文件各 20 项）。**跑计算脚本**：
   - 单人 → `python scripts/compute_scores.py --export <file>`（自动取 `scores.stability`，忽略 `scores.raw`）
   - 双人 → `python scripts/compute_scores.py --couple <A.json> <B.json> --norm …`（回显 Δz 全表 + 选桥/共鸣集合；报告内数值由模板浏览器端计算，脚本结果用于回显与 lint 复算）
   - 回显解析结果与所用常模；正常输入无需等确认；双人常模默认同一套，不一致先问
3. **第 4 域方向**：一律按稳定性方向（规则见 Stop rules「第 4 域方向」；scoring-interpretation §1.2）。双人：`P.a/P.b` 直接填各自导出的稳定性分，`meta.flippedA/flippedB` 保持 false。
4. 质量检查（基于计算输出）：
   - 完整性：20 项齐全，原始分 1–5，z 在 −3~+3
   - 扁平剖面：全维度 |z| ≤ 0.3 → 降权提示"作答可能不够认真，结论仅供参考"
   - 极端应答：全维度同向 |z|>1 → 备注警告社会赞许性
   - 同维度子维度 z 极差 > 2 → 标记矛盾维度（facet-analysis §2；落点在 02 章 line + 03 优盲卡，不单独成章）
5. 人数：1 人 → 单人流程；2 人 → **双人流程**（couple-template.md，关系工具书）：双方数据必须齐全（不齐则停）；产出 = 1 份双人工具书（可按需各出 1 份单人子报告）。双人非恋爱关系、或来访者要求"是否合适"类判断 → 拒做（out-of-scope）。

### Phase 1: 核心分析（产出"文案方向"，不写正文）

| 分析 | 规则文件 | 何时读 |
|------|---------|--------|
| 维度/档位/方向/常模规则 | `references/scoring-interpretation.md` | 每次必读 |
| 15 子维度含义 + 矛盾组合表 | `references/facet-analysis.md` | 每次必读 |
| **分数模式 → 各章文案素材** | `references/interpretation-library.md` | 写数据块前必读 |
| 语言、句式骨架、禁词 | `references/writing-style.md` | 每次必读 |
| 模板 schema 与生成流程 | `references/html-templates.md` | Phase 2 前必读 |
| 双人（关系工具书）规范 + schema | `references/couple-template.md`（+ `design-spec.md` 配色） | 仅双人 |

分析要点（内部结论，供写文案用）：
- 排出最突出/最靠后/内部矛盾最大的 3–4 条线（封面标签与 oneliner 的原料）
- 从 interpretation-library §2 挑 3–5 组优势组合、3–5 组代价组合（须真实对应该来访者档位，不是套模板）
- 亲密/成长按 library §3–§4 挑触发项
- 与样例画像雷同的组合，换切入角度重写（writing-style R7）

### Phase 2: 生成报告 HTML（模板填充，不手写代码）

1. 复制 `templates/report-template.html` → 目标文件（命名 `bfi2_{代号}.html`，代号重复则问 v2/覆盖）
2. 整块替换 `const REPORT = {...}`：数值全部取自 compute 输出（不手算，见 Stop rules）；文案字段按 writing-style §4 句式骨架 + interpretation-library 素材撰写
3. 字段清单与 schema：html-templates §2；缺 lint 必查字段（3 chips / 3 behaviors / 3+3+3 love / ≥3 growth+faq）即返工
4. `es` 域必带 `note`（方向小注）；`meta.domain4Note/normLabel/normDetail` 按所选常模填写
5. **双人**：复制 `templates/couple-report-template.html` → 目标文件（命名 `bfi2_{代号A}_{代号B}.html`）→ 填 `P.a/P.b`（仅原始分 + 各域关系语境 line，严禁派生值——见 Stop rules；报告内数值由模板浏览器端计算）→ 填 `COUPLE_CONTENT` 整块（schema 见 couple-template.md §3；桥/共鸣名必须与 `--couple` 回显集合一致）→ 非学生人群按 JSON 换 `NORM` 表并声明 `meta.norm`。双人禁词、对称语气见 couple-template.md §5。

### Phase 3: 验证（不通过则修复重来）

1. `python scripts/lint_report.py <报告文件>` → 单人 `PASS: all checks passed（新版单人）` / 双人 `PASS: all checks passed（新版双人）`。lint 自动按数据块标记分流：单人查 schema + 常模复算（z/pct/tick）+ 档位一致 + 禁词 + 7 锚点/求助 callout/免责/打印；双人查 COUPLE_CONTENT schema + P 原始分范围 + **禁服务端注入 z（浏览器端契约）** + NORM 表逐值对齐内置 JSON + **选桥/共鸣复算集合相等** + 双人专属禁词 + 11 锚点/安全边界/暂停恢复复盘三卡/打印
2. 浏览器检查（打开文件）：单人——雷达顶点与 z 标注吻合、游标停在正确档位段、分数表 20 行、打印预览无断裂；双人——叠加雷达两轮廓（A 实线/B 虚线）、桥带双游标与 Δz 一致、共鸣≤3、桥 ≤6（可为 0，渲染空态卡，不硬凑差异）、附录 21 行 + 方向标注、黑白打印 A/B 可辨
3. 基线回归（改过模板/脚本/lint 时）跑四条，全 PASS 才继续：`templates/report-template.html`、`examples/bfi2_sample.html`（单人新版）、`templates/couple-report-template.html`、`examples/bfi2_sampleA_sampleB.html`（双人新版）
4. 全部通过才允许交付

### Phase 4: 交付 + 咨询师备注

对话中汇报（不入文件）：

```
【咨询师备注】
- 最显著特征：……
- 子维度矛盾项：……
- 数据质量：正常 / 异常模式说明
- 阈值边界敏感项（pct 靠近 10/35/65/90 的条目）：……
- 双人时：临界桥说明（Δz 在 0.6–0.8、贴 0.7 线的面子标注"边界判断"）+ 双方作答质量对比（若一方扁平/极端，桥结论降权）
```

## Success criteria

- `scripts/lint_report.py` 对报告文件全部 PASS（单人→新版单人 / 双人→新版双人）
- 双层解读成立：常模层（游标/分数表）+ 自比层（文案与优盲由内部格局推出）
- 报告无裸断言：推演类文案用"可能/倾向于/常常"；无"研究证实"式伪引用
- 无样例照搬：封面标签、卡标题、oneliner 与样例句式同而措辞异
- 文件名 `bfi2_{代号}.html` / `bfi2_{代号A}_{代号B}.html`；代号缺失已问询
- 咨询师备注只在对话中，未写入文件
- 数值全部可追溯：单人 z/pct 与 compute 输出一致；双人 z 由模板 NORM 表浏览器端算，lint 复算一致
- （双人）不给匹配分、不判合分；差异双面解读（摩擦 + 互补）；安全边界 callout 在位

## Out of scope（放弃清单）

判据（第一性原理）：本 skill 只做一件事——把 BFI-2 原始分翻译成中文来访者报告（见 Goal）。凡这个目的不要求的加做能力、或仪器效度/咨询伦理不支撑的用途，一律拒做，不做折中。

- **不从 60 题原始答题计分**（走交互页）——输入边界
- **不做心理诊断与治疗建议**——特质报告不是诊断；情绪困扰升级只走模板固定求助 callout
- **不用于高利害决策**——招聘/选拔不用；双人报告不评匹配分、不判"合不合/要不要继续"（工具书只翻译差异，婚恋"是否合适"类要求拒做）
- **不做职业决策结论**——报告无职业章；追问在对话中以"倾向参考"口径回答

## Stop rules

- **证据立场**：推测一律软化措辞；无文献出处不得写"研究证实"（不挂证据标签，护栏在措辞+模板固定免责，见 writing-style §7）
- **第 4 域方向**：输入一律是交互页导出，脚本自动取 `scores.stability`、禁用 `scores.raw`；非导出格式输入先回显确认方向再跑（禁止静默翻转）
- **代号/人数/常模缺失**：Phase 0 清单补齐再继续
- **双人数据不齐 / 非恋爱关系 / 要匹配分**：不硬写双人报告（停，等另一方数据或拒做）
- **数值不手算**：单人 z/pct/tick 只认 compute 脚本输出；双人只填原始分、派生值交给模板浏览器端计算——两侧手填派生值 lint 必 FAIL
- **常模数据内置**：唯一源 `references/bfi2_norms_cn.json`，不读交互页常模；双人换人群需同步换模板内 NORM 表并由 lint 逐值校验

## 常见陷阱

- 把样例文案照搬给新来访者（R7）→ 句式同、措辞必须变
- 手填/微调 z、pct → lint 复算直接 FAIL
- REPORT 数据块里写注释 → lint JSON 解析失败（模板已注明）
- es 域忘填 `note` 小注、或正文出现"焦虑高=稳定"方向混用 → 180° 误读
- 档位词与实际百分位不符（"效率 · 偏低"实为远低）→ lint FAIL
- 亲密章预设"你对象" → 违反泛化措辞规则（library §3）；双人同理不预设婚育状态
- 双人往 `P` 里塞 z/pct（沿用单人习惯）→ lint「禁服务端注入 z」FAIL；双人只填原始分
- 双人手填桥/共鸣名单（不跑 --couple 或不与模板选桥一致）→ lint 集合相等校验 FAIL
- 改模板后没跑基线回归（4 条）→ 所有新报告继承同一 bug

## References

- `templates/report-template.html` — 单人模板骨架（CSS/JS/图表固定，见 html-templates）
- `templates/couple-report-template.html` — 双人模板骨架（十章关系工具书，浏览器端计算，见 couple-template）
- `scripts/compute_scores.py` — 原始分 → z/百分位/档位/刻度；`--couple` 出 Δz/选桥/共鸣复算（常模计算唯一执行器）
- `references/html-templates.md` — 单人：生成流程、REPORT schema、七章结构、输出与验证
- `references/couple-template.md` — 双人：十章结构、COUPLE_CONTENT schema、选桥/共鸣契约、专属语气与禁词、安全边界
- `references/design-spec.md` — 单/双共用颜色语义与图形编码（三层色板、五段带、打印、禁区）
- `references/writing-style.md` — 语气、句式骨架、禁词表、弱护栏规范
- `references/interpretation-library.md` — 分数模式 → 文案方向素材库（**初稿，待咨询师终审**）
- `references/scoring-interpretation.md` — 维度定义、五档分位、方向规则、常模与文化提示
- `references/facet-analysis.md` — 15 子维度含义、矛盾组合速查
- `references/bfi2_norms_cn.json` — 中国常模（Zhang et al. 2022 Table 1，三样本），z 计算唯一数据源

## Examples

- `examples/bfi2_sample.html` — 单人基线（= 模板 + 合成数据，lint 新版单人 PASS 基准）
- `examples/bfi2_sampleA_sampleB.html` — 双人基线（= 双人模板 + 合成 COUPLE_CONTENT，lint 新版双人 PASS 基准）
