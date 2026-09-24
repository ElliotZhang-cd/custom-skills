# 设计规范：颜色语义与图形编码

> **真相源**：单人报告的一切视觉以 **`templates/report-template.html`** 为准。本文件是从该模板**逆向提取**的规范（`bfi2_zyl-v2.html` 等已交付报告的静态部分与模板逐字节一致，故同一套规范适用）。
> **维护规则**：改视觉 = 先改模板 → 再同步本文件 → 跑 `scripts/run_regression.py` 四条基线。**反向不成立**（不得只改本文件而模板不动）。
> **范围**：§1–§5、§7–§9 为**单人报告**规范（本次按模板重写）；双人增量见 §6（保留既有条目，待同法重写）。
> 语言规范见 `writing-style.md`；结构与字段见 `html-templates.md`；阈值见 `thresholds.json`。

## Contents
- §1 色板（`:root` 层 + 硬编码层）
- §2 字体与版式
- §3 组件清单与图形编码（单人）
- §4 各章节配色映射（单人）
- §5 响应式 / 动效 / 打印
- §6 双人报告增量
- §7 禁区（Do Not）
- §8 已知实现与语义冲突（必须知情）
- §9 diff 结论：旧 `DESIGN_SPEC.md` → 现行

---

## 1. 色板

**核心原则：颜色只承担语义，绝不承担好坏。** 语义分三层（中性 / 维度 / 人物），互不混用。

### 1.1 纸面与中性层（`templates/report-template.html` `:root`，逐值核实）

| 变量 | Hex | 用途 |
|---|---|---|
| `--paper` | `#FAF7F2` | 屏幕底色（奶油纸面） |
| `--paper2` | `#F2EBE0` | 次级底（`d-note`、`partner` 卡） |
| `--card` | `#FFFDF9` | 卡片底 |
| `--ink` | `#2B2B2B` | 主文字 / chips 描边 / 导航激活点 / 雷达标签 |
| `--soft` | `#5C564C` | 次级文字（`lead`、卡片正文） |
| `--muted` | `#8A8378` | 注释 / 辅助文字 / 刻度标签 |
| `--line` | `#E6DECF` | 分隔线 / 卡片描边 / 雷达非均值网格环 |
| `--tick` | `#C9BFA8` | facet 轨道均值刻度线 / `partner` 虚线框 / `em` 虚线下划线 |
| `--neutral` | `#7A7484` | 无维度的中性强调（**盲区卡左边线**）。⚠️ 仅单人模板定义，见 §8.3 |
| `--seg-bg` | `#F2EFE8` | 百分位带底色 |
| `--seg-border` | `#D3CCBD` | 百分位带描边 |
| `--seg` | `#E6E1D4` | 百分位带分段统一色（**五段同色，不分深浅**） |
| `--amber` | `#C98F2E` | 求助 callout 左边线 |

### 1.2 五维身份色（维度 = 单一语义；单/双模板**值完全一致**）

| 变量 | Hex | 维度 |
|---|---|---|
| `--e` | `#E07A4F` | 外向性（珊瑚橙） |
| `--a` | `#7C9B6D` | 宜人性（暖绿） |
| `--c` | `#5A7CA6` | 尽责性（靛蓝） |
| `--es` | `#9A7FB8` | 情绪稳定性（雾紫） |
| `--o` | `#D9A441` | 开放性（金黄） |

**作用域约定 `--dc`**：维度块（`.domain`）与游标条（`.pct-track`）由 JS 在容器上 `setProperty('--dc', d.color)`，其子元素用 `var(--dc)` 取当前维度色（顶边框、facet 填充、facet 分数、behavior 圆点、游标、活跃段）。**`--dc` 是"当前块所属维度"，不是全局变量。**

### 1.3 人物身份色（仅双人）

见 §6。单人报告不含人物色。

### 1.4 ⚠️ 硬编码色值层（`:root` 之外，未纳入变量）

以下 hex 直接写在规则里，**当前无变量、也无文档**——是维护陷阱，只减不增（§7）：

| Hex | 出现处 | 语义 |
|---|---|---|
| `#EFE7D9` | `.band-chip`、`.band-cell` 底 | 档位小标签底 |
| `#EFE8DA` | `.track` 底 | facet 轨道底 |
| `#F7ECDB` / `#8A6420` / `#6E5A33` | `.callout` 底 / 标题 / 正文 | 琥珀系警示三件套 |
| `#B9B1A4` | 雷达 `z=0` 虚线环、`.p-bad .p-glyph` 底 | 中性灰褐（"平均"与"旧反应"） |
| `#7C9B6D` | `.p-good .p-glyph` 底 | "正确反应"徽标 —— ⚠️ **与 `--a` 同值**，见 §8.1 |
| `#8A8378` | `.b-item::before` 的 `var(--dc,#8A8378)` **回退值** | ⚠️ 与 `--muted` 同值；仅当 `--dc` 未设时生效（正常路径不触发） |
| `#FBF8F1` | `.pt-seg.on` 的 `color-mix` 基色 | 活跃段浅底基 |
| `#DCD3C2` | `.dot` 导航点 | 未激活导航点 |
| `#EBDFC9` | `::selection` | 选中底色 |
| `rgba(43,43,43,.08)` / `rgba(43,43,43,.4)` | 雷达数据轮廓 fill / stroke | 中性墨色轮廓（见 §8.2） |
| `rgba(250,247,242,.88)` | `nav` 背景 | 导航毛玻璃底 |

---

## 2. 字体与版式

| 项 | 值 |
|---|---|
| 正文族 | `'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif` |
| 衬线族 | `'Noto Serif SC','Songti SC','SimSun',serif` —— 用于 `h1`/`h2`/`h4`/`.d-name`/`.big-score`/`.oneliner`/`.f-score`/`.str-card h5`/`.grow-card h5`/`td.num`/`.partner p` |
| 正文 | `16.5px` / `line-height:1.8` |
| `h1` | `clamp(30px,6.4vw,44px)` / `w900` |
| `h2` | `clamp(24px,4.6vw,31px)` / `w900` |
| `h4` | `17px` / `w700` |
| `.big-score` | `36px`（颜色 = 该维度身份色） |
| `.oneliner` | `19px` / `lh 2`（≤480px 降 17px） |
| `.wrap` | `max-width:700px` / `padding:0 22px` |
| `.lead` | `max-width:60ch` |

---

## 3. 组件清单与图形编码（单人）

### 3.1 导航与进度

| 组件 | 编码 |
|---|---|
| `#progress` | 顶部固定 3px 进度条，`linear-gradient(90deg, var(--e),var(--a),var(--c),var(--es),var(--o))` ⚠️ 装饰性用维度色，见 §8.2 |
| `nav` | 固定顶栏，`rgba(250,247,242,.88)` + `blur(8px)`，底边 `--line` |
| `.dot` / `.dot.active` | 8px 圆点，未激活 `#DCD3C2`，激活 `--ink` + `scale(1.25)` |
| `.cur` | 当前章节序（≤520px 隐藏） |

### 3.2 封面

| 组件 | 编码 |
|---|---|
| `.chip` | `--ink` 1.5px 描边胶囊、透明底、**不用维度色** |
| `.oneliner` | 衬线 19px，`--ink` |
| `.radar-box svg` | `width:100%`，`max-width:460px` |
| `.radar-note` | `--muted` 12.5px（图注，含"z 分：0 = 人群平均位置…"固定句） |

### 3.3 雷达图（几何为硬规范，改动必须同步 `html-templates.md` §4 与回归基线）

```
viewBox="0 0 400 336"      cx=200  cy=162  R=104  N=5
RADAR_ORDER = ['op','ex','ag','es','co']     ← 轴序：开→外→宜→情稳→尽
RADAR_R0    = 0.12                            ← 最小半径系数
ang(i)      = (−90 + 72·i)°
ringR(lv)   = R × (0.12 + 0.88 × ((clamp(lv,−2,2) + 2) / 4))
rOf(z)      = ringR(z)
```

| 元素 | 编码 |
|---|---|
| 网格环 | 5 条，`lv ∈ {−2,−1,0,1,2}`；`stroke:--line`；**`lv=0` 环唯一化**：`#B9B1A4` + `stroke-dasharray:4 3`（= 人群平均，语义唯一） |
| 轴线 | 5 条，`stroke: 该维度身份色`，`stroke-width:1.6`，`opacity:0.75` |
| 数据轮廓 | **中性墨色**：`fill:rgba(43,43,43,.08)` + `stroke:rgba(43,43,43,.4)` `stroke-width:1.4` —— ⚠️ **刻意不用维度色**，见 §8.2 |
| 顶点圆点 | `r=4.4`，`fill: 该维度身份色`，`stroke:#FAF7F2`（纸色描边光晕）`stroke-width:1.6` |
| 轴标签（维度名） | 13px，`fill:--ink`，`text-anchor` 随 `cos(ang)` 取 start/middle/end，`dy` 随 `sin(ang)` 上移/下移 |
| 轴标签（z 值） | 13px `w700`，`fill: 该维度身份色`，`fmtZ` 格式（负号用 `−` U+2212，正数带 `+`） |

**约束**：不得画多条未标注虚线圈；`z=0` 是**唯一**参考环，必须有图注解释圆心/虚线/外向含义。

### 3.4 百分位游标条（`.pct-track`）

| 元素 | 编码 |
|---|---|
| `.pt-band` | `display:flex` `gap:2px` `height:16px`，`border:1px --seg-border`，`bg:--seg-bg`，`radius:7px`，`padding:2px` |
| `.pt-seg` | 五段，宽度 = **10/25/30/25/10 %**（真实占比），统一 `--seg` |
| `.pt-seg.on` | 活跃档：`color-mix(in srgb, var(--dc) 42%, #FBF8F1)` + `box-shadow:inset 0 0 0 1.6px var(--dc)` |
| `.pt-marker` | **3px 竖条、无圆点**，`background:--dc`，位置 = `--p`（pct）；`top/bottom:-6px` 外溢 |
| `.pt-labels` | 五档名（远低/偏低/中间/偏高/远高），10.5px `--muted` |
| `.pt-cap` | 维度名 + 分数（`b` 用 `var(--dc,var(--ink))`）+ `z` 值 |

### 3.5 维度块（`.domain`）与 facet 轨道

| 元素 | 编码 |
|---|---|
| `.domain` | 卡片，`border:1px --line`，**`border-top:5px var(--dc)`**，`radius:16px` |
| `.d-eyebrow` | "维度 N / 5"，11.5px `--muted`，字距 .22em |
| `.d-name` | 衬线 22px `w900` |
| `.big-score` | 36px，**内联 `color: 该维度身份色`** |
| `.band-chip` | 档位词，`#EFE7D9` 底 |
| `.d-note` | 仅 `es` 域渲染（方向小注），`--paper2` 底 |
| `.facet .track` | 9px 高，`#EFE8DA` 底，`radius:6px` |
| `.facet .fill` | 宽度 = **`score/5 × 100%`**（⚠️ 是原始分占比，**不是百分位**），`background:--dc` |
| `.facet .tick` | 2px 竖线，`--tick`，位置 = `f.tick`（= **常模均值 M/5×100**，由 compute 给出） |
| `.f-score` | 2 位小数，`--dc` |
| `.pct` | 人群百分位，11.5px `--muted`（≤420px 隐藏） |
| `.f-note` | facet 白描，缩进 `calc(3em + 10px)` |
| `.b-item::before` | 7px 圆点，`var(--dc,#8A8378)` |

### 3.6 优势卡 / 盲区卡

| 元素 | 编码 |
|---|---|
| `.str-card` | 卡片 `--card` / `--line` |
| `.adv` | **`border-left:4px var(--ac, var(--a))`** —— `--ac` 由 `strengths[].color` 指定的**主题维度色** |
| `.flaw` | **`border-left:4px var(--neutral)`** —— 盲区卡固定中性色，**不用维度色**（语义：代价不属于某个维度） |
| `.tags span` | 11.5px，`--line` 描边，`--muted` 字，`--paper` 底 |

### 3.7 话术卡与「给在意的人」

| 元素 | 编码 |
|---|---|
| `.p-bad .p-glyph` | 22px 圆形徽标，底 `#B9B1A4`（中性），文字 `--muted` |
| `.p-good .p-glyph` | 底 `#7C9B6D`（⚠️ 与 `--a` 同值，见 §8.1），白字 |
| `.p-text em` | 括号点评，`border-bottom:1px dashed --tick` |
| `.partner` | `--paper2` 底 + `1.5px dashed --tick` 框，衬线 16.5px `lh 2.1` |
| `.partner-cap` | 12.5px `--muted`，字距 .15em |

### 3.8 成长卡与求助 callout

| 元素 | 编码 |
|---|---|
| `.grow-card` | 卡片；标题衬线 16.5px |
| `.callout` | `#F7ECDB` 底 + `border-left:4px --amber`，标题 `#8A6420`、正文 `#6E5A33` |

### 3.9 答疑与分数表

| 元素 | 编码 |
|---|---|
| `details` | `--card` 底 / `--line` 框；`summary::after` 为 `+`，`[open]` 时为 `–` |
| `table` | 13.5px；`td.num` 衬线 `w700`；facets 行前缀 `└`（`.ind`，`--muted`） |
| 分数数字 | **内联 `color: 该维度身份色`**（大维度行与子维度行同用其所属维度色） |
| `.band-cell` | 档位小标签，`#EFE7D9` 底 |

---

## 4. 各章节配色映射（单人）

| 对象 | 用色 | 依据 |
|---|---|---|
| 顶部进度条 | 五维色渐变（装饰） | §8.2 |
| 封面 chips | `--ink` 描边 | 画像标签≠维度 |
| 封面 oneliner | `--ink`（衬线） | 中性 |
| 雷达：网格环 | `--line`；`z=0` 环 `#B9B1A4` 虚线 | 平均参考唯一化 |
| 雷达：轴线 / 顶点 / z 值 | 该维度身份色 | 维度=色 |
| 雷达：数据轮廓 | **中性墨色** | §8.2 |
| 维度块：顶边框 / 大分数 / facet 填充 / facet 分数 / behavior 圆点 | 该维度身份色（`--dc`） | 维度=色 |
| 游标条：活跃段 / 游标 | 该维度身份色 | 维度=色 |
| 优势卡左边线 | `strengths[].color` 指定的主题维度色 | 卡片有主题维度 |
| 盲区卡左边线 | `--neutral` | 代价不归属单维度 |
| 话术卡 ✗ / ✓ 徽标 | `#B9B1A4` / `#7C9B6D` | 语义"旧反应/新反应" |
| 给在意的人 | `--paper2` + `--tick` 虚线 | 中性暖色 |
| 求助 callout | `--amber` | 警示语义 |
| 正文三级 | `--ink` / `--soft` / `--muted` | 层级 |

---

## 5. 响应式 / 动效 / 打印

**断点**（`max-width`）：`719px`（`.full-only`↔`.mini-only`）、`520px`（`.cur` 隐藏）、`480px`（oneliner→17px）、`420px`（`.pct` 隐藏、`.f-note` 去缩进）。

**动效**：
- `.reveal`：`opacity 0→1` + `translateY(14px→0)`，`.7s ease`；由 `IntersectionObserver`（`threshold:0.12`）加 `.in`
- `.fill`：`width` 过渡 `1s cubic-bezier(.25,.7,.25,1) .15s`
- `.pt-marker`：`left` 过渡 `1s cubic-bezier(.25,.7,.25,1) .25s`
- `prefers-reduced-motion:reduce`：以上全部关闭，且强制终态

**打印**（`@media print`，与旧 `DESIGN_SPEC.md` 一致并已扩展）：
- `*{-webkit-print-color-adjust:exact;print-color-adjust:exact}`（保留全部数据色）
- `body{background:#fff;padding:14mm 15mm}`；`@page{size:A4;margin:0}`（**页边距 0 → 浏览器自带页眉页脚无处渲染，自动消失**）
- `nav,#progress{display:none}`
- `header.hero{padding:6px 0 16px;break-after:page}`（封面独立成页）
- `break-inside:avoid`：`.card,.str-card,.grow-card,.phrase-card,.partner,.callout,details,.facet,.pct-track`、`.lead,.small-print,p,li`、`.domain>div:first-child`
- `break-after:avoid`：`h2,h4,.group-title`
- 动效强制终态：`.reveal{opacity:1!important}`、`.fill{width:var(--w)!important}`、`.pt-marker{left:var(--p)!important}`
- `beforeprint` 事件（JS）展开全部 `<details>` → FAQ 与完整分数表完整输出

---

## 6. 双人报告增量

> 本轮**未**按模板重写，保留既有条目。双人模板 `:root` 缺 `--neutral`（§8.3）。

### 6.1 人物身份色（仅双人）

| 变量 | Hex | 人物 | 线型 |
|---|---|---|---|
| `--pa` | `#1B6B5F` | A | 深青，实线 / 实心点 |
| `--pb` | `#C0531F` | B | 赭棕，虚线 / 空心点 |

> 语义：`颜色 = 是哪个人`。人物色只出现在「谁」的语境（头像、卡片边框、泳道人名、雷达轮廓、A/B 标签），永不用于「是哪个维度」。
> **双重编码**（青/棕 + 实线/虚线、实心/空心）保证黑白打印仍可区分两人。
> ⚠️ 旧 `DESIGN_SPEC.md` 的 `--aA`/`--aB`（A/B 浅底）**从未落地**（双人模板零引用），已废弃，勿复活。

### 6.2 双人专属编码

| 语义 | 图形 |
|---|---|
| 差异桥 | 一根带两个游标；左右卡边框 = 人物色；桥标题 `--dc` = 面子所属维度色 |
| 共鸣 | 同带双游标（人物色） |
| 冲突泳道人名 | 人物色 |
| 场景菜单 A/B 倾向卡 | 人物色左边框 |
| 雷达两个轮廓 | A `--pa` 实线 / B `--pb` 虚线 |

### 6.3 双人专属禁区

- ❌ 给关系打匹配分、用颜色暗示「谁对谁错」
- ❌ 用「男蓝/女粉」等性别化配色区分 A/B
- ❌ 人物色画维度条、维度色画人物

---

## 7. 禁区（Do Not）

- ❌ 红/绿表示输赢、好坏、危险（一律换中性或语义色）
- ❌ 给档位分配不同深浅（五段同色是刻意的：档位靠**分段宽度 + 标签**区分，不靠颜色深浅）
- ❌ 大圆点/粗描边/高饱和填充抢数据（表达靠线型、高亮档、刻度）
- ❌ 透明叠同色让图与纸面融为一体（带底/卡底须深一档并带描边）
- ❌ 画多条未标注的虚线圈（`z=0` 必须是唯一参考环）
- ❌ **在 `:root` 之外新增硬编码色值**（现存 11 处见 §1.4，只减不增；新增色必须进 `:root`）
- ❌ 把雷达数据轮廓改成维度色（当前中性墨色是刻意设计，见 §8.2）
- ❌ 只改本文件不改模板（本文件是模板的**描述**，不是源头）

---

## 8. 已知实现与语义冲突（必须知情）

1. **`#7C9B6D` 一色两义**：既是 `--a`（宜人性身份色），又是话术卡 ✓ 徽标底色。当前无实际冲突（不在同一语境），但**改 `--a` 会连带改掉 ✓ 徽标**——若将来要独立调整，需先把 ✓ 徽标提为变量。
2. **维度色的两处非维度用法**：①顶部进度条五维色渐变（纯装饰）；②雷达数据轮廓**刻意用中性墨色**而非维度色——因为五个不同色的轮廓在低 z 时半径接近、互相覆盖难以辨认，中性轮廓保证任何剖面都清晰。
3. **`--neutral` 只在单人模板 `:root`**：双人模板没有该变量，若双人模板引用 `--neutral` 会 fallback 失败。跨模板复用 token 前须先确认存在。
4. **两模板 token 集不一致**：单人 = 中性层 12 + 维度 5 + amber；双人 = 中性层 11（无 `--neutral`）+ 维度 5 + 人物 2 + amber。
5. **雷达轴序 ≠ 维度块序**：雷达 `['op','ex','ag','es','co']`（高低交错），维度块 `['es','ex','ag','co','op']`。**两处不同是刻意的**，改序要同时改两处并重跑基线。
6. **facet 填充语义易误读**：`.fill` 宽度是 `score/5`（原始分占比），`.pct` 才是人群百分位。轨道上的 `tick` 是**常模均值位置**（M/5×100，如 66.2%），不是 50%。

---

## 9. diff 结论：旧 `BFI2/DESIGN_SPEC.md`（151 行）→ 现行

| 旧 spec 条目 | 处置 | 说明 |
|---|---|---|
| `--aA` / `--aB`（A/B 浅底） | **废弃** | 双人模板零引用，从未落地 |
| §4 各章节配色映射 | **补回（本文件 §4）** | 旧 spec 有、收编时丢失；已按模板校正（旧文说"大分数"用维度色——实为内联 JS 设置，见 §3.5） |
| 五维色来源"Soto & John (2017) 既定配色" | **补回（§1.2 注）** | 出处信息在收编时丢失 |
| "轨道 **50%** 刻度" | **修正** | 实为**常模均值位置** M/5×100（§3.5）——旧 spec 有误 |
| "远高 **> 90%**" | **修正** | 应为 **≥ 90%**（与 `thresholds.json` 一致） |
| 打印规范 6 条 | **保留并扩展** | 新增 `break-after:avoid` 与动效强制终态清单（§5） |
| 禁区 6 条 | **保留并扩展** | 新增 3 条（硬编码色、唯一参考环、模板为源） |
| 字体版式 / 组件清单 / 响应式断点 / 动效 / 硬编码色值 / 语义冲突 | **新增** | 旧 spec 完全未覆盖（§1.4、§2、§3、§5、§8） |

**净结论**：旧 `DESIGN_SPEC.md` 没有"被删掉的有效内容"——唯一未搬入的 `--aA/--aB` 本就未实现；其余差异是它**缺**（版式/组件/响应式/动效）或**错**（50% 刻度、>90%）的部分。故该文件已清理：连同两份同期设计样张一并移入 `C:\Users\elliot\Desktop\BFI2\_archive\`（`DESIGN_SPEC_SUPERSEDED.md`、`bfi2-report-sample_SUPERSEDED.html`、`bfi2-couple-toolbook-sample_SUPERSEDED.html`），保留以备追溯，不再作为规范依据。
