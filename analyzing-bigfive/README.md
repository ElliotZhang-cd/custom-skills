# analyzing-bigfive

基于 BFI-2（Big Five Inventory-2 中文修订版）维度与子维度分数做大五人格分析，生成来访者视角 HTML 报告。使用者是心理咨询师，读者是无心理学基础的来访者。**v3（2026-09-07）起单人报告为数据驱动模板**：固定骨架（`templates/report-template.html`）+ 一个 `REPORT` 数据块，暖纸色封面/雷达/百分位游标条视觉，全篇零术语、画面化文案。**双人（恋人）报告为 v3 关系工具书**：`templates/couple-report-template.html`（十章，讲差异翻译与相处协议，不评匹配分；规范见 `couple-template.md`）。

## 触发

咨询师提供 5 维度 + 15 子维度的**原始分**（计分平台固定输出的文本或 JSON；单人一份或双人两份），或要求 BFI-2 报告、大五人格分析、人格剖面分析、伴侣大五差异工具书（v3 单人报告无职业/压力/人际独立章节）。

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
│   ├── lint_report.py              # 质量闸门（单人=注入值复算；双人=浏览器端契约+NORM对齐+选桥复算+双人禁词）
│   └── run_regression.py           # 基线回归：四条基线文件 lint 全 PASS 才退出 0
├── references/
│   ├── html-templates.md           # 单人：生成流程、REPORT schema、七章结构、输出与验证
│   ├── couple-template.md          # 双人：十章结构、COUPLE_CONTENT schema、选桥/共鸣契约、专属语气与安全边界、双人陷阱
│   ├── design-spec.md              # 单人设计规范（以模板为真相源）：色板/版式/组件/配色/打印/禁区/已知冲突；双人增量见 §6
│   ├── writing-style.md            # 语气、句式骨架、禁词表、弱护栏规范
│   ├── scoring-interpretation.md   # 维度定义、五档百分位、方向规则、常模与文化提示
│   ├── interpretation-library.md   # 15 子维度含义+画面、同域矛盾表、跨条目组合、亲密、成长、封面、扁平策略
│   ├── bigfive-theory.md           # 理论基石：大五理论综述 + 可分析性白名单/黑名单 + 规则溯源 + 幻觉清单
│   ├── thresholds.json             # 静默失效阈值的单一真相源（扁平/矛盾/显著/双人 Δz/五档切分）
│   └── bfi2_norms_cn.json          # 中国常模数据（唯一常模真相源）
├── examples/
│   ├── bfi2_sample.html            # v3 单人基线（模板骨架 + 另一套合成画像 hx，新版单人 lint PASS）
│   └── bfi2_sampleA_sampleB.html   # v3 双人基线（新版双人 lint PASS）
└── evals/evals.json                # 6 个行为回归用例（方向翻转/不翻转/询问清单/双人/扁平/极端）
```

## 回归与评估

```bash
python scripts/run_regression.py   # 基线回归（改过 templates/ 或 scripts/ 后必跑）
python scripts/lint_report.py <报告文件>   # 单份报告的 lint
```

`evals/evals.json` 是 6 个行为用例（输入 → 预期行为），供人工/会话级回放，不属于自动 lint。

## 真相源链路

1. **原始分**：来访者在计分平台完成 60 题作答，平台输出固定格式分数（文本或 JSON）；本 skill 不做 60 题计分、不感知平台。
2. **单人 z/百分位**：`scripts/compute_scores.py` 读 `references/bfi2_norms_cn.json` 计算，注入 `REPORT`；lint 复算比对，不一致 FAIL。
3. **双人 z/百分位/Δz/选桥/共鸣**：模型只填原始分到 `P`，由双人模板内嵌 NORM 表**浏览器端计算**（`meta.norm` 声明用了哪套人群）；`compute_scores.py --couple` 供 Phase 0 回显、lint 复算选桥集合与 NORM 表逐值对齐 JSON。
4. **方向约定**：第 4 域一律按「情绪稳定性」方向（平台固定输出 JSON 时脚本自动取 `scores.stability`、禁用 `scores.raw`；文本表按 label 判方向，负性方向先回显确认）；焦虑/抑郁/易变子维度恒为本义方向（高分 = 更敏感）。
5. **档位**：百分位五档——远低 <10 / 偏低 <35 / 中间 <65 / 偏高 <90 / 远高 ≥90（切分点数值唯一真相源 `references/thresholds.json`）。
6. **视觉**：一切以 `design-spec.md` 为准，而 design-spec 以 `templates/report-template.html` 为**真相源**——**改视觉必须先改模板**，再同步 design-spec 并重跑四条基线 lint（反向不成立）。两份模板五维身份色须一致。
7. **阈值**：扁平/矛盾/显著/双人 Δz 等「影响模型判断」的阈值一律查 `references/thresholds.json`——写错不报错，只会让结论默默走偏。compute_scores 与 lint 都从它读取，不得各自硬编码。

## 版本沿革

- **v3.5（2026-09-24，当前）**：**SKILL.md 按 authoring-skills 规范重构（先做结构重构，再按用户要求删掉五处内容）**。①章节改为规范骨架 `Goal / Workflow / Success criteria / Stop rules` + 可选 `Context / Input`、`Constraints`、`Gotchas`、`References`，中文原章节名保留在括号内（`Out of scope`、`Stop rules「数值不手算」` 等既有交叉引用仍能命中）；②分析框架（L1–L5）与任务进度清单收进 `Workflow`，Phase 0–4 编号与顺序不变（`run_regression.py` 引用的 Phase 3.3 仍指基线回归）；③「成功判据」由单段原则扩为**原则 + 交付前必须为真的五条**（可追溯/无伪引用/lint 与回归 PASS/报告已保存到输出路径/备注已给）；④**删除五处**：成功判据的「信息量诚实」条与「正文只出现代号、无真名」子句、`Constraints` 的「不从 60 题原始答题计分——输入边界」条、`Gotchas` 的第 4 域静默翻转案例（A001）与真名泄露条；⑤**description 重写为 `Does X and Y. Use when Z.` 两段式并压到约 90 字**——原文边界夹在触发句后、括注混进交付物结构与读者说明；新版第一句 = 能力 + 边界（来访者视角、不做诊断），第二句给触发条件，触发关键词全部保留；⑥同步 `bigfive-theory.md` §0.2 分工表中的 SKILL.md 章节名；顺带修掉 README 的重复条目与错位的代码围栏、清掉 `scripts/__pycache__`。**未动**：Phase 步骤与阈值、模板/lint/脚本。⑦**第二轮按用户要求再删四处**：`Context / Input` 与 description 的「不负责从 60 题原始答题计分」（连同「计分在平台完成，本 skill 不感知平台」一并去掉——都不是本 skill 的业务范围）、`bigfive-theory.md` §8 的同一句、`html-templates.md` §6.2 的「报告不含来访者真名，只用代号」（**真名规则整体去掉**；「代号不渲染进页面」另见该文件 §2 数据块注释）、`evals/evals.json` 用例 1 删掉「雷达图情绪稳定性轴端 z 与正文一致（无符号翻转）」这条断言。**删除后仍存在的相关位**：①第 4 域方向规则本身仍受 `Stop rules`「第 4 域方向」条约束（去掉的只是 Gotchas 案例与 eval 断言）；②README「真相源链路」第 1 条仍描述平台计分链路（面向维护者的数据来源说明，未动）。
- **v3.4（2026-09-23）**：**lint 补齐两条静默失败检查 + 基线修复**。①**加宽「模板示例复用」检查**：原守卫只在 alias+date+封面三项同时命中时才触发，实测过窄——v3 生成时 `love.h2`/`growth.lead`/成长卡/FAQ 逐字沿用模板示例却 PASS；现改为比对数据块全部自由文案（≥12 字），豁免 `partnerTitle`（库内规定用语）/`partnerCap`/`tags`/`meta`；②新增**模板一致性**检查（`<style>` 块与渲染层 JS 必须与 `templates/report-template.html` 逐字节一致——数据块之外不得改动）；③发现并修复 **`examples/bfi2_sample.html` 基线已过时**——其雷达 JS 停留在无 `RADAR_R0` 的旧公式（极端值落向圆心，changelog V9 的修复没同步进基线），已用模板重建渲染层并重写其 7 条复用示例文案；④`bfi2_zyl-v2.html` 同步修掉 1 条残留复用。回归 4/4 PASS，两条新检查均已正向测试（能拦且零误报）。**决策修订**：原计划的「砍 3 条口味检查」**未执行**——两轮实测数据显示禁词检查产出 4 个真阳性、0 误报（零术语是产品要求，违规有后果），故保留。**已否决**：`--forbid-name` 真名检查（曾提议并实现，按决定移除；真名泄露改为人工扫描，见 SKILL.md 陷阱）。
- **v3.3（2026-09-23）**：**设计规范按模板重写（单人部分）**。`references/design-spec.md` 92→约 200 行，改以 `templates/report-template.html` 为**真相源**逆向提取：①新增字体版式（字族/字号级差）、组件清单与逐组件图形编码、响应式断点、动效参数、**`:root` 之外 11 处硬编码色值清单**、**6 条已知语义冲突**（`#7C9B6D` 一色两义、雷达数据轮廓刻意用中性墨色、`--neutral` 仅单人模板有、雷达轴序≠维度块序、facet 填充是 score/5 而非百分位等）；②补回旧 `DESIGN_SPEC.md` 丢失的「各章节配色映射」与五维色出处，**修正其两处错误**（轨道刻度写"50%"实为常模均值 M/5×100；"远高 >90%" 应为 ≥90）；③确认旧 spec 的 `--aA/--aB` 从未落地、可安全废弃；④明确维护方向：**改视觉必须先改模板**，design-spec 是描述而非源头。§6 双人增量保留既有条目、待同法重写。同步更新 SKILL.md / html-templates / couple-template / README 的引用描述。
- **v3.2（2026-09-23）**：**按第一性原理 + 奥卡姆剃刀重建（只砍重复与组织，不动机制与范围）**。①SKILL.md 重构为「组织原则 / 决策规则 / 执行流程」三层，新增**分析框架节**（2 计算层 L1 常模层+L2 自比层 / 2 生成纪律 L3 组合+L4 推演 / 2 register 报告+咨询师备注）；②咨询师备注改为**按原则定义**（"凡在报告里被迫加糖或被迫沉默的，在这里说原话"），原五项降为举例；③新增 `references/thresholds.json` 作**静默失效阈值单一真相源**（扁平/矛盾/显著/双人 Δz/五档切分），compute_scores 与 lint 改为读它、不再各自硬编码；④`facet-analysis.md` 整体并入 `interpretation-library.md`（15 子维度含义+画面合为一张表，同域矛盾表转为 §2），文件删除；⑤`bigfive-theory.md` 658→约 470 行（删与 SKILL.md/html-templates/thresholds.json 重复的框架段、八步算法、阈值总表、章节映射；画面归位到解读库）；⑥`scoring-interpretation.md` 删 §3.3（100% 是矛盾表子集）、双人条款收敛为指针；⑦双人停止向单人文件渗透（writing-style/html-templates/README 复述收敛为指针；design-spec 作为单双共用色板规范保持不变）。**未动**：模板注入方式、lint 检查项集合、15 子维度全量输出、双人子系统机制、输入边界。
- **v3.1（2026-09-12）**：流程精简——双人规范整体下沉 `couple-template.md`（SKILL.md 只留分流）；输入契约改为"平台固定输出的文本或 JSON"（skill 不感知平台）；问询清单精简为代号+常模两项（人数默认单人，两份数据或明示触发双人）；重复规则收敛到唯一规范位；浏览器检查改为条件触发（新增 `scripts/run_regression.py` 基线回归命令）；内容层新增数量弹性规则与扁平剖面文案策略、成长动作库扩容至 16 条、「原理」字段限定库内原理句；分数引用改为「子维度 · 档位」制（禁裸原始分），lint 同步升级。
- **v3（2026-09-07）**：单人报告改为数据驱动模板（固定骨架 + `REPORT` 数据块）；双人改为十章关系工具书（只翻译差异，不评匹配分）。v2 的应用章素材（`references/applied-analysis.md`）与双人规则（`references/couple-dynamics.md`）随之停用，2026-09-08 起两个文件已删除。

## 本机专属配置（换机器需改）

| 可移植写法（SKILL.md 中） | 本机实际路径 |
|---|---|
| `~/Desktop`（默认报告输出目录） | `C:/Users/elliot/Desktop` |

## 明确不做

见 SKILL.md「Out of scope」：不从原始答题计分、不做心理诊断与治疗建议、不用于高利害决策（招聘/选拔不用；双人工具书不评匹配分、不判"合不合/要不要继续"）、不做职业决策结论。
