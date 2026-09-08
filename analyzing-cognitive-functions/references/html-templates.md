# HTML 输出模板

所有报告 = 来访者直接阅读的终端产品,默认保存到用户桌面 `~/Desktop/MBTI/`。语言规范见 writing-style.md。

> **单人报告 = hero 式新基线**(纸感令牌 + 静态 SVG + 全件表格化)。单人视觉事实源 = `examples/mbti_sample.html`(lint PASS)——改任何视觉规则前,先看样例实际长什么样。
>
> **双人报告**:封面双人雷达 + 00–05 章 + footer,图表**内联 JS 数据驱动**(与单人静态 SVG 不同);规则见 `references/couple-report.md`,组件规范与双人口径 lint 见 §5。双人视觉事实源 = `examples/mbti_sampleA_sampleB.html`(lint 双人口径 PASS);设计记录 `docs/2026-09-07-couple-report-design.md`。

## Contents
- §1 单人报告基础(令牌 / 排版 / 组件类 / 打印样式)
- §2 单人视觉件(雷达 / 柱状图 / 天平图 / 表格件总表 / 场景块等)
- §3 单人报告结构模板(hero + 01–07 章 + footer)
- §4 输出规范与交付前验证
- §5 双人报告(JS 数据驱动)

## 1. 单人报告基础

### 1.1 设计令牌(纸感系,与样例逐字一致)

```css
:root {
  --bg: #F7F5EF; --fg: #262419; --muted: #6E6A60; --border: #DCD6C8; --card: #FFFFFF;
  --accent: #1F5F66; --accent-text: #1B4A50; --soft: #FAFAF6; --hairline: #B9B29F;
  /* 八功能色(常量,不变) */
  --fi: #c0392b; --ni: #8e44ad; --fe: #2980b9; --ti: #16a085;
  --te: #d35400; --ne: #e67e22; --se: #27ae60; --si: #7f8c8d;
  --font-heading: "Noto Serif SC","Source Han Serif SC","Songti SC",SimSun,serif;
  --font-body: "Noto Sans SC","Microsoft YaHei","PingFang SC",sans-serif;
}
```

- 八功能色 = 功能身份,一种功能一种颜色,全书沿用(柱状图、天平圆点、表格首列定性词、代码字色)。
- 功能代码(Fi/Ni/…)可**裸用**于正文(参考式):`<span class="fn" style="color:var(--fi)">Fi</span>`——衬线 600 + 功能色即身份标识;`.fn-code` 灰色括注体系退役。

### 1.2 排版

- `body`:衬线 `16px / line-height 2.0 / color:var(--fg)` + 噪点纹理背景(data URI feTurbulence,16%,与样例同款);`max-width:680px; margin:0 auto; padding:0 20px 80px`;`body p { text-align:justify }`
- **hero 首屏**(`header.hero#hero`):`min-height:86vh` 居中纵排——`.kicker`(黑体 .72em、letter-spacing .42em、大写)→ `h1` 定位句(衬线 700 2.55em,`<em>` 渐变字 accent→ni)→ `.lede`(一句,黑体 .92em muted 居中)→ `.radar-box`(≤380px)→ 图注 → `.scrollhint`(「↓ 往下读」)
- 正文区:`section`(`border-top:1px solid var(--border); margin-top:56px; padding-top:40px`)+ `.sec-num`(衬线 .8em、letter-spacing .3em、muted,格式「01 · OVERVIEW」)→ `h2`(衬线 700 1.62em)→ `h3`(衬线 700 1.15em)
- 字号刻度:小注 .74–.8em / 正文 16 / lead 1.02em / h3 1.15em / h2 1.62em / hero h1 2.55em;行高正文 2.0,表格与卡内 1.75–1.85

### 1.3 组件类总表(关键属性照抄样例 `<style>` 块)

| 类名 | 用途 | CSS 关键属性 |
|------|------|-------------|
| `.kicker` | hero 眉题 | 黑体 .72em;letter-spacing:.42em;text-transform:uppercase;color:var(--muted);padding-left:.42em |
| `.hero h1`(+`em`) | 定位句大标题(从前两位功能生成,规则见 writing-style §10.6) | 衬线 700 2.55em;line-height 1.35;`em{font-style:normal;color:transparent;background:linear-gradient(120deg,var(--accent),var(--ni));-webkit-background-clip:text}` |
| `.lede` | hero 一句话(固定文本,照录) | 黑体 .92em muted;line-height 2.0;居中;max-width 26em |
| `.radar-box` / `.scrollhint` | 雷达容器 / 下滑提示 | radar-box ≤380px 居中,svg width 100%;scrollhint 黑体 .75em muted letter-spacing .2em |
| `.chart-note` | 图注(每图一条) | 黑体 .8em muted;line-height 1.7;text-align:left;max-width 560px |
| `table` 默认 | **平面表格 = 全篇统一件型**(与盲区表同款) | `width:100%;border-collapse:collapse;font-size:.9em`;`th,td{padding:10px 12px;border-bottom:1px solid var(--border);text-align:left;vertical-align:top}`;`th{font-family:var(--font-body);color:var(--muted);font-weight:700;font-size:.78em;letter-spacing:.08em}`——无外框、无竖线、无底色、无圆角 |
| `.lt` | 列表型表格首列限宽 | `.lt th:first-child,.lt td:first-child{width:12em}`(关键词总表/优势表/兼容表/建议表) |
| `.duo-t` | 强端·代价表(每轴一张) | `th{font-size:.88em;letter-spacing:.04em}`(th 内联功能色);`td{width:50%;font-size:.9em;line-height:1.85}` |
| `.pc-t` | 双弱福利·代价表(条件件) | `ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px}`;`li{position:relative;padding-left:20px;font-size:.92em;line-height:1.75}`;`td:first-child li::before{content:"✦";color:var(--accent)}`、`td:last-child li::before{content:"◇";color:var(--hairline)}` |
| `.hl` | 表格内命中高亮 | `background:linear-gradient(180deg,transparent 60%,rgba(31,95,102,.20) 60%);padding:0 .08em` |
| `.beam`(+figcaption) | 天平图容器 | `figure{margin:24px 0 4px}`;svg `width:100%;max-width:640px;display:block;margin:0 auto`;figcaption 黑体 .8em muted 居中(caption 直接画进 svg 时可留空) |
| `.scene` | 场景块(**线型:仅左竖线,无底色**) | `border-left:3px solid var(--accent);padding:6px 0 6px 20px;margin:22px 0`;`b` 黑体 .74em muted letter-spacing .16em 做小标签;`p` 衬线 .98em |
| `.relg` | 亲密关系定义列表 | `display:grid;grid-template-columns:8.5em 1fr;font-size:.94em`;`div{padding:12px;border-bottom:1px solid var(--border)}`;`.k` 黑体 700 .88em muted;`div:nth-child(4n+1),(4n+2)` 斑马纹 `rgba(255,255,255,.6)`;≤640px 单列 |
| `.bound-list` | 07 边界声明列表 | `list-style:none;gap:8px;黑体 .86em muted;line-height 1.9` |
| `.footer`(+#hero 对应) | 页脚 | `border-top:1px solid var(--border);margin-top:64px;padding:26px 0 0;text-align:center`;`.meta-line` 黑体 .74em muted(代号 · 报告日期 · 数据来源);`.disc` 黑体 .8em muted max-width 40em(含临床句) |
| `.fn` / `.muted` / `p.lead` | 彩色代码 / 弱化小字 / 章引言 | `.fn{衬线 600}`;`.muted{color:var(--muted);font-size:.9em}`;`.lead{font-size:1.02em}` |

**卡框禁用清单(出现即 lint FAIL,防回流)**:`.card`、`.grid2`、`.ov-grid`、`.procon`(全件表格化);单人报告同时禁用旧结构件:`chapter-head`、`pull`、`epigraph`、`summary-card`、`fnchart/.fn-*`、`axis-block/.axis-*`、`combo-card`、`type-cards`、`meta-header`、`guide-box`、`toc`、剖面图/类型栈打分表(见 §2.7 废弃清单)。

### 1.4 打印样式(必须有——来访者会打印或导 PDF)

逐字使用(与样例一致):

```css
@page { size: A4; margin: 16mm 15mm; }
@media print {
  body { background: #fff; background-image: none; max-width: none; padding: 0 10mm; }
  .hero { min-height: auto; padding: 20px 0 6px; }
  .scrollhint { display: none; }
  section { margin-top: 40px; padding-top: 28px; }
  .beam, .scene, table, .relg { break-inside: avoid; }
  tr { break-inside: avoid; }
  * { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
}
```

## 2. 单人视觉件(全部内联 SVG/CSS,零 JS 依赖,打印安全)

> **分工纪律**:雷达管形状总览(相对高低)/ 柱状图管精确分数 / 天平图管四条轴与强弱 / 表格件管内容 / scene 管收束。一图一职,互不复读。**零 JS**:图表全部为手写内联 SVG(坐标按下述公式预算),不做滚动动画。

### 2.1 hero 雷达图(SVG)

- `viewBox 0 0 380 380`,圆心 (190,190),R=132;顶点序 `Fi, Ni, Te, Se, Fe, Ne, Ti, Si`;顶点角度 = −90° 起、每 45°
- 半径 = **相对归一化** `0.18 + 0.82 × (分−min)/(max−min)`(不读绝对分);4 层参考环(r = R×25%/50%/75%/100%,八边形折线,无刻度含义)+ 8 根辐条
- 数据多边形:`fill:rgba(31,95,102,.10)`,`stroke:var(--accent)` 1.6px;顶点圆点 r=3.4 功能色;外圈标签 = 代码(衬线 600 14px 功能色,`paint-order:stroke` 3px 纸色描边光晕,标签半径 R+28)
- 图注(必配):「形状只看相对高低:凸出来的是用得最顺的,凹进去的是最费力的;分差小的时候形状接近正八边形,这也是诚实的读数。每个字母是一种做事方式,下一章逐个认识它们。」

### 2.2 第 1 章柱状图(SVG)

- `viewBox 0 0 680 380`;margin L30/R8/T26/B60;网格线 0/20/40/60/80/100(0–100 绝对标尺,20 一格;0 线 #B9B29F,其余 #DCD6C8;刻度字只标 20–100)
- 8 柱按实测分**降序**;柱宽 ≈55.75(gap 28);柱色 = 功能身份色(rx=3);柱顶数值(--fg 11.5px 黑体);柱底代码(衬线 600 13px 功能色,y=346)
- 图注(必配):「柱高 = 实测分(0–100);一种功能一种颜色,后文所有图沿用同一套颜色。」

### 2.3 天平图 ×4(02 章,SVG,每轴一张)

- `viewBox 0 0 640 210`;支点三角 `M320 142 l-13 20 h26 z`(fill #B9B29F)+ 梁(半长 240,stroke var(--accent) 4px 圆头,圆心 (320,120))
- **倾角 = clamp(−4°, +4°, (右分−左分)×0.16°/分)**——**分高的一端更重、往下沉**;两端接近时天平放平(与参考报告「强端翘起」方向相反)
- 两端圆点 r7(功能色)+ 外环 r12(同色,透明度 = 点透明度×0.32,stroke 1.5);**点透明度 = 相对高低** `(分−min)/(max−min)×0.75+0.2`
- 点旁标注两行:①「Ni · 65.5」(衬线 600 功能色 15px,**含精确分**;y = 点 y+32)②轴词一句(黑体 11.5px muted;y = 点 y+50):预见收敛↔体验当下 / 发散可能↔存档与熟路 / 忠于内核↔推进结果 / 回应他人↔自洽建模——**不用昵称层**(评审废弃)
- **caption 四分支(固定文案,按分差自动选用;X 用 `<tspan>` 功能色强调,y=200 居中)**:

| 条件 | 文案 |
|------|------|
| 双弱(两端实测分均列全维后三位) | 「这条轴两头都偏弱——它不是你的主场。」 |
| \|差\| ≥ 12 | 「在这条轴上,更常露面的显然是 X。」 |
| \|差\| ≥ 5 | 「更常露面的是 X。」 |
| \|差\| < 5 | 「两者接近——这条轴没有明显的赢家。」 |

- 02 章引言必须含天平读法句(照录):「每条轴像一架小天平——分高的一端更重,沉在下面;两端接近时,天平放平。」

### 2.4 表格件总表(八张,全 hairline 平面件)

| 表 | 落位 | 列头(照录) | 行数与规则 |
|----|------|-----------|-----------|
| 关键词总表 `.lt` | 01 开头 | 关键词 / 功能 · 分数 · 排名 / 一句话 | 4 行;首列定性词功能色衬线粗体;行序 = 最高 / 第二 / 居中代表 / 最低 |
| 对照总表 | 02 引言后 | 对照 / 你这一条轴的情况 | 4 行;强端在前、弱端侧用 muted 小字 |
| 强端·代价表 `.duo-t` ×4 | 02 每轴天平图后 | 强端:X n / 代价:Y n(表头内联功能色;双弱轴两格均为定性名,如「Si 37.1:档案柜未上锁」;接近轴同样用定性名) | 每轴 1 张,共 4 张 |
| 福利·代价表 `.pc-t` | 02 双弱轴后(**条件件**:两端均列全维后三位才出现) | 双弱带来的好处 / 双弱的代价 | 单行双格,各含 `<ul>`(✦/◇ 项目符);福利列 = 不被该能力绑定的自由,代价列 = 日常多花的力气 |
| 盲区表 | 04 | 盲区 / 真实成本 / 可以怎么做 | 行 = 费力功能(含分数);成本列 = 具体代价;「可以怎么做」列 = 可执行动作(含频次/场景) |
| 兼容表 `.lt` | 05 | 对方类型 / 互补与摩擦 / 解法 | **必配 4 行**:执行型(Te/Si 强)/ 同类(与本人最强两项相同)/ 体验型(Se 强)/ 照顾型(Fe 极强);互补一句、摩擦一句(成本措辞,禁评价词)、解法一句(可执行) |
| 优势表 `.lt` | 03 | 优势 / 适合的场合 | 3–4 行;首列 = 白话标题(功能色) |
| 建议表 `.lt` | 06 | 方向 / 做法 | 4 行;护强 ×2 + 补弱 ×2;「护强项回报 > 补短板」原则句为章引言必备 |

候选类型表(01 章内):`候选 / 栈序 / 命中` 三列,2 行;标题格式「最接近的类型:X 或 Y(仅供参考)」;命中列内用 `.hl` 高亮;栈序用彩色 `.fn` + 箭头。

### 2.5 亲密关系与收束件

- **rel 定义列表 `.relg`**(05 必配):四键 = 你给出的 / 你索取的 / 你的摩擦点 / 关系里的你;每键一段大白话。
- **场景块 `.scene`**(线型):小标签(`b`)取「你是不是也这样 / 写在最后 / 三句值得直接背下来的句式」;每轴一条「你是不是也这样」(第二人称 ≤60 字,落在具体行为,不引入新结论);06 章末「写在最后」= 全篇收束。
- **边界声明 `.bound-list`**(07 照录 writing-style §9.3 参考口径 4 条)+ `h3 附录 · 得分明细` 表(功能 / 得分 / 所属对照 / 这一条轴里更常露面 / 角色(白话近似))。

### 2.6 分工纪律(评审)

雷达管形状总览 / 柱状图管精确分数 / 天平图管四条轴与强弱 / 表格件管内容 / scene 管收束——**一图一职,互不复读**;正文不复述图表读法(语言密度规则见 writing-style §10.1)。

### 2.7 已废弃件清单(勿再生成;出现即 lint FAIL——单人)

速览卡 / 题记 / 三结论卡 / 恋爱一句话 / 目录 toc / 阅读指南框 / chapter-head / chapter-sub / pull 锐评 / 八彩条形图 / 轴对立合并图 / 排位剖面图 / 类型栈打分表 / 组合卡 / 证据标签(ev-tag)/ meta-header 页眉 / 卡框类(.card/.grid2/.ov-grid/.procon)/ 进度条 / 首字下沉。

## 3. 单人报告结构模板(2800–4000 字)

```
hero(#hero)  kicker「Jungian Cognitive Functions · 人格坐标报告」
             + h1 定位句(从前两位功能生成,两句、每句 ≤10 字,em 渐变字;规则 writing-style §10.6)
             + lede 固定句(照录 writing-style §9.2)
             + 雷达图(SVG,§2.1)+ 图注 + 「↓ 往下读」
01 总览(01 · OVERVIEW)      你的总览:四个关键词
             关键词总表(.lt)+ h3 八维得分 + 柱状图(§2.2)+ 图注
             + h3 最接近的类型(候选表,.hl 命中)+ 「别把任何标签当身份证」固定句(§9.4)
02 四条轴(02 · YOUR TRADE-OFFS)
             引言(照录冠名修正句 + 天平读法句)+ 对照总表
             + 取舍一~四,每条轴:h3(Ni 预见 vs Se 体验 式短对)
               → 天平图(§2.3)→ 强端·代价表(.duo-t)
               → [双弱时:福利·代价表 .pc-t] → 「你是不是也这样」场景块
03 优势(03 · STRENGTHS)      h2 你的优势:什么场合最值钱 + 优势表
04 盲区(04 · BLIND SPOTS)    引言(照录 §9.5)+ 盲区表(盲区/真实成本/可以怎么做)
05 亲密关系(05 · INTIMATE RELATIONSHIPS)
             引言(照录:你付出的和你想要的,经常不是同一种东西)
             + rel 定义列表 + h3 兼容地图:没有对错,只有磨合 + 兼容表
             + 「三句值得直接背下来的句式」场景块
06 发展(06 · DEVELOPMENT)    h2 发展建议:先护强项,再帮短板省力
             + 引言(护强项回报 > 补短板原则句)+ 建议表 + 「写在最后」场景块
07 边界(07 · BOUNDARIES)     h2 边界声明:报告是镜子,不是判决书
             + 边界声明 ul(照录 §9.3)+ h3 附录 · 得分明细表
footer       .meta-line(代号 · 报告日期 · 数据来源)+ .disc(参考收束句 + 临床句)
```

结构规则:

- **章节恰 7 个**(sec-num 01–07;hero 不算章),锚点 id = s1–s7 + hero;无目录、无页眉(meta 进 footer)。
- 取舍每条轴内顺序固定:天平图 → 强端·代价表 →(双弱时)福利·代价表 → 场景块;轴序固定:一 = Ni–Se / 二 = Ne–Si / 三 = Fi–Te / 四 = Fe–Ti（与分析轴同一套，见 scoring-algorithm §1.1）。
- **双弱判定** = 两端实测分均列全维后三位;此时天平 caption 用双弱分支,且组内加福利·代价表(无双弱轴则全报告无 .pc-t,正常)。
- caption 四分支、关键定性词(价值驱动/迷雾里认方向 等)措辞见 writing-style;**比喻收缩原则**最高优先(writing-style §4.1)。
- 附录得分明细 = 8 行 × 5 列(功能[彩色代码+学术名] / 得分[两位小数] / 所属对照 / 这一条轴里更常露面 / 角色[白话近似、无原型名])。
- **降级场景**（双人仅一方数据时）：单人报告在 05 章后附一节「从你这方看到的关系模式」（`h3` + 表格/段落承载），**不新增 sec-num**（保持 01–07 恰 7 个）；不推测缺席方。
- 双人报告结构见 §5,不适用本节。

## 4. 输出规范

### 4.1 文件命名与保存
- 单人:`mbti_<用户代号>.html` + `mbti_<用户代号>.json`;双人:`mbti_<代号A>_<代号B>.html` + 两份单人次 JSON;v2 命名 `mbti_<代号>-v2.*`
- 用代号不用真名;**日期不进文件名**,只出现在 footer `.meta-line`
- 保存路径:默认 `~/Desktop/MBTI/`;用户另行指定时从其指定
- 得分 JSON 的 schema 与字段规则见 `input-parsing.md` §4

### 4.2 必须标注的声明
- hero lede 固定句(照录 writing-style §9.2)
- 01 章末「别把任何标签当身份证」固定句(照录 §9.4 / §2.3)
- 07 边界声明(照录 §9.3,4 条)
- footer `.disc` 收尾句(照录 §9.3 尾句,含「不构成临床诊断」)

### 4.3 交付前验证(强制)

1. 运行 lint:`python scripts/lint_report.py <报告文件>`,输出「全部检查通过。」。单人检查项:
   - hero(kicker + h1 定位句 + lede 固定句 + 雷达 svg);柱状图(rect ≥8);天平图 =4;关键词总表 / 对照总表 / 优势表 / 建议表 / 盲区表三列头;候选类型表;rel 四键;兼容表 ≥4 行;duo-t =4;三句句式;07 边界声明;footer 临床句 + meta 行
   - 禁词(writing-style §6,含比喻收缩禁用系);卡框与已废弃件回流 = FAIL;sec-num = 7、锚点 s1–s7、纸纹不打印(print 块去背景图);`@page A4`、噪点、680px、@media print
   - 双人报告走双人口径（§5.3：JS 数据契约 + 四条轴/雷达/四象限挂载 + 边界/伦理/临床句 + 禁旧件回流 + 不判合分承诺），单人结构件自动跳过
2. JSON 校验:得分 JSON 可解析、`scores` 8 键齐全且顺序为 `Ne,Ni,Fe,Fi,Te,Ti,Se,Si`、与报告中的分数一致
3. 浏览器渲染检查:雷达形状与分数相对高低互证、柱状图数值、天平倾角(分高端在下)、caption 分支、表格 hairline、锚点可跳、打印预览(注意浏览器缓存——用带 `?v=时间戳` 的地址强制刷新)无组件断裂、纸纹不打印
4. 基线样例回归:改过 lint 或 CSS 后先跑样例——`python scripts/lint_report.py examples/mbti_sample.html`(必须 PASS)
5. 全部通过才允许交付

## 5. 双人报告（JS 驱动）

结构 = 封面 + 00–05 章 + footer；图表由内联 `<script>` 从 `A`/`B` 两个数据对象自动重算（双人「换数据即生成」的刻意设计，与单人静态 SVG 不同）。完整规则（定位/数据契约/章节/文案/保留固定文本/口径差异）见 **`references/couple-report.md`**；as-built 设计规格存档 `docs/2026-09-07-couple-report-design.md`。

> 视觉事实源 = `examples/mbti_sampleA_sampleB.html`（lint 双人口径 PASS）。旧 01–08 章结构、八维度评分条（.fit-*）、双栏卡（.person-cards）、四阶段/冲突/风险模板、`.pull` 锐评、`.chapter-head`、正文证据标签（ev-tag）**全部废弃**，出现即 FAIL。

### 5.1 组件类与 CSS（新双人，逐字见新样例 `<style>` 块）

- **底**：与单人 §1.1 同一套纸感令牌 + 噪点 + 八功能色常量；`body max-width:720px`（双人比单人宽 40px，容纳四象限/雷达方形画布），`@page A4` + `@media print`（去背景、`break-inside:avoid`、`print-color-adjust:exact`）。
- **共用单人同款件**：`.kicker`/`.hero h1`(+`em` 渐变,双人 2.35em 覆盖单人 2.55em)/`.lede`/`.scrollhint`/`.sec-num`/`h2`/`h3`/`table`(hairline)/`.hl`/`.scene`(左竖线线型)/`.relg`(定义列表)/`.chart-note`/`.bound-list`/`.footer`(`.meta-line`+`.disc`)/`.fn`(彩色代码=身份)。
- **双人专属件**：
  - `.hero-radar`（封面双雷达叠加容器）+ `.cover-legend`（图例：实线= A、虚线= B、凸出= 互补入口）
  - `.quad`（01 四象限矩阵容器）
  - `.beam`（02 四条轴光谱条容器，`figure`+`figcaption`）
  - `.portraits`/`.portrait`（00 速写卡双列网格，`.A`/`.B` 变体；顶角 `.tag`、`.fn-points`、`.desc`、`.mbti-ref`；≤600px 单列）
- **人物编码**：实心 = A、空心/描边 = B；**颜色永远属于功能，不属于人**（旧「颜色 = 人 P1紫/P2绿」废弃，无 `--p1-color`/`--p2-color`）。

### 5.2 图表函数（内联 `<script>`，数据驱动）

四个函数读 `A`/`B` 对象产出 SVG：`renderHeroRadar()`（双人雷达叠加）、`renderQuadrant()`（四象限散点）、`renderBeam(id,L,R,nameL,nameR)`×4（对数比值光谱条，L/R 用轴词对）。规格细节（半径归一化公式、log 比值 offset 与 K=256、OFF 偏移表、实心/空心、渐变带不代表错位量、无刻度数字）见 `couple-report.md` §3。数据契约与换数据改哪里见 §1。

### 5.3 双人口径 lint（新）

- **判定**：页面含 `renderHeroRadar` 或 `renderBeam` 或 kicker 含「双人（恋人）」→ 双人口径；单人结构件自动跳过。
- **结构**：`renderBeam` 挂载恰 4 次（`beam1..beam4`）；`renderHeroRadar()`、`renderQuadrant()` 各挂载 1 次；`id="heroRadar"`、`id="quadrant"` 容器存在；`class="portrait A/B"` = 2；「仅供参考」≥2。
- **数据契约**：`const A={`、`const B={` 均含 8 功能键；`renderBeam(` 四调用的 L/R 为 `Ni–Se、Ne–Si、Fi–Te、Fe–Ti`（轴名用短横；实参为两个独立字符串）。
- **固定文本**（needle 标点无关子串）：lede 固定句、不判合分承诺「关系是做出来的，不是算出来的」、临床句「不构成临床诊断」、边界「不是…判决书」。
- **禁词与回流**：writing-style §6 禁词 + 比喻收缩禁用系；**旧双人件回流 = FAIL**（`fit-fill`/`fit-group`/`person-card`/`chip-row`/`epilogue`/`meter-bar`/`meter-fill`/`highlight-box`/`p1-tag`/`p2-tag`/`--p1-color`）；**旧单人次章件 + 正文证据标签回流 = FAIL**（`chapter-head`/`class="pull"`/`ev-tag`/`fnchart`/`axis-block`/`combo-card`/`type-cards`）；`@page A4`、噪点、`@media print`、body 720px。
- **不判合分**：正文禁「你们合不合」「要不要继续」「匹配度/契合度评分」式判决（writing-style §8 防伤害兜底 + 本条）。
- 基线回归：改 lint/CSS 后先跑 `examples/mbti_sampleA_sampleB.html`（双人）与 `examples/mbti_sample.html`（单人），均须 PASS。
