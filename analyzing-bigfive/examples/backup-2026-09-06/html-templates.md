# HTML 输出模板

所有报告 = 来访者直接阅读的终端产品，默认保存到 **`C:/Users/elliot/Desktop/relations/BFI2/`**。语言规范见 writing-style.md。

## Contents
- §1 CSS 基础体系（变量 / 排版 / 组件类 / 打印样式）
- §2 图表与布局（雷达图 / 仪表条 / 子维度卡片 / 职业倾向参考 / 双人对比图）
- §3 报告结构模板（单人 / 双人）
- §4 输出规范（命名 / 声明 / 交付前验证）

## 1. CSS 基础体系

### 1.1 CSS 变量（颜色方案）
```css
:root {
  --bg: #fafaf8; --text: #1a1a1a; --muted: #5a5a5a; --border: #d0d0cc; --accent: #2c3e50;
  --extraversion: #e67e22; --agreeableness: #27ae60; --conscientiousness: #2980b9;
  --emotional-stability: #c0392b; --openness: #8e44ad;
  --highlight: #f9f3e8; --card-bg: #ffffff;
  --low-bg: #fde8e8; --mid-bg: #f0eeee; --high-bg: #e8f5e9;
}
```
五个维度的颜色分配为常量，不可修改。双人报告新增 --p1-color（紫）和 --p2-color（绿）。

### 1.2 基础排版
- 字体：`"Noto Serif SC","Source Han Serif SC","Songti SC",Georgia,serif`
- 行高：`1.85`；最大宽度：单人 860px，双人 900px
- 响应式：`@media (max-width: 640px)` 双栏降为单栏，目录转块级
- 代码括注样式 `.fn-code`：`font-size:0.75em; color:var(--muted); font-weight:400`（灰色小字）

### 1.3 核心组件类

| 类名 | 用途 | CSS 关键属性 |
|------|------|-------------|
| `.meta-header` | 页眉（日期/编号/量表来源） | `font-size:0.85em; color:var(--muted); border-bottom:1px solid var(--border)` |
| `.guide-box` | 阅读指南 | `background:var(--highlight); border-radius:8px; padding:18px 22px` |
| `.summary-card` | 一页速览卡 | `background:#fff; border:2px solid var(--accent); border-radius:10px; padding:22px 26px` |
| `.ev-tag` | 证据标签基类 | `display:inline-block; font-size:0.72em; padding:2px 8px; border-radius:3px; vertical-align:middle; margin-left:6px` |
| `.ev-research` / `.ev-theory` / `.ev-hypothesis` | ✅绿 / 🔶橙 / ⚪灰 | 背景 #e8f5e9 字 #2e7d32 / 背景 #fff3e0 字 #e65100 / 背景 #f0f0ee 字 #757575 |
| `.toc` | 锚点目录 | `background:#fff; border:1px solid var(--border); border-radius:8px; padding:16px 22px; font-size:0.9em` |
| `.appendix` | 附录区块 | `border-top:2px dashed var(--border); margin-top:48px; padding-top:24px` |
| `.bar-container` / `.bar-track` / `.bar-fill` | 仪表条 | `display:flex; height:22px; border-radius:4px; overflow:hidden` |
| `.callout` | 强调框 | `background:#fff; border:1px solid var(--border); border-radius:8px; box-shadow` |
| `.scene-box` | 场景对话框 | `border:1px solid #e0e0dc; border-radius:6px; padding:16px 20px; margin:12px 0; background:#fff` |
| `.dual-col` | 双栏布局 | `display:grid; grid-template-columns: 1fr 1fr; gap:24px` |
| `.chart-box` | 图表容器 | `background:#fff; border:1px solid var(--border); border-radius:8px; padding:18px; margin:14px 0; text-align:center` |
| `.facet-grid` | 子维度三列网格 | `display:grid; grid-template-columns: repeat(3, 1fr); gap:12px` |
| `.facet-card` | 子维度卡片 | `background:#fff; border:1px solid var(--border); border-radius:6px; padding:12px 14px; border-left:4px solid var(--accent)`（左侧 4px 色条颜色由 inline style 按维度色覆盖，见 §2.3） |
| `.facet-flag` | 子维度"差异大"角标（极差>2 时标注） | `display:inline-block; font-size:0.7em; background:#fff3cd; color:#856404; padding:1px 6px; border-radius:3px; margin-left:4px` |
| `.humility` | 谦卑段落容器（writing-style.md §9.1 固定块） | `background:#fafafa; border-left:3px solid var(--border); padding:12px 16px; margin:16px 0; font-size:0.88em; color:var(--muted)` |
| `.riasec-badge` | 职业倾向参考标签 | `display:inline-block; padding:4px 14px; border-radius:20px; font-weight:700; color:#fff; font-size:0.95em` |
| `.meter-bar` / `.meter-track` / `.meter-fill` | z 分仪表条 | `display:flex; height:16px; .meter-fill 必须 display:block; min-width:4px` |
| `.conflict-header` | 冲突统计标签 | `display:flex; gap:16px; flex-wrap:wrap; font-size:0.9em` |
| `.p1-tag` / `.p2-tag` | 双人报告人物标签 | 紫色/绿色 inline-block 标签 |
| `.fn-code` | 学术名灰色括注 | `font-size:0.75em; color:var(--muted)` |

### 1.4 打印样式（必须有）
```css
@media print {
  body { background:#fff; }
  .summary-card, .callout, .scene-box, .guide-box, .chart-box, .facet-card { break-inside: avoid; }
  .toc { display: none; }
  * { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
}
```

## 2. 图表与布局（全部内联 SVG，无外部依赖，打印安全）

> 图表承载报告的**常模层**（相对所标注常模人群的位置，见 scoring-interpretation.md §4.1）；**自比层**（内部格局与矛盾）由第 2–3 章正文承担。图表必须带锚点标注（同龄人平均 / 极值 / 阅读指引），让位置自解释。

### 2.1 五维度雷达图（速览卡 + 第 1 章）

SVG 雷达图：5 轴从中心向外辐射，轴端标注维度名。来访者位置用多边形连接，填充半透明色。

- `viewBox="0 0 360 330"`，中心 (180,170)，最大半径 120（上/左/右各留 ≥60 单位、下方留 ≥40，防文字裁剪）
- 5 轴角度：从 12 点钟方向顺时针，每隔 72° 一个轴
- z 分 -3 ~ +3 映射到半径 0 ~ 120
- 每个轴端：维度名 + 「z · 超短人话标签」（如"外向性 / -0.92 · 偏安静"）
- 参考线：**只保留一条「同龄人平均」圈（z=0，r=60）**，用加粗虚线（`stroke-width:1.5`）以区别于其他线，并**在圈上/圈旁直接标注「同龄人平均」**；最外圈（r=120）标注「很突出」。**不得画多条未标注的虚线圈**（读者无法分辨哪条是平均）
- **极值标注**：z 最高的轴端加「▲ 最突出」、最低的轴端加「▼ 最靠后」小标注
- 来访者多边形：实色填充（--accent，opacity 0.15）+ 实色描边（--accent）
- **图下必带一行阅读指引**，必须写全坐标约定（"圆心 = 远低于同龄人平均，加粗虚线 = 同龄人平均（z=0），越往外越高；五边形越往外鼓越突出"），避免读者误以为平均应在圆心
- **lint 锚点**：SVG 内保留 `<!-- 维度(z=X.XX): ... -->` 注释（每维度一条，z 与 h3/定位条一致）
- **防文字裁剪**：viewBox 必须为标签留出边距——雷达图用 `viewBox="0 0 360 330"`、中心 (180,170)、半径 120（上/左/右各留 ≥60 单位、下方留 ≥40）；所有轴端文本的 x/y 计算后，必须确认 text-anchor 起点在 viewBox 内且文本行宽不越界（middle 锚点看两端，start 锚点看右端，end 锚点看左端）；图内辅助标注（同龄人平均/很突出/▲▼）放在轴间空区，不与轴端文本重叠。交付前必须用浏览器实际打开检查一遍文字是否完整可见

### 2.2 五维度发散式定位条（第 1 章，必配）

以"同龄人平均"为中心的发散条：中间竖线=同龄人平均（z=0），圆点向左=低于同龄人、向右=高于同龄人。

- 标尺范围 z = -3 ~ +3（与雷达图映射一致，|z|>2 的极端分不会越界），中线在 50% 处；色带 33.3% / 33.3% / 33.4% 对应 z<-1 / -1~+1 / >+1（z=±1 落在 33.3% / 66.7% 处）；marker left% = (z+3)/6×100
- 图上方轴标注**必须带三色块图例**（浅红=明显低于同龄人 z<-1 / 浅灰=与同龄人相近 -1~+1 / 浅绿=明显高于同龄人 z>+1），不得只写文字不标颜色；下方一行阅读指引（"中间竖线=同龄人平均（z=0）；圆点离竖线越远偏得越多；三色带以 ±1 个标准差为界"）
- 圆点（● ±z）落在对应位置；行末给「具体分/平均分 · 人话等级」（如"2.58/5（平均 3.19）· 偏安静"）
- **lint 锚点必须保留**：`.bar-container` 容器、`.bar-label` 内维度名、其后 200 字符内的 `● ±z` 标记（marker 紧跟 label，中间勿插长内容）

HTML 实现示例：
```html
<div class="bar-container">
  <span class="bar-label" style="color:var(--extraversion)">外向性</span>
  <span class="bar-track">
    <span class="bar-zone low" style="width:25%"></span>
    <span class="bar-zone mid" style="width:50%"></span>
    <span class="bar-zone high" style="width:25%"></span>
    <span class="bar-center"></span>
    <span class="bar-marker" style="left:27%">● -0.92</span>
  </span>
  <span class="bar-score">2.58/5（平均 3.19）· 偏安静</span>
</div>
```

### 2.3 子维度卡片网格（第 2 章）

- 用 `.facet-grid` 把 15 个子维度排成三列
- 每张卡片：维度色条（左侧 4px）+ 子维度名 + z 分 + 等级 + 一句话解读
- 同一维度的三个子维度用相同色系
- 矛盾子维度（极差 > 2 的维度下）加一个浅黄色角标"注意：差异大"

### 2.4 职业倾向参考标签（第 4 章）

- 1-3 个倾向标签并排，每个用对应维度的颜色（如"艺术-常规方向"）
- 标签下方：一段文字描述（措辞"可能 / 倾向于 / 参考"，见 applied-analysis.md §1）

### 2.5 双人雷达图重叠（双人第 1 章）

- 与单人雷达图相同结构
- 来访者 A：紫色多边形（--p1-color）
- 来访者 B：绿色多边形（--p2-color）
- 两个多边形重叠区域用混合色（如紫色 + 绿色 = 灰色重叠区）
- 轴端标注双方 z 分（如"外向性 A:-0.92 / B:+0.61"）

### 2.6 双人维度对比条（双人第 2 章）

五条横向双向箭头条：
- 中心 = z=0
- 左端延伸 = 负向 z 分
- 右端延伸 = 正向 z 分
- 双方用不同颜色（紫/绿）
- 每个维度下方标注 Δ 值和相似度标签

## 3. 报告结构模板

### 3.1 单人报告（来访者终端产品，7000-9000 字）

```
页眉 .meta-header：测评日期 · 报告日期 · 量表来源 · 来访者代号 · 所用常模
阅读指南 .guide-box（照录 writing-style.md §固定文本块）
目录 .toc（锚点导航）

0  一页速览卡 .summary-card（职责：三层结论——最突出的两面 / 最靠后的两面 / 最需要注意的一件事 + 探索方向）
   ［雷达图（§2.1 改造版：同龄人平均标注 + 极值标注 + 阅读指引）］
1  你的五维度长什么样（职责：常模层——你相对同龄人的位置，不展开内部格局）
   ［发散式定位条 ×5（§2.2）：轴标注 + 阅读指引 + 具体分/平均分］
   每维度：等级 + 白描 + 至少一个"比如"场景
2  细节：你的子维度画像（职责：自比层核心——15 子维度与内部矛盾）
   ［子维度卡片网格 × 15，每卡至少一个具体场景/实例］
   矛盾模式专门分析（如适用）
3  你独特的人格画像（职责：自比层整合——核心张力，深写）
   五维度交互模式（核心张力/最显著组合）
4  你在工作中可能的样子（职责：应用——引用第 3 章结论往场景落，不重新解释特质）
   ［职业倾向参考标签 + 文字描述］
   场景对话 + 为什么（带证据标签）+ 边界（什么情况下不成立）
5  压力下的你（职责：应用——压力场景）
   脆弱性→触发场景→具体应对 完整链条 + 场景对话 + 为什么 + 边界
6  你与人相处的方式（职责：应用——人际场景）
   人际关系模式（亲密/社交）+ 至少一个冲突场景对话
7  给你的成长建议
   每条 = 现状 + 理解 + 可以试着做（含频次/场景）

附录A 术语表
附录B 这份报告的局限（双层措辞，见 scoring-interpretation.md §4.3）
附录C 你可能想问的
```

### 3.2 双人报告（来访者终端产品，8000-10000 字）

```
页眉 .meta-header（含双方数据来源）
伦理声明 .guide-box（照录 couple-dynamics.md §7）
目录 .toc

1  你们各自的人格快照（双栏卡片 + 雷达图对比）
2  五维度相似度与差异
   ［五条双向对比条］
   相似-吸引效应分析
3  关系中的天然优势（3-5 项）
4  可能的风险点（经验规则：高风险组合，非预测）
5  冲突模式参考 + 最可能触发的话题（含场景对话）
6  关系满意度参考（五维度组合 × 脆弱-应激-适应模型）
7  沟通风格差异（能量方向 + 情绪基调）
8  具体可以怎么做（5 类方法 + 适用条件）
9  结语

附录：这份报告的局限
```

## 4. 输出规范

### 4.1 文件命名与保存
- 单人：`bfi2_{代号}.html`（例：`bfi2_zyh.html`）
- 双人：`bfi2_{代号A}_{代号B}.html`（例：`bfi2_zyh_zyl.html`）
- 代号用用户提供的写法（如 zyh、A001，可带 `-` 如 `zyh-v2`；不用空格和 `_`，`_` 保留作双人代号分隔符），文件名不带日期（文件系统自带时间戳）
- 目标文件已存在（代号重复）→ 问用户：加 `-v2` 后缀，还是同一代号复用（覆盖）
- 用代号不用真名，保护来访者隐私
- 保存路径：**默认 `C:/Users/elliot/Desktop/relations/BFI2/`**；用户另行指定时从其指定

### 4.2 必须标注的声明
- 阅读指南（报告开头，照录 writing-style.md 固定文本块）
- 报告末尾："本报告基于 BFI-2 测评数据的理论分析，不构成临床诊断，不作为任何重大决定的依据。"
- 附录 B：常模来源 + 文化差异提示（照录 scoring-interpretation.md §4.3）
- 双人报告开头：照录伦理声明（couple-dynamics.md §7）

### 4.3 交付前验证（强制）
1. 运行 lint：`python3 scripts/lint_report.py <报告文件>`，全部 PASS
2. 浏览器打开检查：雷达图可见、仪表条渲染正常、速览卡完整、目录锚点可跳转、打印预览无组件断裂
3. 全部通过才允许交付
