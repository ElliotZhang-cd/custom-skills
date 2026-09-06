# Spec：analyzing-cognitive-functions 报告视觉与语言改造（A 纸感书卷系对齐）

日期：2026-09-06 · 状态：设计定稿（用户已批准）
参照系（唯一标准，全部已定稿）：
- 视觉事实源：`C:/Users/elliot/.zcode/skills/analyzing-bigfive/examples/bfi2_sample.html`
- 设计系统规范：`analyzing-bigfive/references/html-templates.md`
- 语言规则：`analyzing-bigfive/references/writing-style.md` §10

## 0. 目标与红线

**Goal**：没有心理学基础的读者，直观、形象、生动地理解自己的认知功能报告；语言按 humanizer-zh 去 AI 味（视觉与语言标准以 bigfive 定稿为准，术语按本 skill 白话体系翻译）。

**红线（已否决，不得回退）**：
1. 顶部进度条、谦卑段落、首字下沉：已取消，勿生成
2. 所有内容与正文 680px 同宽（图表经 `.wide` 破格至 860px）；A4 可打印（`@page A4`、纸纹不打印）
3. 拉引文 = 每章一条 ≤22 字（一行以内）锐评：落在具体行为或数据上、敢下判断、禁对仗金句腔；组合卡禁裸断言（必须摆档位+数值+推导）
4. 禁词表、固定文本块（阅读指南/局限声明/类型只是名字/非预测承诺/伦理声明）照旧；"不是A而是B"句式全篇 ≤2 处

**brainstorm 定稿决策（2026-09-06，用户逐项确认）**：
| # | 决策 | 结论 |
|---|------|------|
| D1 | 定位条渐变语义 | **中性双调渐变 × 绝对标尺**（纸灰→墨青表"用量"，无好坏义；0–100 直映射，中点=50 不画中线） |
| D2 | 速览卡图形 | **P2 题记画像**：速览卡无图表，衬线大字一句话画像 + 挂回功能名小字 + 三条结论卡 |
| D3 | 术语深度① | 八功能为骨架，**学术名+白描引用体系照旧**（现状 §2），只补 §10 语言密度与锐评 |
| D4 | 谦卑段落 | **全链路移除**（规则 4 处 + lint 必查项），与 bigfive 1206 对齐 |
| D5 | chapter-key | **取消**一句话结论框，换 chapter-sub 副题 + 章末锐评拉引文 |
| D6 | 双人范围 | **单人为主**：双人报告只继承新 CSS 底（同 style 块自动生效），双人专属组件本轮不重绘 |

**关键原理（mockup 三轮迭代沉淀，防回退）**：
- 刻度图可读性取决于读者是否知道参照点语义，与有无刻度无关。百分制自解释（"用了几成"），故第 1 章定位条成立；本 skill 无常模，唯一参照点是量表中点 50
- 速览卡不放任何量值图：本报告八个裸分数（平坦、名字未教过）无论怎么摆都是抽象名词清单；雷达 = 8 条未教过的轴 × 平坦数据 → 形状无信号。速览卡的"形象"来自**解读**（句子），不来自数据排列
- 平坦剖面（如全距 12 分）下一切量值图（含合计双极条）都接近居中；"基本均衡"是诚实的读数，chart-note 必须写好这种读法，不得暗示"图上没差别 = 图没用"

## 1. CSS 设计令牌与基础（html-templates.md §1 重写依据）

### 1.1 `:root`（逐字使用）

```css
:root {
  --bg: #F7F5EF;            /* 纸色（含 16% 内联 SVG 噪点纹理） */
  --fg: #262419; --muted: #6E6A60; --border: #DCD6C8;
  --card: #FFFFFF; --accent: #1F5F66; --accent-text: #1B4A50;
  /* 八功能色（常量，不变——沿用现有分配） */
  --fi: #c0392b; --ni: #8e44ad; --fe: #2980b9; --ti: #16a085;
  --te: #d35400; --ne: #e67e22; --se: #27ae60; --si: #7f8c8d;
  /* 双人人物色（继承用） */
  --p1-color: #8E5EA2; --p2-color: #4F9D69;
  --font-heading: "Noto Serif SC","Source Han Serif SC","Songti SC",SimSun,serif;
  --font-body: "Noto Sans SC","Microsoft YaHei","PingFang SC",sans-serif;
}
```

- 删除：`--highlight`、`--text`（旧名）、旧 `bar-fill` 系全部样式、chapter-key、进度条相关
- `body`：`font-family:var(--font-heading); font-size:16px; line-height:2.0; color:var(--fg); background-color:var(--bg)` + 内联 SVG 噪点（16%，data URI，与 bigfive 同款）；`max-width:680px; margin:0 auto; padding:40px 20px 80px`；`body p { text-align:justify }`
- **正文列宽 680px**；`.wide { margin-left:-90px; margin-right:-90px }`（≤900px 归 0）用于定位条组；白描卡网格**与正文同宽不破格**
- 语义色 chip 沿用 bigfive 三色证据标签（✅ #E0EBDD/#3E7257、🔶 #F6ECD9/#8A5A2B、⚪ #EDEEE8/#64748B）；本 skill **不引入**红绿档位色（无常模，红绿=评价，违 R4）
- 卡片半透明：主要卡片容器 `background:rgba(255,255,255,.72)`（清单见 §2 末）

### 1.2 打印样式（逐字基线，组件清单按本报告适配）

```css
@page { size: A4; margin: 16mm 15mm; }
@media print {
  body { background:#fff; background-image:none; max-width:none; padding:0 10mm; }
  .wide { margin-left:0; margin-right:0; }
  .summary-card, .callout, .guide-box, .chart-box, .facet-card, .advice-card,
  .caution-row, .faq-card, .find-card, .combo-card, .scene-box { break-inside: avoid; }
  .toc { display:none; }
  * { print-color-adjust:exact; -webkit-print-color-adjust:exact; }
}
```

### 1.3 通用组件类（照抄 bigfive 样例 CSS，类名不变）

`.chapter-head`(+`.num`)、`.chapter-sub`、`.meta-header`、`.guide-box`、`.toc`、`.summary-card`、`.find-card`(+`.find-ico`)、`.ev-tag` 三色、`.fn-code`、`.pull`、`.combo-card` 全家、`.lead`、`.callout`、`.rel-label`、`.scene-box`、`.advice-card`(+`.ac-num`)、`.caution-row`、`.appendix`(+`.term-list`/`.appb`/`.ev-stat`)、`.faq-card`。

适配点：
- `.chapter-head .num` 用两位数 00–09（衬线 3.4em/700 var(--accent) opacity .3）
- `.summary-card` 边框色适配本 skill 强调色：`border:1.5px solid rgba(31,95,102,.5)`
- `.pull` 文案约束 ≤22 字（见 §4.6）；`white-space:nowrap` 保留，≤640px 换行

## 2. 六视觉件去向 + 新件（html-templates.md §2 重写依据）

**分工纪律（写进模板正文，lint 不查但评审查）**：题记管照见（速览卡，无图）；定位条管精确分数位置；白描卡管逐个解释；极性图管轴倾斜；剖面图管班底叙事；栈表管可核对。一图一职，互不复读。

### 2.1 渐变定位条 ×8（第 1 章，替代降序条形图）
- 8 行按分数**降序**；每行：`.bar-label`（功能名，字色 inline=功能色）+ `.bar-zchip`（文案 `● 原始分`，如 `● 56.3`，底色统一中性 `#F1F1EA/#5F6B76`）+ `.bar-track` + `.bar-score`
- 轨道：`linear-gradient(90deg,#EDECE3 0%,#C9D4D1 50%,#1F5F66 100%)`——**中性双调**：左=用得少，右=用得多；**渐变中点 = 量表中点 50，不画中线**
- 圆点 14px var(--accent) + 3px 白描边 + 投影；`left% = 原始分`（0–100 直映射）
- `.bar-score` 行末 = **类别归属**（"感知 · 对外" / "判断 · 对内"），不重复分数、不写排名
- 8 行外包 `.wide`，末尾一行 `.bar-legend`：「渐变中点 = 量表中点（50）：越靠右 = 平时用得越多 · 越靠左 = 用得越少；这项测试里没有"不好的分数"，两端只是用法不同」（措辞可在实现时微调，口径不变）
- 不引入 ±1sd 虚线（无标准差概念）

### 2.2 白描卡 ×8（第 1 章，替代功能速览网格）
- `.fn-grid` 改为 facet-card 式两列网格（≤640px 单列，**同宽不破格**）；顺序 = writing-style §2 白描表教学序（Ni, Fi, Ti, Te, Fe, Ne, Si, Se）
- 每卡：8px 功能色圆点 + 学术名（700 .92em）+ 分数徽章右浮（.78em/700 var(--accent-text)）+ 白描一行（.82em muted，直接复用 §2 白描表）
- 卡片无左侧色条（圆点制）；禁在卡内重复轴结构解释（轴归第 3 章）

### 2.3 三轴极性图（第 3 章，纸感重绘）
- 结构保持：三行（态度轴 / 感知轴 / 判断轴），每行中轴两侧条、长度=合计分线性映射、条内分数、条端两极名、行末读数结论
- 纸感化：轨道底 `#E9E9E2`，填充 var(--accent)（两侧同色，靠端点文字区分）；SVG 或 div 均可，打印安全
- **chart-note 必须含均衡剖面的读法**（如"两条接近等长 = 你在这条轴上两边都顺手，具体偏哪边看读数"）；禁用位置标记滑轨（既有禁令保留）

### 2.4 排位剖面图（第 3 章，纸感重绘）
- 8 条横条按**位置序**（第一→第八）排列，条长 = 该位功能实测分（0–100 绝对标尺）
- 深色 var(--accent) = 意识位 1–4（平时的你）；浅色 #8FA9AD = 阴影位 5–8（阴影里的你）；50 分竖虚线参照
- 异常位行末标注（如第六位全场最高）
- 行首 = "第N位 · 功能名"；chart-note 一行讲清深浅含义与位置来源（"位置来自第 2 章的类型推断"）

### 2.5 依恋象限图（第 6 章，换皮——决策③）
- 结构与规则**全部保留**：`viewBox="0 0 300 260"`、四象限标注、推测位置虚线圆、边界敏感跨象限、恋爱/家人双图
- 换皮 = 纸感令牌：轴与框线 var(--border)/var(--accent)，象限名衬线，虚线圆 var(--accent) + 填充 rgba(31,95,102,.08)
- 该章证据地位不变（整章 ⚪ 导向 + 替代解释规则照旧）

### 2.6 类型栈打分表（附录 A，纸感重绘）
- 结构保留：两候选 × 8 位置，每级色块（功能色，阴影位 opacity .55），右侧实测分 + ✓/≈/✗；纸感边线与衬线表头
- 职责：可核对（打分过程展示）；不与剖面图抢叙事

### 2.7 题记 `.epigraph`（新件，速览卡 hero——D2）
- 结构：无框居中；正文衬线 `1.3em/700 var(--accent-text) line-height:1.9`，可断两行；下方挂名行 `.72em var(--muted)`（"——你的前两位：外倾直觉 · 内倾情感（分数见第 1 章）"）
- 写作规则（进 writing-style §10）：全报告一条；内容**落在前两位功能的组合上**，用已教过的白话概念；禁对仗金句腔、禁"不是A而是B"；≤32 字；挂名行功能名与分数排序一致
- 分工：题记管"一眼照见"；速览卡其余 = 三条 `.find-card`（最顺手 / 最费力 / 注意一件事）+ 恋爱一句话，无图表

### 2.8 半透明卡清单
`summary-card`、`find-card`、`advice-card`、`caution-row`、`faq-card`、`combo-card`、`scene-box` 用 `rgba(255,255,255,.72)`；chart-box 保持白底。

## 3. 报告结构（html-templates.md §3 重写依据）

- 章节 **0–9 与附录 A/B/C 全部保持**（0 速览 / 1 分数+白描 / 2 类型 / 3 荣格理论核心 / 4 优势与成长空间 / 5 性格画像 / 6 亲密关系模式 / 7 可能的成长环境 / 8 成长方向 / 9 具体建议）
- 每章：`.chapter-head`（num 00–09，速览卡的含在 summary-card 内）+ `.chapter-sub`（一句"这一章回答什么"）——**chapter-key 一句话结论框取消**（D5）
- **每章末一条 `.pull` 锐评**（第 1–9 章，共 9 条；速览卡与附录不放）；lint 数量把关
- 核心张力（3.4 节）改用 **combo-card** 承载：两侧 = 两个功能的"排位词 + 原始分 + 白描一句"，`combo-read` 大白话 + 一个典型场景；🔶 或 ⚪；全报告组合卡 ≥1
- 三级速读新定义：**速览卡（题记 + 结论卡）→ 章副题 → 章末锐评**
- `.meta-header` 对齐 bigfive 1206 口径：`报告日期 · 用户代号 · 数据来源`（删测评日期与量表来源——报告读者用不到）
- 附录 A（类型打分对照）/ B（局限声明 + 证据统计）/ C（FAQ）结构不变；`.appendix-tech` 可选阅读豁免区保留
- 字数目标 6000–8500 不变

## 4. 语言规范变更（writing-style.md 修改依据）

### 4.1 谦卑段落全链路移除（D4）
- writing-style §9.1 删除（存档一行注明"已取消（1206/09-06），勿生成"）；§8.2 改为"推测属性由逐条证据标签承担"
- html-templates §4.2 删除"依恋/成长环境章末照录谦卑段落"
- attachment-inference §4.1 删除"来访者报告正文中，依恋章末尾必须照录固定谦卑段落"句
- lint `REQUIRED_BLOCKS` 删除"谦卑段落"项

### 4.2 新增 §10（组合卡、标签式结构与语言密度——对应 bigfive §10，含本 skill 适配）
1. **组合卡**：跨功能组合结论必须用 combo-card——并排给出两个功能的**排位词 + 原始分 + 白描一句**（适配说明：本 skill 无常模无 z，"档位+z 值"落地为"排位词+原始分"），再大白话解释组合含义 + 一个典型场景；措辞"看起来/倾向于"；禁裸断言
2. **排位词一致性**：组合卡与结论卡中的排位词（最顺手/前两位/靠后/最费力）必须与分数排位一致；禁"低/差"式评价词（R4 姊妹条）
3. **第 6 章标签式结构**：亲密关系等用 `.rel-label` 引导，描述在前、场景在后写入 `.scene-box`，场景标 ⚪
4. **语言密度**：组件读法只允许一行说明（chart-note/图例），正文不复述组件用法（禁"下面这张表把…摆在一起"式旁白）；结论卡/组合卡给过的结论，正文只写"意味着什么、怎么做"；一处结论只带一个推测标记，禁止叠加免责；正文段 ≤3 句（场景对白除外）
5. **一结论一画面**：每个抽象结论后跟一个"比如"级日常画面；没有画面改写到有画面为止
6. **锐评式拉引文**（`.pull`，每章一条，第 1–9 章共 9 条）：≤22 字一行以内；落在具体行为或数据上、敢下判断；禁对仗金句腔（"稳处省电弱处耗神"式）、禁"不是A而是B"排比堆叠、禁概括到谁都能套；只用本章素材、不引入新结论、不带证据标签
7. **去 AI 味基线**（humanizer-zh 自查）：禁"这是一个温和的好消息"式概括抒情、禁"愿你……"祝愿腔、禁三段式排比堆叠、"不是A而是B"每段至多一次（全篇 ≤2）、破折号每段至多一个；改完大声读一遍；比喻先自问"读者能一眼解出来吗"，解不出来宁可不用
8. **题记规则**：见 §2.7

### 4.3 既有规则不动
语气总纲、八功能命名表+白描、R1–R8、去 AI 味 §4（4.5 工程禁词表等）、§6 禁词表→替换表、证据三级标签、深度规范（除 4.4 条）、固定文本块（阅读指南/局限声明/类型只是名字）照旧。
- 4.4 深度规范微调：删除"每章一句话结论框"条，替换为"每章 chapter-sub 副题 + 章末 pull 锐评；三级速读 = 速览卡 → 章副题 → 章末锐评"

## 5. 文件改动清单（执行范围）

| 文件 | 改动 |
|------|------|
| `references/html-templates.md` | §1 令牌/组件表/打印块重写；§2 六视觉件+题记规范重写；§3 结构模板重写（含分工纪律）；§4 验证清单更新 |
| `references/writing-style.md` | §5 深度规范 4.4 微调；§8.2/§9.1 谦卑段落处理；新增 §10 |
| `references/attachment-inference.md` | §4.1 删谦卑段落句（1 处） |
| `SKILL.md` | Phase 2 视觉件清单与组件描述同步；Phase 3 lint 检查项描述同步 |
| `scripts/lint_report.py` | 见 §6 |
| `examples/mbti_sample.html` | **新建**基线样例：合成数据（全距明显 >12，覆盖异常位场景）、完整 0–9 章 + 三附录、lint PASS——对齐 bigfive 样例制度，作为唯一视觉事实源 |

不改动：`input-parsing.md`、`scoring-algorithm.md`、`couple-dynamics.md`（双人报告本轮只继承 CSS 底）、文件命名/输出路径/得分 JSON schema、证据标签体系、禁词表。

## 6. lint 升级（scripts/lint_report.py）

- **移除**：REQUIRED_BLOCKS 中"谦卑段落"项
- **新增**：
  1. `@page { size: A4` 存在（打印红线）
  2. 纸纹噪点 data URI（`feTurbulence`）存在，且 `@media print` 内 `background-image:none`
  3. body `max-width:680px`
  4. `.epigraph` 存在（速览卡题记）
  5. `.combo-card` 存在（组合卡 ≥1）
  6. `.chapter-head` 出现 ≥10 次（00–09）；`.pull` 出现 =9 次（单人报告口径）
  7. 定位条容器（`.bar-track`）出现 ≥8 次
- **保留**：裸功能代码、禁词（含统计措辞）、固定文本块（阅读指南/局限声明）、证据标签存在、速览卡、打印块存在、双人专项（非预测承诺/伦理声明）、meter-fill 向后兼容
- **口径**：含 `p1-tag` 的双人报告跳过单人结构计数（chapter-head/pull/epigraph/combo-card 数量检查），避免双人误报——本轮双人只继承 CSS 底
- 样例回归：`python3 scripts/lint_report.py examples/mbti_sample.html` 必须 PASS

## 7. 执行与验收（流程：spec → writing-plans → 子代理执行 → 首秀验收 → 规则回写）

1. **子代理执行**：按 §5 清单分派；规则文件改写与样例生成可并行，lint 升级须与样例联调
2. **首秀验收**：用 `mbti_qqc.json` 真实分数重新生成报告，命名 **`mbti_qqc-v2.html`**（保留旧版对照），保存到 `/c/Users/elliot/Desktop/relations/MBTI/`
3. **验收标准（全过才算完）**：
   - lint PASS（新规则全生效）+ 得分 JSON 与报告分数一致
   - 浏览器渲染：定位条/白描卡/极性图/剖面图/象限图/栈表正常，锚点可跳，打印预览无断裂、纸纹不打印
   - 与 `bfi2_sample.html` / `bfi2_qqc.html` 并排目测：纸感、章节头、卡片、拉引文风格一致
   - 红线抽查：无进度条/谦卑段落/首字下沉；pull 每条 ≤22 字；"不是A而是B"全篇 ≤2；组合卡无裸断言
4. **规则回写** = §5 清单落地本身（规则文件即定稿载体，spec 存档于 `docs/`）
