# HTML 输出模板（v3 · 数据驱动）

所有报告 = 来访者直接阅读的终端产品，默认保存到 **`~/Desktop`**（本机实际路径见 README「本机专属配置」）。语言规范见 writing-style.md。

> **本版为 2026-09-07 重构后的模板，唯一视觉与结构事实源 = `templates/report-template.html`。**
> 报告不再手写 HTML：复制模板 → 整块替换 `const REPORT = {...}` 数据块 → 跑 lint → 浏览器检查。
> CSS/JS/图表渲染逻辑一律不改（改模板 = 改本规范 + 重跑基线 lint）。
> **双人报告（恋人工具书）另用 `templates/couple-report-template.html`，规范见 `couple-template.md`**——数据契约不同（浏览器端计算），不要用单人模板。
> **颜色语义与图形编码的唯一规范：`design-spec.md`**（以 `templates/report-template.html` 为真相源逆向提取）；百分位带为「五段同色 + 活跃档维度色高亮(42%+内描边) + 3px 无点游标 + 档名加粗着色」满配样式。改视觉 = 先改模板 → 再同步 design-spec → 重跑基线。

## Contents
- §1 生成流程（复制模板 → 填数据块）
- §2 REPORT 数据块 schema（字段逐一说明）
- §3 七章结构与各字段文案要求（对齐新版样例）
- §4 渲染层机制速览（雷达/刻度条/分数表；只读，不改）
- §5 双人报告（指向 couple-template.md）
- §6 输出规范（命名 / 声明 / 交付前验证）

## 1. 生成流程

```
1. 收集原始分（5 维度 + 15 子维度，来自平台固定输出：文本表或 JSON）
2. python scripts/compute_scores.py --export <导出.json> --norm cn_college
   → 得到每个条目的 score / z / pct（+ tick）
3. 复制 templates/report-template.html → 目标文件名
4. 整块替换 const REPORT = {...}：
   - meta：alias / date / normId / normLabel / normDetail / domain4Note（+ 扁平剖面时必填 qualityNote）
   - cover：chips×3 + oneliner（1–2 行）
   - domains[5]：数值（来自 step 2）+ line / note(es 域) / facets[].line / behaviors×3
   - strengths / flaws：标题 + 正文 + tags
   - love：h2 / lead / patterns×3 / pitfalls×3 / phrases×3 / partner 三件
   - growth：h2 / lead / cards×3–5
   - faq：×3–5 问
5. python scripts/lint_report.py <目标文件> → 必须 PASS
6. （必要时）浏览器检查（§6.3）→ 交付
```

**禁止**：改 `<style>` 块、改渲染 JS、改章节 id / 锚点 / 固定文案、在 REPORT 里写注释（lint 按 JSON 解析数据块，注释会导致解析失败）。

## 2. REPORT 数据块 schema

```js
const REPORT = {
  meta: {
    alias: "zyh",                       // 代号（不渲染进页面，仅随文件走）
    date: "2026-09-05",                 // 填写日期 YYYY-MM-DD
    normId: "cn_college",               // cn_college | cn_employee | cn_adolescent
    normLabel: "中国大学生样本（N=1194，17–28 岁，Zhang et al. 2022）",
    normDetail: "中国大学生样本 CN-College（N=1194，17–28 岁，470 男 / 724 女；Zhang et al., 2022, Table 1）",
    domain4Note: "第四域按「情绪稳定性」方向呈现（分数越高越平稳），其子维度保持「敏感性」本义方向。",
    qualityNote: ""                     // 仅扁平剖面（全维度 |z|≤0.3）时必填：降权提示，01 章渲染
  },
  cover: {
    chips: ["安静的观察者", "心软的共情者", "绷着一根弦的梦想家"],   // 恰好 3 个白描标签
    oneliner: ["第一行。", "第二行。"]                              // 1–2 个短句，每行一句
  },
  demoPct: 68,                          // 01 章读数示例的游标位置（选一个档位清晰的值）
  domains: [                            // 恰好 5 个，key/顺序/名称/颜色固定
    { key: "es", name: "情绪稳定性", color: "#9A7FB8",
      score: 2.75, z: -0.43, pct: 33,  // 数值全部来自 compute_scores.py
      line: "维度的一句话定调（≤60 字，说人话）",
      note: "小注：…（仅 es 域需要，其余域留空或省略此字段）",
      facets: [
        { name: "焦虑", score: 4.00, z: 0.92, pct: 82, tick: 66.2, line: "一句话白描（15–30 字）" },
        { name: "抑郁", score: 3.50, z: 0.83, pct: 80, tick: 57.2, line: "…" },
        { name: "易变", score: 2.25, z: -0.52, pct: 30, tick: 54.0, line: "…" }
      ],
      behaviors: ["典型表现 1。", "典型表现 2。", "典型表现 3。"]   // 恰好 3 条，以句号结尾
    },
    // ex（#E07A4F）社交/果断/活力 → ag（#7C9B6D）同情/谦恭/信任
    // → co（#5A7CA6）条理/效率/负责 → op（#D9A441）好奇/审美/想象
    // 维度显示顺序固定：es, ex, ag, co, op
  ],
  strengths: [                          // 超能力卡 3–5 张
    { color: "o",                       // 左边线色：e|a|c|es|o（按主题挑相关维度）
      title: "创意共情型选手",           // ≤10 字白描标题
      body: "正文 60–110 字：点出具体子维度与档位 + 组合含义 + 一个落点（适合做什么/像什么场景）",
      tags: ["开放性 · 偏高", "宜人性 · 偏高"] }   // 「名称 · 档位」，档位必须与该条目实际 pct 一致
  ],
  flaws: [                              // 隐形代价卡 3–5 张（无 color 字段）
    { title: "心软，且不敢说不", body: "…", tags: ["宜人性 · 偏高", "果断 · 偏低"] }
  ],
  love: {
    h2: "在亲密关系里，你是怎样的",
    lead: "章引导语（≤80 字）",
    patterns: [                         // 默认模式 恰好 3 条
      { b: "你的爱是做事，不是说甜话。", t: "支撑句（40–90 字，引用具体分数）" } ],
    pitfalls: [                         // 坑 恰好 3 条，句式同上
      { b: "迁就到失联。", t: "…" } ],
    phrases: [                          // 话术卡 恰好 3 张
      { scene: "想说自己的偏好时",
        bad: "「随便，都行，听你的。」", badHint: "（真实偏好被咽了回去）",
        good: "「我更想吃 A，不过 B 我也可以，你定。」", goodHint: "（说一半也好过不说）" } ],
    partnerTitle: "给伴侣的一小段话",
    partner: "”第一人称一段话（100–160 字）…”",   // 保留中文引号对
    partnerCap: "— 截图或长按，转发给 TA —"
  },
  growth: {
    h2: "如果想让日子好过一点",
    lead: "章引导语（≤80 字）",
    cards: [                            // 成长卡 3–5 条
      { title: "1 · 给焦虑设「办公时间」",  // 编号「N · 」开头
        body: "做法（≤90 字，具体到频次/时长/场景）",
        tags: ["对应：焦虑 · 偏高", "原理：…（可选，仅库内原理句）"] }   // 至少一个「对应：<子维度名> · <档位>」
    ]
  },
  faq: [                                // 自定义 FAQ 3–5 问（分数表/数据说明两项由模板固定提供）
    { q: "过段时间再测，分数会一样吗？", a: "回答（≤80 字）" }
  ]
};
```

字段命名、域 key/名称/颜色、子维度名与顺序、各列表的固定数量（3 chips / 3 behaviors / 3+3+3 love / strengths·flaws·growth·faq 各 3–5）由 lint 强制，不得增删改。唯一放宽：**扁平剖面**（全维度 |z|≤0.3 且 `meta.qualityNote` 已填）时 strengths / flaws / growth 降为 2–5，其余不放宽。

## 3. 七章结构与文案要求

结构与新版样例逐块对齐；文案写作规则见 writing-style.md，内容推导素材见 interpretation-library.md。

| # | 章节 | 数据字段 | 写作职责 |
|---|------|---------|---------|
| 封面 | hero：3 标签 + 一句话 + 雷达 | `cover` | 全报告的"一眼是你"：标签取自最突出/最矛盾的维度组合；一句话把最大的张力说透 |
| 01 | 读法（三十秒读懂分数） | `demoPct` + `meta.qualityNote`（扁平剖面时）+ 模板固定文 | 不写人，只教读图：游标条（高亮段随 demoPct 切换）+ 三条原则卡（模板固定） |
| 02 | 五维逐个说人话 | `domains` | 每域：line 定调（不重复分数）→ 3 facets 各一句白描 → 3 behaviors 日常画面 |
| 03 | 优势与盲区 | `strengths`/`flaws` | 每条 = 跨维度/跨子维度组合；正文必须点到具体子维度与档位；tags 挂「名称 · 档位」 |
| 04 | 亲密 | `love` | 泛化句式（不预设恋爱状态，"和在意的人/TA"可用）；patterns/pitfalls 每条以判断句 b 开头；phrases 三场景各 ✗→✓ 一对 |
| 05 | 成长 | `growth` | 每条挂"对应：X 分数"；动作具体到频次 |
| 06 | 答疑与数据 | `faq` + 模板固定 | 常见疑问；分数表与数据说明由模板自动生成 |

内容规则：
- 02 章各域 `line` 若涉及敏感方向（如 es 域换方向解读），在 line 里直接说清（样例句式："这个分数换个方向读更准确…"），并在 es 域 `note` 留方向小注
- 03 章优盲卡与 04/05 章的结论必须能从分数组合推出（组合表在 interpretation-library.md）；**禁止把样例的句子照搬给新来访者**——句式骨架可复用，具体措辞必须随分数变化
- 各章文案中出现的百分位（如"高于约 67% 的人"）必须与实际 pct 一致（lint 会抽查「名称 · 档位」标签；百分位文字由写作者核对，档位词对照 scoring-interpretation.md §2.1 五档表）

## 4. 渲染层机制速览（只读）

- **雷达图**：z 分制，每环 = 1 SD，z=0 虚线五边形 = 人群平均；z 映射半径 `r=R×(0.12+0.88×(clamp(z,−2,2)+2)/4)`（最内环留 0.12R 最小半径，z ≤ −2 的极端值不落圆心，避免多顶点重叠与轮廓自交）；轴序固定 开→外→宜→情稳→尽（高低交错）；顶点色 = 维度色
- **百分位游标条**：五段宽 = 10/25/30/25/10（远低/偏低/中间/偏高/远高真实占比）；游标位置 = pct；当前档浅染维度色
- **子维度条**：填充 = score/5；轨道小刻度 `tick` = 常模均值位置（由 compute 脚本给出，勿手改）；右侧 pct 为人群百分位
- **分数表**：从 domains 自动生成 20 行（5 维 + 15 子维度），无需维护
- **打印**：`@page{margin:0}`（规避浏览器页眉页脚）+ reveal 状态在打印时强制展开 + beforeprint 自动打开 details——FAQ 与分数表完整输出
- **导航/进度条/入场动效**：固定；prefers-reduced-motion 自动降级

## 5. 双人报告

双人（恋人）报告走独立模板与规范：`templates/couple-report-template.html` + `references/couple-template.md`。本文件的 §1 生成流程、§2 REPORT schema、§3 七章结构**仅适用于单人**；双人的结构、契约与语气一律以 `couple-template.md` 为准，本文不复述。

## 6. 输出规范

### 6.1 文件命名与保存
- 单人（新版）：`bfi2_{代号}.html`；双人：`bfi2_{代号A}_{代号B}.html`（规范见 couple-template.md）
- 代号用用户给的写法（zyh、A001，可带 `-`，不用空格和 `_`）；**限 ASCII 字母/数字/连字符**（中文或含空格的代号不被 lint 文件名正则接受，遇到先让用户换一个）；文件名不带日期
- 目标文件已存在 → 停下来问：加 `-v2` 还是覆盖
- 默认保存 `~/Desktop`（本机实际路径见 README「本机专属配置」）

### 6.2 声明（全部由模板固定提供，不手写给）
- 01 章三原则卡 + 常模小注（`normLabel`）
- 求助 callout「什么时候该认真求助」+ 免责（"不构成任何心理诊断"）
- 06 章数据说明（`normDetail` + 量表出处）

### 6.3 交付前验证（强制，不通过则修复后重来）
1. **计算复跑**：`python scripts/compute_scores.py …` 输出与 REPORT 数值一致（lint 会自动复算，报 FAIL 即数值被手改过）
2. **lint**：`python scripts/lint_report.py <报告文件>` → `PASS: all checks passed（新版单人）`
3. **浏览器检查（仅必要时）**：模板/脚本/lint 变更后首次生成、lint 报渲染类 FAIL、或换新环境首次交付时执行——打开报告确认：雷达五顶点与 z 标注位置吻合；游标停在正确档位段内；分数表 20 行齐全；打印预览（Ctrl+P，边距"默认"）无组件断裂、封面单页、FAQ 与分数表展开完整。日常填充数据默认跳过（渲染层由基线回归守护）
4. 基线回归：改动过模板或 lint 后，跑 `python scripts/run_regression.py`（四条基线：`templates/report-template.html`、`examples/bfi2_sample.html`、`templates/couple-report-template.html`、`examples/bfi2_sampleA_sampleB.html`），全 PASS 再出新报告
