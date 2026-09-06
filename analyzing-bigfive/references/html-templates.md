# HTML 输出模板

所有报告 = 来访者直接阅读的终端产品，默认保存到 **`C:/Users/elliot/Desktop/relations/BFI2/`**。语言规范见 writing-style.md。

> 本版为 2026-09-06 视觉重设计后的模板。设计令牌、组件与图表的**唯一视觉事实源** = `examples/bfi2_sample.html`（单人基线样例，lint PASS）；双人新增组件（snap/scard/meters 系）以 SPEC §3.7/§3.8 定稿数值 + §2.6 的追加 CSS 为准。改任何视觉规则之前，先看样例实际长什么样。

## Contents
- §1 CSS 基础体系（设计令牌 / 排版 / 组件类 / 打印样式）
- §2 图表与布局（雷达图 / 定位条 / 子维度卡片 / RIASEC / 双人重叠雷达 / 五维相似度对比表）
- §3 报告结构模板（单人 / 双人 / 组合卡与 verdict 卡）
- §4 输出规范（命名 / 声明 / 交付前验证）

## 1. CSS 基础体系

### 1.1 CSS 变量（设计令牌）

`:root` 逐字使用以下代码块（来源：SPEC §2.1）：

```css
:root {
  --bg: #F7F5EF;            /* 纸色（含 16% 内联 SVG 噪点纹理） */
  --fg: #262419;            /* 正文（墨色） */
  --muted: #6E6A60;         /* 次要文字 */
  --border: #DCD6C8;        /* 边线（暖调） */
  --card: #FFFFFF;          /* 卡片 */
  --accent: #1F5F66;        /* 图形强调（墨青） */
  --accent-text: #1B4A50;   /* 文字强调 */
  /* 定位条轨道 = 连续渐变（见 §3.5），旧式分段轨道变量已废弃 */
  /* 维度色（常量，不变） */
  --extraversion: #e67e22; --agreeableness: #27ae60; --conscientiousness: #2980b9;
  --emotional-stability: #c0392b; --openness: #8e44ad;
  /* 双人人物色（P1 紫 / P2 绿，在灰绿底上按对比度校准） */
  --p1-color: #8E5EA2; --p2-color: #4F9D69;
}
```

- 五个维度的颜色分配为**常量，不可修改**。双人报告人物色：P1 紫 `--p1-color`、P2 绿 `--p2-color`；双人全篇（雷达 / 对比表 / 快照卡 / 人物标签）必须从这两个变量取色，不得另配色值。
- 实现时把 §1.2 的两行字体变量并入同一个 `:root`（样例即如此）。
- 语义色 chip（背景 / 文字，写死，不从变量派生）：

| 用途 | 背景 | 文字 |
|------|------|------|
| 证据标签 ✅ `.ev-research` | #E0EBDD | #3E7257 |
| 证据标签 🔶 `.ev-theory` | #F6ECD9 | #8A5A2B |
| 证据标签 ⚪ `.ev-hypothesis` | #EDEEE8 | #64748B |
| 相似度：高度相似（Δ≤0.5） | #E2EEE6 | #3E7257 |
| 相似度：中度差异（0.5<Δ≤1） | #F6ECD9 | #8A5A2B |
| 相似度：显著差异（1<Δ≤2） | #F7E4E0 | #A6402F |
| 相似度：高度差异（Δ>2） | #F3D9D4 | #8F3D2E |
| 差异最大行 flag / 高亮底 | #F7E4E0 / #FDF7F5 | #A6402F |

- 颜色两条铁律：**颜色 = 人**（双人报告全篇 P1/P2 色令牌同源）；**颜色 = 档位语义**（红 = 差异大 / 低于同龄人，绿 = 相似 / 高于同龄人）。

### 1.2 排版

字体双栈（SPEC §2.2，并入 `:root`）：

```css
--font-heading: "Noto Serif SC","Source Han Serif SC","Songti SC",SimSun,serif;
--font-body: "Noto Sans SC","Microsoft YaHei","PingFang SC",sans-serif;
```

- 标题（h1-h3、章节号）用衬线（`var(--font-heading)`）；1206 A 方向：正文转衬线（行高 2.0、两端对齐），黑体仅用于 UI 小件。`body`：`font-family:var(--font-heading); font-size:16px; line-height:2.0; color:var(--fg); background-color:var(--bg)` + 内联 SVG 噪点纹理（16%，数据 URI，零依赖）；`max-width:680px; margin:0 auto; padding:40px 20px 80px`
- 字号刻度（px）：14 / 16 / 18 / 24 / 32 / 48。正文 16、行高 1.75；小注 14（.78em 级）；小节标题 18（1.12em 级）；章节标题 24（1.5em）；章节号 48（3em）半透明
- **正文列宽 680px**（≈38 汉字/行，符合 65–75 字符行长准则）；定位条、雷达等图表用 `.wide` 破格至 860px；**子维度网格、卡片与正文同宽不破格**（1206：与正文对齐）：`.wide { margin-left:-90px; margin-right:-90px; }`，`@media (max-width:900px)` 时左右 margin 归 0
- 移动端断点 640px：facet-grid、bar-score、.snap 降单列（toc 同步降单列，见 §1.3）
- 间距刻度 4 / 8 / 12 / 16 / 24 / 32 / 48px，章节块间 ≥32px；卡片圆角 10px，大容器（对比表、速览卡）12px，chip 全圆角；卡片 = 白底 + 1px var(--border)，无阴影或极轻阴影（打印安全）
- `.fn-code`：`font-size:0.75em; color:var(--muted); font-weight:400`（学术名灰色小字括注）

### 1.3 组件类总表

关键属性逐条照抄自样例 `<style>` 块（双人组件 snap/scard/meters 系见下方追加块）。

| 类名 | 用途 | CSS 关键属性 |
|------|------|-------------|
| `.chapter-head`（+.num） | 大编号章节头 | `display:flex; align-items:baseline; gap:16px; margin:48px 0 6px`；`border-bottom:3px double #B9B29F; padding-bottom:12px`（双细线）；`.num` 衬线 3.4em/700 墨青 opacity .3；后接 `.chapter-sub`（衬线 .88em） |
| `.chapter-sub` | 章节副题（"这一章回答什么"） | `font-size:.85em; color:var(--muted); margin:0 0 18px` |
| `.prog-bar` | 顶部阅读进度条——**已取消（1206）**，勿再生成；打印块中相关行一并删除 |
| `.pull` | 每章末尾一句话锐评（≤30 字、一行以内）：上下细线 + 大引号 + 衬线 1.15em/700 墨青；由分析层基于本章素材生成——言辞犀利、一针见血、直观形象，不引入新结论，不带证据标签；首字下沉已取消 |
| `.meta-header` | 页眉（代号/日期/量表来源/常模） | `font-size:.78em; color:var(--muted); border-bottom:1px solid var(--border); padding-bottom:12px; margin-bottom:24px` |
| `.guide-box` | 阅读指南 / 双人伦理声明 | `background:#FAFAF6; border:1px solid var(--border); border-left:3px solid var(--accent); border-radius:10px; padding:16px 20px; margin:20px 0; font-size:.92em` |
| `.toc` | 锚点目录 | `background:var(--card); border:1px solid var(--border); border-radius:10px; padding:16px 22px; font-size:.88em; margin:20px 0`；`ol` 两列 grid（`grid-template-columns:1fr 1fr; column-gap:24px; row-gap:2px`），640px 降单列 |
| `.summary-card` | 一页速览卡（第 0 章） | `background:var(--card); border:1.5px solid rgba(8,145,178,.5); border-radius:12px; padding:24px 26px 22px`；内部 `.sum-grid` 单列 grid gap 18px——大雷达在上（无背景框），三条结论卡纵列在下 |
| `.chart-box` / `.chart-note` | 图表容器 / 图下阅读指引 | `.chart-box{ margin:0 auto; text-align:center }`，svg `max-width:100%; height:auto`；`.chart-note{ font-size:.8em; color:var(--muted); margin:10px 0 0; text-align:left; line-height:1.6 }` |
| `.find-card`（+.find-ico） | 速览卡结论卡 ×3 | `background:#FAFAF6; border:1px solid var(--border); border-radius:10px; padding:12px 15px; margin-bottom:10px; display:flex; gap:12px; align-items:flex-start`；`.find-ico` 30×30 圆角 9 白字 .9em/800，底色 inline = 相关维度色；b .88em；p .84em muted line-height 1.65 |
| `.ev-tag`（+.ev-research / +.ev-theory / +.ev-hypothesis） | 证据标签三色 chip | 基类 `display:inline-block; font-size:.72em; padding:2px 9px; border-radius:20px; vertical-align:middle; margin-left:6px; white-space:nowrap`；三色见 §1.1 语义色表 |
| `.fn-code` | 学术名括注 | `font-size:.75em; color:var(--muted); font-weight:400` |
| `.bar-container`（+.bar-label / +.bar-zchip / +.bar-track / +.bar-dash / +.bar-dot / +.bar-score / +.bar-legend / +.zc-low / +.zc-mid / +.zc-high） | 定位条（§2.2） | `.bar-container{ display:flex; align-items:center; gap:10px; margin:12px 0; background:var(--card); border:1px solid var(--border); border-radius:10px; padding:13px 16px }`；`.bar-label` 宽 64px、700、.9em（字色 inline = 维度色）；`.bar-zchip` inline-block .74em/700 圆角 12 padding 1px 9px nowrap——`.zc-low` #F7E4E0/#A6402F、`.zc-mid` #F1F1EA/#5F6B76、`.zc-high` #DFEFE0/#2F7A4D；`.bar-track` flex:1 高 22px 圆角 7 relative，`linear-gradient(90deg,#EBB3A8 0%,#EDECE3 50%,#B2D3A2 100%)`；`.bar-dash` 宽 2px 竖虚线 `repeating-linear-gradient(180deg,#7B828C 0 3px,transparent 3px 7px)`，top/bottom -4px，left 33.3% / 66.7%；`.bar-dot` 14px 圆点 var(--accent) + 3px 白描边 + 投影，`transform:translate(-50%,-50%)`；`.bar-score` 宽 150px .78em muted 右对齐（≤640px 108px / .72em）；`.bar-legend` .72em muted 右对齐 |
| `.dim-block` | 单人第 1 章维度小节 | h3 `font-size:1.12em; margin:30px 0 8px`；h3::before 10px 维度色圆点（`background:var(--dot)`，容器 inline `style="--dot:var(--维度色)"`） |
| `.facet-grid` / `.facet-card`（+.fc-dot / +.fc-lv / +.fc-z） | 子维度三列网格 / 卡片 | grid `repeat(3,1fr)` gap 12px margin 16px 0，≤640px 单列；卡片白底 1px 圆角 10 padding 12px 14px（**无左侧色条**）；`.fc-head` flex baseline gap 7px；`.fc-dot` 8px 圆点 var(--dc)；b .92em；`.fc-lv` .76em muted；`.fc-z` `margin-left:auto` .78em/700 var(--accent-text)；p .82em muted line-height 1.65 margin 6px 0 0 |
| `.facet-flag` | 子维度"差异大"角标（维度内子维度极差 > 2 时标注） | `display:inline-block; font-size:.7em; background:#F6ECD9; color:#8A5A2B; padding:0 6px; border-radius:9px; margin-left:4px; font-weight:600` |
| `.combo-card`（+.combo-head / +.combo-pair / +.combo-side / +.combo-x / +.combo-read） | 组合卡（§3.3） | `background:var(--card); border:1px solid var(--border); border-left:4px solid var(--accent); border-radius:10px; padding:14px 18px; margin:18px 0`；`.combo-head` .8em muted margin-bottom 10px；`.combo-pair` grid `1fr auto 1fr` gap 12px align-items stretch；`.combo-side` `background:#FAFAF6; border-left:3px solid var(--dc); border-radius:8px; padding:10px 13px`（b .92em 色 var(--dc)；span .8em muted）；`.combo-x` 800 var(--accent) 1.15em 垂直居中；`.combo-read` .92em line-height 1.75 margin 12px 0 0 |
| `.lead` | 组合卡后的分段引导语 | `display:block; font-weight:700; color:var(--accent-text); font-size:.9em; margin:20px 0 2px` |
| `.callout` | 关键结论强调框（双人第 6 章等） | 白底 1px 圆角 10 + `border-left:4px solid var(--accent)`，padding 14px 18px，margin 18px 0 |
| `.rel-label` | 第 6 章标签式结构引导词（亲密关系 / 普通社交 / 场景） | `display:inline-block; font-weight:700; font-size:.82em; color:var(--accent-text); letter-spacing:.08em; margin:18px 0 2px`；::before 3px×12px var(--accent) 圆角竖条 margin-right 7px |
| `.scene-box` | 场景卡 | 白底 1px 圆角 10，`padding:12px 16px 13px; margin:10px 0 16px`；内部 `.rel-label{ margin:0 0 4px }`；p .95em margin 2px 0 0 |
| `.advice-card`（+.ac-num） | 编号条目卡（优势 / 建议 / 方法） | `display:flex; gap:14px; background:var(--card); border:1px solid var(--border); border-radius:10px; padding:13px 16px; margin:10px 0`；`.ac-num` 30px 圆形 var(--accent) 白字 .88em/800；p .92em line-height 1.7 margin 0 |
| `.caution-row` | 风险 / 留意条目 | 白卡 1px + `border-left:3px solid #D97706`（琥珀），圆角 8，padding 12px 16px，margin 10px 0，.92em/1.7；`b:first-child{ color:#8A5A2B }` |
| `.appendix`（+.term-list / +.appb / +.ev-stat） | 附录区块 | `border-top:2px dashed var(--border); margin-top:52px; padding-top:26px`；h2 衬线 1.3em；`.term-list li` / `.appb p` .95em；`.ev-stat` .85em muted |
| `.faq-card` | 附录C 每问一卡 | 白底 1px 圆角 10 padding 14px 18px margin 12px 0；`b.q` block var(--accent-text) margin-bottom 4px；`p.a` .94em margin 0 |
| `.riasec-badge` | RIASEC 职业倾向标签 | `display:inline-block; padding:4px 14px; border-radius:20px; font-weight:700; color:#fff; font-size:.95em; margin:0 4px`（底色 inline = 维度色） |
| `.snap` / `.scard` / `.srow` | 双人第 1 章人格快照双卡 | CSS 见下方"双人追加块"；`.scard` 容器 inline `style="--pc:var(--p1-color)"` 或 `var(--p2-color)` |
| `.meters-table` / `.mt-row` / `.meter` | 双人第 2 章五维相似度对比表（§2.6） | CSS 见下方"双人追加块" |
| `.p1-tag` / `.p2-tag` | 双人人物标签（lint 必查两者并存） | `display:inline-block; font-weight:700`，颜色 inline `var(--p1-color)` / `var(--p2-color)` |

兼容性：`meter-fill` 是旧版仪表条的填充类，新模板不再使用；如使用 `meter-fill` 必须带 `display:block` 与 `min-width`（lint 向后兼容检查，缺一即 FAIL）。

双人追加块（单人样例 `<style>` 中没有；双人报告在复制单人 `<style>` 后整段追加）：

```css
.snap { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 640px) { .snap { grid-template-columns: 1fr; } }
.scard { background: var(--card); border: 1px solid var(--border); border-top: 3px solid var(--pc);
  border-radius: 10px; padding: 14px 16px; }
.scard h4 { display: flex; align-items: center; gap: 7px; margin: 0 0 6px; font-size: .95em; color: var(--pc); }
.scard h4 i { width: 8px; height: 8px; border-radius: 50%; background: var(--pc); }
.srow { display: grid; grid-template-columns: 64px 56px 1fr; gap: 8px; align-items: baseline;
  padding: 7px 0; border-top: 1px dashed var(--border); font-size: .85em; }
.scard h4 + .srow { border-top: none; }
.srow b { font-weight: 700; }
.srow .lv { color: var(--accent-text); font-weight: 600; }
.srow span:last-child { color: var(--muted); }
.p1-tag, .p2-tag { display: inline-block; font-weight: 700; }
.meters-table { background: #fff; border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
.mt-row { display: grid; grid-template-columns: 108px 1fr 1fr 112px; align-items: center;
  padding: 15px 18px; border-top: 1px solid #EFEFE9; gap: 8px; }
.mt-row.head { border-top: none; background: #FAFAF6; border-bottom: 1px solid #EFEFE9; }
.meter { display: inline-flex; gap: 4px; }
.meter i { width: 16px; height: 16px; border-radius: 4px; background: #E9E9E2; }
.meter .p { background: var(--p1-color); }
.meter .g { background: var(--p2-color); }
```

（`.srow` 首列 64px 为 SPEC 定稿值；若"情绪稳定性"五字换行，可放宽至 72px，其余不动。）

### 1.4 打印样式（必须有）

逐字照抄样例 `@media print` 块（必须含 `@page { size: A4; margin: 16mm 15mm; }` 与 `body { background-image: none; }`——A4 可打印、纸纹不打印）：

```css
@media print {
  body { background: #fff; max-width: none; padding: 0 10mm; }
  .wide { margin-left: 0; margin-right: 0; }
  .summary-card, .callout, .guide-box, .chart-box, .facet-card, .humility,
  .advice-card, .caution-row, .faq-card, .find-card { break-inside: avoid; }
  .toc { display: none; }
  * { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
}
```

双人报告在此基础上把 `.cmp-row`、`.scard` 一并加进 break-inside avoid 列表（SPEC §3.10）。

## 2. 图表与布局（全部内联 SVG，无外部依赖，打印安全）


### 2.1 五维度雷达图（单人速览卡内 / 双人第 1 章）

SVG 雷达图，5 轴从中心向外辐射，多边形连接五个顶点，顶点带彩色数据点。单人报告的雷达**只出现在速览卡内**（第 1 章只有定位条，不重复画雷达）；双人报告的雷达在第 1 章（§2.5）。

- **几何（固定值，不得改动）**：`viewBox="0 0 300 280"`，中心 (150,150)；r_max=100（z=+3），映射 **r=(z+3)/6×100**；同龄人平均圈 r=50；外圈 r=100。渲染宽 `width="380"`，雷达本身**无背景框**（速览卡大雷达直接裸放）
- **轴线端点（已算好，直接用）**：上 (150,50)、右上 (245,119)、右下 (209,231)、左下 (91,231)、左上 (55,119)；**轴序固定**：外向性(上) → 宜人性(右上) → 尽责性(右下) → 情绪稳定性(左下) → 开放性(左上)；顶点坐标 = 中心 + (轴端点 − 中心) × r/100
- 平均圈：`stroke="var(--accent)" stroke-width="1.4" stroke-dasharray="4,3" opacity=".55"`，圈上方标注「同龄人平均」（9.5px muted）；外圈 #E4E4DC 1.2、5 条轴线 #E4E4DC 1px
- **每维度先写注释再画点**：`<!-- 外向性(z=+0.97): r=66.2, 顶点(150.0,83.8) -->`——五个维度各一条，注释格式与 z 值**不可变**（lint 锚点；z 必须与正文 h3、定位条 chip 一致）。手算坐标前先逐维度写注释，写完再画 polygon/圆点，交付前浏览器放大核对图形与数字互证
- 数据多边形：单人 = `fill="rgba(31,95,102,0.16)" stroke="var(--accent)" stroke-width="2"`；双人 = 两个多边形（§2.5）
- **数据点**：每顶点 `r="4.5"` 圆点 + 1.5px 白描边；填充色单人 = 维度色、双人 = 人物色
- **轴端三连 text，顺序不可变（lint 锚点）**：① 维度名（11.5px、必须带 `font-weight="700"`、fill #1E293B）→ ② z 值（10px muted；**必须是紧跟维度名 text 的下一个 text**）→ ③ ▲/▼（9.5px；「▲ 最突出」fill #3E7257、「▼ 最靠后」fill #64748B，只出现在极值轴端）。顶部轴 z 行在名字上方，其余轴在名字下方，行距 12px
- **阅读指引跟图走**：雷达画在哪个容器里，指引就写在那个容器里图的正下方（`.chart-note`）。单人速览卡 `.chart-note` 固定文案：「圆心 = 远低于同龄人平均；加粗虚线圈 = 同龄人平均（z=0），越往外越高；五边形越往外鼓，该维度越突出。轴端的 ▲ / ▼ 标出你最突出和最靠后的维度。」第 1 章只写定位条自己的引导，**不得残留雷达描述**
- **防文字裁剪**：轴端 text-anchor 起点须在 viewBox 内（顶部 middle、右侧 start、左侧 end；middle 锚点看两端，start 看右端，end 看左端）；交付前必须用浏览器实际打开检查文字完整可见

骨架（可直接复制后替换数值，数值即样例基线）：

```html
<svg viewBox="0 0 300 280" width="380" role="img" aria-label="五维度雷达图">
  <circle cx="150" cy="150" r="50" fill="none" stroke="var(--accent)" stroke-width="1.4" stroke-dasharray="4,3" opacity=".55"/>
  <circle cx="150" cy="150" r="100" fill="none" stroke="#E4E4DC" stroke-width="1.2"/>
  <text x="150" y="93" text-anchor="middle" font-size="9.5" fill="#64748B">同龄人平均</text>
  <line x1="150" y1="150" x2="150" y2="50" stroke="#E4E4DC" stroke-width="1"/>
  <!-- 另 4 条轴线端点：(245,119) (209,231) (91,231) (55,119) -->
  <!-- 外向性(z=+0.97): r=66.2, 顶点(150.0,83.8) -->
  <!-- 宜人性(z=-1.04): r=32.7, 顶点(181.1,139.9) -->
  <!-- 尽责性(z=+1.66): r=77.7, 顶点(195.7,212.9) -->
  <!-- 情绪稳定性(z=+0.39): r=56.5, 顶点(116.8,195.7) -->
  <!-- 开放性(z=-0.75): r=37.5, 顶点(114.3,138.4) -->
  <polygon points="150,83.8 181.1,139.9 195.7,212.9 116.8,195.7 114.3,138.4"
           fill="rgba(31,95,102,0.16)" stroke="var(--accent)" stroke-width="2"/>
  <circle cx="150" cy="83.8" r="4.5" fill="#e67e22" stroke="#fff" stroke-width="1.5"/>
  <!-- 另 4 个顶点圆点，填充色各用所属维度色 -->
  <text x="150" y="36" text-anchor="middle" font-size="11.5" font-weight="700" fill="#1E293B">外向性</text>
  <text x="150" y="24" text-anchor="middle" font-size="10" fill="#64748B">+0.97</text>
  <!-- 极值轴端在 z 行之后再放第三行：▲ 最突出（#3E7257）/ ▼ 最靠后（#64748B） -->
</svg>
<p class="chart-note">圆心 = 远低于同龄人平均；加粗虚线圈 = 同龄人平均（z=0），越往外越高；五边形越往外鼓，该维度越突出。轴端的 ▲ / ▼ 标出你最突出和最靠后的维度。</p>
```

### 2.2 五维度定位条（单人第 1 章，必配）

以"同龄人平均"为口径的发散条：**轨道是一条连续渐变色带**，圆点落在带上。

- 轨道：`linear-gradient(90deg, #EBB3A8 0%, #EDECE3 50%, #B2D3A2 100%)`——越左越红 = 越低于同龄人、越右越绿 = 越高于同龄人；**渐变中点 = z=0，不画中线**
- ±1 个标准差处画**竖虚线**（`.bar-dash`，left 33.3% / 66.7%），分出"低 / 相近 / 更高"三段
- 圆点 14px var(--accent) + 3px 白描边 + 投影；`left% = (z+3)/6×100`（如 +0.97 → 66.2%、-1.04 → 32.7%）
- **z 值 chip（`.bar-zchip`，文案 `● ±z`）必须紧跟 `.bar-label` 之后作为兄弟元素**——中间不得插入任何其他标签（lint 锚点：label 后 200 字符内必须出现 `● ±X.XX`）。底色按 z 所在段：z < -1 → `.zc-low`（红底）；-1 ≤ z ≤ +1 → `.zc-mid`（灰底）；z > +1 → `.zc-high`（绿底）
- `.bar-label` 字色 inline = 维度色；行末 `.bar-score`：「原始分/5（平均 X.XX）· 档位」；五条定位条外包一层 `.wide`，末尾放一行 `.bar-legend`
- `.bar-legend` 固定口径：「渐变中点 = 同龄人平均（z=0）：偏红 = 低于 · 偏绿 = 高于；竖虚线 = ±1 个标准差（低 / 相近 / 更高 的分界）；圆点离中点越远偏得越多」；第 1 章定位条上方的引导段落也按此口径写，只讲定位条
- `.bar-container` 自身即一行白卡（白底 + 边线 + 圆角 10），不要再包一层外卡
- **已否方案（1206 评审已否决，不得回退）**：三色块分区、行白卡变体、分格 + 格内标签、中线——最终形态以样例 CSS 为准

HTML 实现示例（数值来自样例）：

```html
<div class="bar-container">
  <span class="bar-label" style="color:var(--extraversion)">外向性</span><span class="bar-zchip zc-mid">● +0.97</span>
  <span class="bar-track">
    <span class="bar-dash" style="left:33.3%"></span>
    <span class="bar-dash" style="left:66.7%"></span>
    <span class="bar-dot" style="left:66.2%"></span>
  </span>
  <span class="bar-score">3.83/5（平均 3.19）· 中等偏高</span>
</div>
```

### 2.3 子维度卡片网格（单人第 2 章）

- 用 `.facet-grid` 把 15 个子维度排成三列（≤640px 单列），外包 `.wide`
- 每张 `.facet-card`：容器 inline `style="--dc:var(--所属维度色)"`；首行 = 8px 维度色圆点 + 子维度名（700）+ 等级（并入名称行，muted `.fc-lv`）+ z 徽章右浮（`.fc-z`，700 accent-text）；次行一句话解读（.82em muted）
- **卡片无左侧色条**（旧版 4px 色条已废，改用名称前圆点）；同一维度的三个子维度共用同一 `--dc`
- 矛盾子维度（所在维度内子维度极差 > 2）名称后加 `.facet-flag`「差异大」角标

### 2.4 RIASEC 职业倾向标签（单人第 4 章）

- 1–3 个 `.riasec-badge` 并排，每个底色 inline = 对应维度色（如"企业型 E"用尽责性色）
- 标签下方一段文字描述，措辞"可能 / 倾向于 / 参考"（applied-analysis.md §1）

### 2.5 双人重叠雷达图（双人第 1 章）

- 骨架与单人雷达图完全相同（几何 / 平均圈 / 轴线端点 / 防裁剪全部照 §2.1；每维度仍写 `<!-- 维度(z=±X.XX): ... -->` 注释）
- 两个数据多边形：A = `fill="rgba(142,94,162,0.16)" stroke="var(--p1-color)" stroke-width="2"`；B = `fill="rgba(79,157,105,0.14)" stroke="var(--p2-color)" stroke-width="2"`（填充各 14–16%）
- 10 个顶点圆点：r=4.5 + 白描边，填充 = 各自人物色——**顶点色即"哪点是谁"**
- 轴端标注：维度名（700）之后一行双人 z 格式 `A -1.02 · B +0.71`（muted）；不再放单人式纯 z 值 text——lint 的单人 z 一致性锚点不适用于双人雷达，z 一致性由快照卡 / 对比表的锚点承担
- 顶点坐标先按 r=(z+3)/6×100 逐维度算好写进注释再画点；双人轴端文字更长，留白要更大，交付前浏览器实检
- **分工**：雷达图管"整体形状像不像"，对比表（§2.6）管"各在哪一档、差多少"——两图不重复画对方的信息

### 2.6 五维相似度对比表（双人第 2 章）

`.meters-table` 替代旧"双向箭头条"。**分工标注：对比表管差多少，雷达管整体形状，两图不重复。**

- 4 列网格 `108px | 1fr | 1fr | 112px`（两翼收窄等宽，中间放大居中）
- 表头 `.mt-row.head`：维度 | ●P1 代号 | ●P2 代号 | 差异（CSS 圆点 + 人物色名字 700 居中；表头灰底 #FAFAF6 + 底线）
- 每行：维度名（.95em/700）| P1 五格条 | P2 五格条 | Δ 值（.9em/800）+ 四档 chip
- **五格条**：5 个 16px 圆角 4px 格子（gap 4px），填充数 = 档位（低=1 … 高=5），填充色 = 人物色（P1 用 `.p`、P2 用 `.g`），空格 #E9E9E2；**不画 Δ 轨道图形**（避免与雷达图重复）——"差多少"由格数差 + Δ 数值承担
- 行序按 **Δ 降序**；**仅当存在 Δ>1 时**，最大 Δ 行加「▲ 差得最远」flag（chip 样式）+ 浅红底 #FDF7F5 + 3px 左边条 #A6402F（`box-shadow:inset 3px 0 0 #A6402F`）
- Δ 阈值标签 = couple-dynamics.md §1.1 四档（高度相似 / 中度差异 / 显著差异 / 高度差异，经验规则 ⚪），chip 配色见 §1.1 语义色表；**不自造标签**
- 行内**不放**档位文字注释（"低 · 偏安静"之类）——档位含义由第 1 章快照卡承担，两章不重复

对比表辅助类（配合 `.meters-table` 使用，随双人追加块一起复制）：

```css
.cname { font-size: .95em; font-weight: 700; }
.flag { display: inline-block; font-size: .7em; background: #F7E4E0; color: #A6402F;
  padding: 0 6px; border-radius: 9px; margin-left: 4px; font-weight: 600; }
.cell { text-align: center; }
.dv { display: flex; flex-direction: column; align-items: center; gap: 3px; }
.dval { font-size: .9em; font-weight: 800; }
.chip { display: inline-block; font-size: .72em; padding: 1px 8px; border-radius: 20px; white-space: nowrap; }
.chip-sim { background: #E2EEE6; color: #3E7257; }  /* 高度相似 */
.chip-mod { background: #F6ECD9; color: #8A5A2B; }  /* 中度差异 */
.chip-sig { background: #F7E4E0; color: #A6402F; }  /* 显著差异 */
.chip-sev { background: #F3D9D4; color: #8F3D2E; }  /* 高度差异 */
```

骨架示例（第一行为 Δ 最大行的高亮写法）：

```html
<div class="meters-table">
  <div class="mt-row head">
    <span>维度</span>
    <span style="text-align:center"><span class="p1-tag" style="color:var(--p1-color)">●</span> 小雅</span>
    <span style="text-align:center"><span class="p2-tag" style="color:var(--p2-color)">●</span> 阿杰</span>
    <span style="text-align:center">差异</span>
  </div>
  <div class="mt-row" style="background:#FDF7F5;box-shadow:inset 3px 0 0 #A6402F;">
    <span class="cname">外向性<span class="flag">▲ 差得最远</span></span>
    <span class="cell"><span class="meter"><i class="p"></i><i></i><i></i><i></i><i></i></span></span>
    <span class="cell"><span class="meter"><i class="g"></i><i class="g"></i><i class="g"></i><i class="g"></i><i></i></span></span>
    <span class="cell dv"><span class="dval"><b>Δ 1.73</b></span><span class="chip chip-sig">显著差异</span></span>
  </div>
  <!-- 其余 4 行按 Δ 降序排列；仅 Δ>1 的最大行加高亮 -->
</div>
```

## 3. 报告结构模板

### 3.1 单人报告（来访者终端产品，7000–9000 字）

```
页眉 .meta-header：报告日期 · 来访者代号 · 所用常模（不写测评日期与量表来源——报告读者用不到，1206 确认）
阅读指南 .guide-box（照录 writing-style.md 固定文本块）
目录 .toc（锚点导航，两列网格）

00 一页速览 .summary-card（id="s0"，内部放一个 .chapter-head：num=00）
   职责：三层结论——最突出的两面 / 最靠后的两面 / 最需要注意的一件事 + 探索方向
   ［大尺寸雷达图（width=380，无背景框）+ .chart-note 阅读指引（跟图走，§2.1）］
   ［三条 .find-card 纵列：编号徽章底色 = 相关维度色］
01 你的五维度长什么样 .chapter-head(num=01) + .chapter-sub
   职责：常模层——你相对同龄人的位置，不展开内部格局
   ［定位条 ×5（§2.2），外包 .wide + .bar-legend］
   每维度一个 .dim-block（共 5 个）：h3 =「维度名 <span class="fn-code">英文名</span>：档位（z = ±X.XX）」+ 证据标签
   （h3 必须以维度名开头、"（z = ±X.XX）"紧跟档位——lint z 一致性锚点）
2  细节：你的子维度画像 .chapter-head(num=02) + .chapter-sub
   职责：自比层核心——15 子维度与内部矛盾
   ［.facet-grid ×15（§2.3），外包 .wide］
   矛盾模式专门分析（如适用）+ .humility（writing-style.md §9.1 固定块照录）
3  你独特的人格画像 .chapter-head(num=03) + .chapter-sub
   职责：自比层整合——核心张力，深写
   ［.combo-card 组合卡（§3.3，全文首先出现处）］
   三个 .lead 分段正文（怎么帮 / 例外 / 团队位置）
4  你在工作中可能的样子 .chapter-head(num=04) + .chapter-sub
   职责：应用——引用第 3 章结论往场景落，不重新解释特质
   ［.riasec-badge ×1–3 + 文字描述（§2.4）］
5  压力下的你 .chapter-head(num=05) + .chapter-sub
   职责：应用——压力场景；脆弱性 → 触发场景 → 具体应对 完整链条
   "已拥有的优势" → .advice-card ×n；"需要留意" → .caution-row ×n
6  你与人相处的方式 .chapter-head(num=06) + .chapter-sub
   职责：应用——人际场景
   .rel-label「亲密关系」/「普通社交」引导；每块先描述段、后 .scene-box 场景卡
   （场景卡带「场景」标签，属推测性质标 ⚪）
7  给你的成长建议 .chapter-head(num=07) + .chapter-sub
   每条 = 现状 + 理解 + 可以试着做（含频次/场景）→ .advice-card ×n

附录A 术语表 .appendix（id="appa" data-ch="附录"）
附录B 这份报告的局限 .appendix（id="appb"；.appb 段 + .ev-stat 证据统计行）
附录C 你可能想问的 .appendix（id="appc"；.faq-card 每问一张）
```

结构规则：

- 单人报告共 **8 个 `.chapter-head`（00–07）**，每章开头 `.chapter-head` + 一句 `.chapter-sub`（"这一章回答什么"）
- 锚点 `id` 固定：s0–s7、appa/appb/appc；**s4 / s5 / s6 / s7 是 lint 必查锚点**，缺一即 FAIL
- 证据统计行先数后写：`grep -c 'class="ev-tag ev-research"'`（另两个同理）的三个数必须与「✅ × N 处 · 🔶 × N 处 · ⚪ × N 处」声明一致（lint 校验）
- 曾提议在第 7 章后新增第 8 章（SPEC §3.12b），已在设计评审中取消——**不得添加任何额外章节**

### 3.2 双人报告（来访者终端产品，8000–10000 字）

```
页眉 .meta-header（双方代号 + 数据来源 / 常模 / 报告日期；不写测评日期与量表来源）
伦理声明 .guide-box（照录 couple-dynamics.md §7 固定块，逐字——
   含"这份报告基于双方的人格测评数据分析"，lint 必查）
目录 .toc

1  你们各自的人格快照 .chapter-head
   ［.snap 快照双卡（.scard ×2，--pc 分别 var(--p1-color)/var(--p2-color)）：
     白描唯一来源 = scoring-interpretation.md §2.2 三桶模板压缩为一句，禁止自由发挥；
     档位唯一来源 = §2.1 分档表（判档前 z 四舍五入两位）；
     子维度矛盾不在快照卡展开（留给各自的单人子维度内容）；禁词规则照常］
   ［重叠雷达图（§2.5）］
2  五维度相似度与差异 .chapter-head
   ［.meters-table 对比表（§2.6）：行序按 Δ 降序；存在 Δ>1 时最大行加"▲ 差得最远"高亮］
   verdict「一眼结论」卡（句式见 §3.4）
   相似-吸引效应分析（600±100 字：Δ≤0.5 的维度 = 默契点、Δ>1 的维度 = 磨合区；
     措辞"可能 / 倾向于"，标 🔶/⚪）
3  关系中的天然优势 .chapter-head → .advice-card ×3–5（从高度相似两维 + 互补点展开）
4  可能的风险点 .chapter-head → .caution-row ×3–4
   （逐条对应一个 Δ>1 维度，couple-dynamics.md §2.1 张力表；措辞"可能"，经验规则）
5  冲突模式参考 .chapter-head → 触发话题 .caution-row ×2–3 + 冲突场景 .scene-box ×2
   （每场标 ⚪；场景必须引用双方具体档位）
6  关系满意度参考 .chapter-head → 正文 400±100 字 + .callout 一句总结
   （couple-dynamics.md §4；效应量排序只作大致参考）
7  沟通风格差异 .chapter-head → 两行对比卡（复用 .mt-row 网格骨架：
   风格维度 | P1 表现 | P2 表现；能量方向 / 情绪基调两行）
8  具体可以怎么做 .chapter-head → .advice-card ×5（每条含适用条件，逐条对应第 4/5 章的风险）
9  结语 → 衬线（var(--font-heading)）居中短段，无编号、不加大标题层级、无标签

附录 这份报告的局限（.appendix + .appb + .ev-stat；单人文本 + 双人措辞）
```

- 全篇用 `.p1-tag` / `.p2-tag` 标注人物（lint 必查两个类并存）
- lint 必查容器清单对双人报告同样生效（§4.3）——注意 §4.3 第 1 条的落位提示

### 3.3 组合卡 `.combo-card`（跨维度结论的通用载体）

照录 SPEC §3.12a：

- 单人第 3 章首先出现；**任何"维度 × 维度组合"类结论都必须用它承载，不允许出现无推导的裸断言**
- `.combo-head`：小字注明"从你的分数组合里读出来" + 🔶/⚪ 证据标签（组合推断至少 🔶，无理论依据的为 ⚪）
- `.combo-pair`：两个 `.combo-side` 并排（左侧 3px 各自维度色），各含 **维度名 + 实际档位 + z 值 + 一句白描**（档位与措辞必须与 scoring-interpretation §2.1/§2.2 一致，不得写"低开放性"这类与档位不符的简称）
- `.combo-read`：大白话解释组合含义，含一个具体典型场景；措辞按证据规范（"看起来 / 倾向于"）
- 单人样例：尽责性（高，+1.66）× 开放性（中等偏低，-0.75）→「计划外变化让你想先回到计划里」
- 配套：`.lead` 引导语（--accent-text 700 .9em）用于组合卡之后的长正文分段（单人第 3 章三段：怎么帮 / 例外 / 团队位置）；组合卡引入的 🔶 计入证据统计

结构示例（摘自样例）：

```html
<div class="combo-card">
  <div class="combo-head">下面这股"劲"是从你的分数组合里读出来的 <span class="ev-tag ev-theory">🔶</span></div>
  <div class="combo-pair">
    <div class="combo-side" style="--dc:var(--conscientiousness)">
      <b>尽责性 · 高</b><span>z = +1.66 · 偏好计划与秩序</span>
    </div>
    <span class="combo-x">×</span>
    <div class="combo-side" style="--dc:var(--openness)">
      <b>开放性 · 中等偏低</b><span>z = -0.75 · 偏好熟悉与实际</span>
    </div>
  </div>
  <p class="combo-read">……大白话解释组合含义，落到一个具体典型场景……</p>
</div>
```

### 3.4 双人第 2 章 verdict「一眼结论」卡句式

照录 SPEC §3.12：白卡 + 左侧 4px var(--accent)（容器样式可复用 `.combo-card` 的底样式，内部只放固定句式三行）：

- 最像：{维度}（双方都{档位}，几乎一样）
- 最不同：{维度}（A {档位} / B {档位}，Δ {值}）
- 整体相似度：{很像 / 中等相似 / 差异较大}（平均 Δ {值}）

整体相似度分档（平均 Δ<0.5 很像 / 0.5–1 中等相似 / >1 差异较大）为经验规则（⚪）；数值全部由 Δ 计算得出；句内措辞按 writing-style 证据规范执行。

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
1. 运行 lint：`python3 scripts/lint_report.py <报告文件>`，输出 `PASS: all checks passed`。
   - 必查容器（单人 / 双人通用）：meta-header（页眉）/ guide-box（阅读指南）/ toc（目录）/ chapter-head（章节头）/ summary-card（速览卡）/ chart-box（图表容器）/ bar-container（仪表条）/ facet-grid（子维度网格）/ riasec-badge（RIASEC 代码标签）/ ev-tag（证据标签）
   - 双人另查：meters-table（五维相似度对比表）/ meter（五格条）/ scard（人格快照卡）、`.p1-tag` 与 `.p2-tag` 并存、伦理声明句在位
   - 其余检查照常生效：禁词表、固定文本块、维度 z 三处一致性（h3 / SVG 注释 / 轴端 text / 定位条 chip）、证据统计数 vs 实际数、文件命名
   - **落位提示**：现版 lint 的必查容器清单对双人报告同样生效，而 §3.2 的双人结构不含速览卡 / 定位条 / 子维度网格 / RIASEC 章节——生成双人报告前先确认 `.summary-card` / `.bar-container` / `.facet-grid` / `.riasec-badge` 四个类的落位口径，避免 lint 误报
2. 基线样例回归：`examples/bfi2_sample.html`（单人）与 `examples/bfi2_sampleA_sampleB.html`（双人样例，建成后）**同样跑 lint**，必须 PASS——改过 lint 或 CSS 后先跑这两条再出新报告：
   ```bash
   python3 scripts/lint_report.py examples/bfi2_sample.html
   python3 scripts/lint_report.py examples/bfi2_sampleA_sampleB.html
   ```
4. 双人报告浏览器核对：快照双卡档位与 scoring-interpretation §2.1 一致；对比表列对齐且行序按 Δ 降序；重叠雷达形状与轴端数字互证（缩得最深的顶点 / 外扩最远的顶点与 Δ 最大维度对得上）；伦理声明在位
5. 全部通过才允许交付
