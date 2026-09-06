# HTML 输出模板

所有报告 = 来访者直接阅读的终端产品,默认保存到 `/c/Users/elliot/Desktop/relations/MBTI/`(Git Bash 路径)。语言规范见 writing-style.md。

> **2026-09-07 版**(用户批复落地):**单人报告 = 参考正文 hero 式**(结构完全以 `jung-8-function-report.html` 为准,纸感令牌 + 静态 SVG + 全件表格化)。单人视觉事实源 = `examples/mbti_sample.html`(lint PASS)——改任何视觉规则前,先看样例实际长什么样。
>
> **双人报告本轮冻结**:沿用 2026-09-06 基线(卡框系 CSS 底),结构与组件规范见 §5,双人视觉事实源 = `examples/mbti_sampleA_sampleB.html`;单人规范不适用于双人,双人不迁移(迁移另立项)。设计沿革存档:`docs/2026-09-06-reskin-design.md`、`docs/2026-09-07-reference-content-plan.md`。

## Contents
- §1 单人报告基础(令牌 / 排版 / 组件类 / 打印样式)
- §2 单人视觉件(雷达 / 柱状图 / 天平图 / 表格件总表 / 场景块等)
- §3 单人报告结构模板(hero + 01–07 章 + footer)
- §4 输出规范与交付前验证
- §5 双人报告(2026-09-06 基线,冻结)

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
| `.hero h1`(+`em`) | 定位句大标题(从前两位功能生成,规则见 writing-style §10.8) | 衬线 700 2.55em;line-height 1.35;`em{font-style:normal;color:transparent;background:linear-gradient(120deg,var(--accent),var(--ni));-webkit-background-clip:text}` |
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
| `.footer`(+#hero 对应) | 页脚 | `border-top:1px solid var(--border);margin-top:64px;padding:26px 0 0;text-align:center`;`.meta-line` 黑体 .74em muted(报告日期 · 用户代号 · 数据来源);`.disc` 黑体 .8em muted max-width 40em(含临床句) |
| `.fn` / `.muted` / `p.lead` | 彩色代码 / 弱化小字 / 章引言 | `.fn{衬线 600}`;`.muted{color:var(--muted);font-size:.9em}`;`.lead{font-size:1.02em}` |

**卡框禁用清单(出现即 lint FAIL,防回流)**:`.card`、`.grid2`、`.ov-grid`、`.procon`(2026-09-07 全件表格化);单人报告同时禁用旧结构件:`chapter-head`、`pull`、`epigraph`、`summary-card`、`fnchart/.fn-*`、`axis-block/.axis-*`、`combo-card`、`type-cards`、`meta-header`、`guide-box`、`toc`、剖面图/依恋象限图/类型栈打分表(见 §2.7 废弃清单)。

### 1.3 打印样式(必须有——来访者会打印或导 PDF)

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

> **分工纪律**:雷达管形状总览(相对高低)/ 柱状图管精确分数 / 天平图管四组对照与强弱 / 表格件管内容 / scene 管收束。一图一职,互不复读。**零 JS**:图表全部为手写内联 SVG(坐标按下述公式预算),不做滚动动画。

### 2.1 hero 雷达图(SVG)

- `viewBox 0 0 380 380`,圆心 (190,190),R=132;顶点序 `Fi, Ni, Te, Se, Fe, Ne, Ti, Si`——对角(1-5/2-6/3-7/4-8)恰为四组同能力对照:Fi–Fe、Ni–Ne、Te–Ti、Se–Si;顶点角度 = −90° 起、每 45°
- 半径 = **相对归一化** `0.18 + 0.82 × (分−min)/(max−min)`(不读绝对分);4 层参考环(r = R×25%/50%/75%/100%,八边形折线,无刻度含义)+ 8 根辐条
- 数据多边形:`fill:rgba(31,95,102,.10)`,`stroke:var(--accent)` 1.6px;顶点圆点 r=3.4 功能色;外圈标签 = 代码(衬线 600 14px 功能色,`paint-order:stroke` 3px 纸色描边光晕,标签半径 R+28)
- 图注(必配):「形状只看相对高低:凸出来的是用得最顺的,凹进去的是最费力的;分差小的时候形状接近正八边形,这也是诚实的读数。每个字母是一种心理功能,下一章逐个认识它们。」

### 2.2 第 1 章柱状图(SVG)

- `viewBox 0 0 680 380`;margin L30/R8/T26/B60;网格线 0/20/40/60/80/100(0–100 绝对标尺,20 一格;0 线 #B9B29F,其余 #DCD6C8;刻度字只标 20–100)
- 8 柱按实测分**降序**;柱宽 ≈55.75(gap 28);柱色 = 功能身份色(rx=3);柱顶数值(--fg 11.5px 黑体);柱底代码(衬线 600 13px 功能色,y=346)
- 图注(必配):「柱高 = 实测分(0–100);一种功能一种颜色,后文所有图沿用同一套颜色。」

### 2.3 天平图 ×4(02 章,SVG,每轴一张)

- `viewBox 0 0 640 210`;支点三角 `M320 142 l-13 20 h26 z`(fill #B9B29F)+ 梁(半长 240,stroke var(--accent) 4px 圆头,圆心 (320,120))
- **倾角 = clamp(−4°, +4°, (右分−左分)×0.16°/分)**——**分高的一端更重、往下沉**;两端接近时天平放平(2026-09-07 用户批示:与参考报告「强端翘起」方向相反)
- 两端圆点 r7(功能色)+ 外环 r12(同色,透明度 = 点透明度×0.32,stroke 1.5);**点透明度 = 相对高低** `(分−min)/(max−min)×0.75+0.2`
- 点旁标注两行:①「Ni · 65.5」(衬线 600 功能色 15px,**含精确分**;y = 点 y+32)②轴词一句(黑体 11.5px muted;y = 点 y+50):发散可能↔预见收敛 / 体验当下↔存档与熟路 / 忠于内核↔推进结果 / 回应他人↔自洽建模——**不用昵称层**(2026-09-07 评审废弃)
- **caption 四分支(固定文案,按分差自动选用;X 用 `<tspan>` 功能色强调,y=196 居中)**:

| 条件 | 文案 |
|------|------|
| 双弱(两端实测分均列全维后三位) | 「这组两头都偏弱——它不是你的主场。」 |
| \|差\| ≥ 12 | 「在这组里,更常露面的显然是 X。」 |
| \|差\| ≥ 5 | 「更常露面的是 X。」 |
| \|差\| < 5 | 「两者接近——这一组没有明显的赢家。」 |

- 02 章引言必须含天平读法句(照录):「每组像一架小天平——分高的一端更重,沉在下面;两端接近时,天平放平。」

### 2.4 表格件总表(六张,全 hairline 平面件)

| 表 | 落位 | 列头(照录) | 行数与规则 |
|----|------|-----------|-----------|
| 关键词总表 `.lt` | 01 开头 | 关键词 / 功能 · 分数 · 排名 / 一句话 | 4 行;首列定性词功能色衬线粗体;行序 = 最高 / 第二 / 居中代表 / 最低 |
| 对照总表 | 02 引言后 | 对照 / 你这一组的情况 | 4 行;弱端侧用 muted 小字 |
| 强端·代价表 `.duo-t` ×4 | 02 每轴天平图后 | 强端:X n / 代价:Y n(表头内联功能色;双弱轴两格均为定性名,如「Si 37.1:档案柜未上锁」) | 每轴 1 张,共 4 张 |
| 福利·代价表 `.pc-t` | 02 双弱轴后(**条件件**:两端均列全维后三位才出现) | 双弱带来的好处 / 双弱的代价 | 单行双格,各含 `<ul>`(✦/◇ 项目符);福利列 = 不被该能力绑定的自由,代价列 = 日常多花的力气 |
| 盲区表 | 04 | 盲区 / 真实成本 / 可以怎么做 | 行 = 费力功能(含分数);成本列 = 具体代价;「可以怎么做」列 = 可执行动作(含频次/场景) |
| 兼容表 `.lt` | 05 | 对方类型 / 互补与摩擦 / 解法 | **必配 4 行**:执行型(Te/Si 强)/ 同类(Fi/Ni 强)/ 体验型(Se 强)/ 照顾型(Fe 极强);互补一句、摩擦一句(成本措辞,禁评价词)、解法一句(可执行) |
| 优势表 `.lt` | 03 | 优势 / 适合的场合 | 3–4 行;首列 = 白话标题(功能色) |
| 建议表 `.lt` | 06 | 方向 / 做法 | 4 行;护强 ×2 + 补弱 ×2;「护强项回报 > 补短板」原则句为章引言必备 |

候选类型表(01 章内):`候选 / 栈序 / 命中` 三列,2 行;标题格式「最接近的类型:X 或 Y(仅供参考)」;命中列内用 `.hl` 高亮;栈序用彩色 `.fn` + 箭头。

### 2.5 亲密关系与收束件

- **rel 定义列表 `.relg`**(05 必配):四键 = 你给出的 / 你索取的 / 你的摩擦点 / 关系里的你;每键一段大白话。
- **场景块 `.scene`**(线型):小标签(`b`)取「你是不是也这样 / 写在最后 / 三句值得直接背下来的句式」;每轴一条「你是不是也这样」(第二人称 ≤60 字,落在具体行为,不引入新结论);06 章末「写在最后」= 全篇收束。
- **边界声明 `.bound-list`**(07 照录 writing-style §9.3 参考口径 4 条)+ `h3 附录 · 得分明细` 表(功能 / 得分 / 所属对照 / 这一组里更常露面 / 角色(按八维功能栈近似))。

### 2.6 分工纪律(评审查)

雷达管形状总览 / 柱状图管精确分数 / 天平图管四组对照与强弱 / 表格件管内容 / scene 管收束——**一图一职,互不复读**;正文不复述图表读法(语言密度规则见 writing-style §10.4)。

### 2.7 已废弃件清单(勿再生成;出现即 lint FAIL——单人)

速览卡 / 题记 / 三结论卡 / 恋爱一句话 / 目录 toc / 阅读指南框 / chapter-head / chapter-sub / pull 锐评 / 八彩条形图 / 轴对立合并图 / 排位剖面图 / 依恋象限图 / 类型栈打分表 / 组合卡 / 证据标签(ev-tag)/ meta-header 页眉 / 卡框类(.card/.grid2/.ov-grid/.procon)/ 进度条 / 首字下沉。

## 3. 单人报告结构模板(2800–4000 字)

```
hero(#hero)  kicker「Jungian Cognitive Functions · 人格坐标报告」
             + h1 定位句(从前两位功能生成,两句、每句 ≤10 字,em 渐变字;规则 writing-style §10.8)
             + lede 固定句(照录 writing-style §9.2)
             + 雷达图(SVG,§2.1)+ 图注 + 「↓ 往下读」
01 总览(01 · OVERVIEW)      你的总览:四个关键词
             关键词总表(.lt)+ h3 八维得分 + 柱状图(§2.2)+ 图注
             + h3 最接近的类型(候选表,.hl 命中)+ 「别把任何标签当身份证」固定句(§9.4)
02 四组对照(02 · YOUR TRADE-OFFS)
             引言(照录冠名修正句 + 天平读法句)+ 对照总表
             + 取舍一~四,每组:h3(Ni 预见 vs Ne 发散 式短对)
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
footer       .meta-line(报告日期 · 用户代号 · 数据来源)+ .disc(参考收束句 + 临床句)
```

结构规则:

- **章节恰 7 个**(sec-num 01–07;hero 不算章),锚点 id = s1–s7 + hero;无目录、无页眉(meta 进 footer)。
- 取舍组内顺序固定:天平图 → 强端·代价表 →(双弱时)福利·代价表 → 场景块;轴序按参考口径:一 = 看未来(Ni–Ne)/ 二 = 与当下(Se–Si)/ 三 = 下判断(Fi–Te)/ 四 = 对人对理(Fe–Ti)。
- **双弱判定** = 两端实测分均列全维后三位;此时天平 caption 用双弱分支,且组内加福利·代价表(无双弱轴则全报告无 .pc-t,正常)。
- caption 四分支、关键定性词(价值驱动/迷雾里认方向 等)措辞见 writing-style;**比喻收缩原则**最高优先(writing-style §4.1)。
- 附录得分明细 = 8 行 × 5 列(功能[彩色代码+学术名] / 得分[两位小数] / 所属对照 / 这一组里更常露面 / 角色[按八维功能栈近似,白话、无原型名])。
- 双人报告结构见 §5,不适用本节。

## 4. 输出规范

### 4.1 文件命名与保存
- 单人:`mbti_<用户代号>.html` + `mbti_<用户代号>.json`;双人:`mbti_<代号A>_<代号B>.html` + 两份单人次 JSON;v2 命名 `mbti_<代号>-v2.*`
- 用代号不用真名;**日期不进文件名**,只出现在 footer `.meta-line`
- 保存路径:默认 `/c/Users/elliot/Desktop/relations/MBTI/`;用户另行指定时从其指定
- 得分 JSON 的 schema 与字段规则见 `input-parsing.md` §4

### 4.2 必须标注的声明
- hero lede 固定句(照录 writing-style §9.2)
- 01 章末「类型只是名字」固定句(照录 §9.4)
- 07 边界声明(照录 §9.3,4 条)
- footer `.disc` 收尾句(照录 §9.3 尾句,含「不构成临床诊断」)
- 双人报告开头:照录伦理声明(couple-dynamics.md §6.2)

### 4.3 交付前验证(强制)

> 环境注记:本机 `python3` 是 Windows Store stub——**命令一律用 `python`**。

1. 运行 lint:`python scripts/lint_report.py <报告文件>`,输出「全部检查通过。」。单人检查项:
   - hero(kicker + h1 定位句 + lede 固定句 + 雷达 svg);柱状图(rect ≥8);天平图 =4;关键词总表 / 对照总表 / 优势表 / 建议表 / 盲区表三列头;候选类型表;rel 四键;兼容表 ≥4 行;duo-t =4;三句句式;07 边界声明;footer 临床句 + meta 行
   - 禁词(writing-style §6,含比喻收缩禁用系);卡框与已废弃件回流 = FAIL;`@page A4`、噪点、680px、@media print
   - 双人报告走双人口径(§4.3 旧制:chapter-head=8、pull=8、fit-fill ≥16、非预测承诺、伦理声明),单人结构件自动跳过
2. JSON 校验:得分 JSON 可解析、`scores` 8 键齐全且顺序为 `Ne,Ni,Fe,Fi,Te,Ti,Se,Si`、与报告中的分数一致
3. 浏览器渲染检查:雷达形状与分数相对高低互证、柱状图数值、天平倾角(分高端在下)、caption 分支、表格 hairline、锚点可跳、打印预览(注意浏览器缓存——用带 `?v=时间戳` 的地址强制刷新)无组件断裂、纸纹不打印
4. 基线样例回归:改过 lint 或 CSS 后先跑样例——`python scripts/lint_report.py examples/mbti_sample.html`(必须 PASS)
5. 全部通过才允许交付

## 5. 双人报告(2026-09-06 基线,冻结——本轮不迁移)

**双人报告沿用 2026-09-06 视觉改造定稿,本节内容为冻结快照;除 lint 双人口径外,2026-09-07 单人改造不影响双人。** 双人 CSS 底 = 09-06 卡框系(纸感令牌 + chapter-head + pull),完整样式块见 `examples/mbti_sampleA_sampleB.html`;单人新基线(§1–§3)不适用于双人。

### 5.0 结构模板(冻结)

```
页眉 .meta-header:报告日期 · 双方代号 · 数据来源(两人各自单独作答)
伦理声明 .guide-box(照录 couple-dynamics.md §6.2「在读这份报告之前」,置于最前)
阅读指南 .guide-box(「怎么读这份报告」,双人口径:模式作主语、无对错;末尾加粗附一行一句话总评)
目录 .toc(01–08 章 + 结语 + 附录)

01  你们各自是怎样的人 — 双栏卡 ×2(.person-cards:白卡 + border-top 3px 人物色;
      每卡三段:①一句话画像(h4 白话定性)②关系里常见的一幕(两三句,含对话片段)
      ③分数两行——最顺手一行、最费力一行,学术名+分数,八项齐全)
02  你们在这 8 件事上的合拍程度 — 评分条 ×8 组(.fit-*,外包 .wide,组按分数降序;
      条长 = 维度分×10%,双方各一条、同长同数,颜色 = 人;每组 .fit-head 右侧附中性
      分工注 .fit-note——「这格谁在扛」,禁评价词禁红绿)
      + .chart-note + 读图短评(章首写明双刻度换算:单人百分制 → 关系维度 1–10;
      短评按「最长 / 最短 / 中间合并带过」组织,不逐维一段)
03  这段关系自带的天赋 — .advice-card ×3–5(结构来源 / 具体表现 / 使用提示)
04  总体来看,你们的关系长什么样 — .callout 固定说明(couple-dynamics §0.2)+ 综合段
      (可含 h3「这段关系的短板长什么样」小节)
05  这段关系可能会怎样发展 — 开头照录非预测承诺(couple-dynamics §3.4,不得改写);
      四阶段每阶段 ≥1 个 .scene-box 场景(A: / B: 对话,内心独白斜体);全章 ⚪;
      阶段三必须含逻辑检验(循环为何稳定 / 双方隐性满足 / 打破需要什么)
06  你们最容易在哪几件事上卡住 — 冲突卡 ×2–3:标题 + 中性 chip 统计行(频次/破坏性/可解性,
      §5.2 .chip-row)+ .scene-box 对话 + 分析(模式作主语,禁指责任何一方)
07  需要留意的几个风险 — .caution-row ×2–4(等级 / 描述 / 会怎么变严重 / 前置信号)
08  具体可以怎么做 — 章头标 🔶;.advice-card ×3–5,每条含目标 / 怎么做 / 对话示例 / 什么时候失灵

结语(.epilogue:衬线居中、不编号、无锐评、无图表)
附录 这份报告的局限(.appendix:局限声明双人口径改写 + 结论依据构成统计行)
```

结构规则(冻结,原文照录):

- **双人报告为两个人读的同一份**:全程双向「你们」、对双方公平——不得出现偏问某一方的叙述框架(禁「作为 A 的你」式行文);理论分析严格以荣格八维理论为中心,机制解释一律落在功能轴、功能互动与内外倾上,伴侣研究/依恋研究等外部概念最多一句带过,不得作为分析框架
- `.chapter-head` 恰 **8 个**(num 两位数 **01–08**),每章开头 `.chapter-head` + 一句 `.chapter-sub`;**第 1–8 章章末各一条 `.pull` 锐评(共 8 条,≤22 字)**,结语与附录不放
- 锚点 `id`:c1–c8、epilogue、appb
- 评分条:每维度一个**共同分**(couple-dynamics §1),每组两条同长、同数——颜色只负责把两个人都放进图里,`.chart-note` 必须写明这层读法;评分过程数字不进正文(writing-style R8)
- 冲突 / 风险 / 阶段的描述一律"模式"作主语;场景、对话用 A: / B: 格式,内心独白用斜体
- 证据统计行先数后写:三个 `ev-tag` 计数必须与附录「✅ × N 处 · 🔶 × N 处 · ⚪ × N 处」一致
- 字数目标 **6000–9000**;文件命名与两份单人次 JSON 见 §4.1

### 5.1 双人 CSS 底(09-06 版,冻结)

双人报告 `<style>` = **09-06 单人基线全量复制** + 双人组件追加。关键类(逐字 CSS 见 `examples/mbti_sampleA_sampleB.html` 或 `examples/backup-2026-09-07/` 内旧样例):

`.chapter-head`(+`.num` 00–08 式两位数,双细线 #B9B29F)、`.chapter-sub`、`.meta-header`、`.guide-box`、`.toc`、`.pull`(≤22 字锐评,大引号)、`.ev-tag` 三色 chip、`.fn-code`、`.callout`、`.rel-label`、`.scene-box`、`.advice-card`(+`.ac-num`)、`.caution-row`、`.appendix`(+`.term-list`/`.appb`/`.ev-stat`)、`.faq-card`、`.wide`(±90px 破格)、半透明卡清单(`rgba(255,255,255,.72)`)、`@media print`(break-inside 清单)。

### 5.2 双人专属组件(冻结)

**颜色铁律:颜色 = 人。** P1 紫 `--p1-color: #8E5EA2` / P2 绿 `--p2-color: #4F9D69`;人物标签、评分条、双栏卡从这两个变量取色;功能色只用于功能名文字标记(`.fn-code` 体系);不引入红绿档位色。

| 类名 | 用途 | CSS 关键属性 |
|------|------|-------------|
| `.fit-group`(+`.fit-head`/`.fit-def`/`.fit-row`/`.fit-who`/`.fit-track`/`.fit-fill`/`.fit-num`/`.fit-note`) | 第 2 章评分条 ×8 组 | 每组 = 维度名 + 一句话定义 + 双方各一条横条(条长 = 维度分×10%,数值条末同人物色,track `#EFEDE5` 高 18px 圆角 5);`.fit-note` 组右端中性分工注(muted,「这格谁在扛」,禁评价词);8 组外包 `.wide`,组按分数降序;`.chart-note` 说明「分数属于两个人,两条只是把双方都放进图里,颜色只区分人,不分好坏」 |
| `.person-cards` + `.person-card`(+`.cp1`/`.cp2`) | 第 1 章双栏卡 ×2 | grid `1fr 1fr` gap 14px(≤640px 单列);卡 = `rgba(255,255,255,.72)` + 1px var(--border) + 圆角 10 + `border-top:3px solid` 人物色;h4 .98em;p .86em/1.75 |
| `.chip-row` + `.chip` | 第 6 章冲突统计行 | 行 `display:flex;gap:8px;flex-wrap:wrap`;chip `inline-block .74em/700 圆角 20 padding 2px 10px`,中性色 `#F1F1EA/#5F6B76`——高/中/低只靠文字,禁红绿 |
| `.p1-tag` / `.p2-tag` | 双人人物标签(lint 必查两者并存) | `inline-block .75em padding 1px 9px 圆角 4 #fff/700`;底色 `var(--p1-color)`/`var(--p2-color)` |
| `.dialogue` | 对话文本 | `padding-left:14px;border-left:2px solid var(--border);margin:8px 0`;说话人 b 用人物色,内心独白 `<em>` 斜体 |
| `.epilogue` | 结语 | `border-top:2px dashed var(--border);margin-top:52px;padding-top:30px;text-align:center`;h2 衬线 1.3em;p 居中 |

旧件(`.dual-col`/`.meter-bar` 系/`conflict-header` 红黄绿/`highlight-box`/`warn-box`/`stack-box`)勿再生成;`meter-fill` 向后兼容检查保留。

### 5.3 双人口径 lint(冻结)

chapter-head =8(01–08)、pull =8、评分条行 ≥16(.fit-fill)、p1/p2 标签并存、非预测承诺、伦理声明;单人口径计数(速览卡/题记/彩条图/轴对立图/hero/表格件)自动跳过。
