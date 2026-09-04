# HTML 输出模板

所有报告 = 来访者直接阅读的终端产品，默认保存到 `/c/Users/elliot/Desktop/relations/MBTI/`（Git Bash 路径）。语言规范见 writing-style.md。

## Contents
- §1 CSS 基础体系（变量 / 排版 / 组件类 / 打印样式）
- §2 图表与布局（降序条形图 / 功能速览网格 / 三轴极性图 / 排位剖面图 / 依恋象限图 / 类型栈图）
- §3 报告结构模板（单人 / 双人，含各章深度要求）
- §4 输出规范（命名 / 声明 / 交付前验证）

## 1. CSS 基础体系

### 1.1 CSS 变量（颜色方案）
```css
:root {
  --bg: #fafaf8; --text: #1a1a1a; --muted: #5a5a5a; --border: #d0d0cc; --accent: #2c3e50;
  --fi: #c0392b; --ni: #8e44ad; --fe: #2980b9; --ti: #16a085; --te: #d35400;
  --ne: #e67e22; --se: #27ae60; --si: #7f8c8d;
  --highlight: #f9f3e8; --card-bg: #ffffff;
}
```
八个功能的颜色分配为常量，不可修改。双人报告新增 --p1-color（紫）和 --p2-color（绿）。

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
| `.chapter-key` | 章一句话结论框 | `background:var(--highlight); border-left:4px solid var(--accent); padding:10px 16px; border-radius:4px; margin:10px 0 18px; font-weight:600` |
| `.summary-card` | 一页速览卡 | `background:#fff; border:2px solid var(--accent); border-radius:10px; padding:22px 26px` |
| `.ev-tag` | 证据标签基类 | `display:inline-block; font-size:0.72em; padding:2px 8px; border-radius:3px; vertical-align:middle; margin-left:6px` |
| `.ev-research` / `.ev-theory` / `.ev-hypothesis` | ✅绿 / 🔶橙 / ⚪灰 | 背景 #e8f5e9 字 #2e7d32 / 背景 #fff3e0 字 #e65100 / 背景 #f0f0ee 字 #757575 |
| `.toc` | 锚点目录 | `background:#fff; border:1px solid var(--border); border-radius:8px; padding:16px 22px; font-size:0.9em` |
| `.appendix` | 附录区块 | `border-top:2px dashed var(--border); margin-top:48px; padding-top:24px` |
| `.faq-item` | FAQ 条目 | `margin-bottom:18px` |
| `.callout` | 强调框 | `background:#fff; border:1px solid var(--border); border-radius:8px; box-shadow` |
| `.scene-box` | 场景对话框 | `border:1px solid #e0e0dc; border-radius:6px; padding:16px 20px; margin:12px 0; background:#fff` |
| `.dual-col` | 双栏布局 | `display:grid; grid-template-columns: 1fr 1fr; gap:24px` |
| `.dialogue` | 对话文本 | `padding-left:16px; border-left:2px solid #e0e0dc` |
| `.chart-box` | 图表容器 | `background:#fff; border:1px solid var(--border); border-radius:8px; padding:18px; margin:14px 0; text-align:center` |
| `.stack-box` | 功能栈标签（附录/类型栈图） | `display:inline-block; padding:3px 10px; border-radius:3px; font-weight:700; color:#fff` |
| `.meter-bar` / `.meter-track` / `.meter-fill` | 适配性评分条 | `display:flex; height:20px; .meter-fill 必须 display:block; min-width:4px` |
| `.conflict-header` | 冲突统计标签 | `display:flex; gap:16px; flex-wrap:wrap; font-size:0.9em` |
| `.match-yes` / `.match-no` / `.match-ok` | 类型匹配标记 | 绿 ✓ / 红 ✗ / 橙 ≈ |
| `.p1-tag` / `.p2-tag` | 双人报告人物标签 | 紫色/绿色 inline-block 标签 |
| `.fn-grid` | 功能速览两列网格 | `display:grid; grid-template-columns: 1fr 1fr; gap:12px; font-size:0.92em; margin:14px 0` |
| `.fn-grid-item` | 网格项 | `display:flex; align-items:center; gap:10px; padding:8px 12px; background:#fff; border:1px solid var(--border); border-radius:6px` |
| `.fn-grid-bar` | 网格内迷你色条 | `width:4px; height:28px; border-radius:2px; flex-shrink:0` |

### 1.4 打印样式（必须有——来访者会打印或导 PDF）
```css
@media print {
  body { background:#fff; }
  .summary-card, .callout, .scene-box, .guide-box, .chart-box, .col-box { break-inside: avoid; }
  .toc { display: none; }
  * { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
}
```

## 2. 图表与布局

> **图的分工**：第 1 章降序条形图（分数模样）＋ 功能速览网格（每个维度的解释）；第 3 章三轴极性图（两条功能轴的倒向）＋ 排位剖面图（八位置的形状）；第 6 章依恋象限图；附录 A 类型栈对照。禁用面积/大小编码（气泡图）——窄分数段下不可读。数据细节由网格与图表承载，正文只说倾向与场景。

### 2.1 降序条形图（第 1 章「分数模样」）
- 八条功能色条按分数降序排列，条内标分数；一眼看出谁高谁低
- 禁用面积/大小编码（气泡图）

### 2.2 功能速览两列网格（第 1 章「每个维度的解释」）
- 用 `.fn-grid` 把八个功能排成两列卡片
- 每张卡片：左侧 4px 色条（功能色）+ 学术名 + 一句白描 + 右侧分数
- 轴结构用**文字**逐轴讲（writing-style.md §2.1 模板）：每条轴一段——两端是谁、倒向哪端、意味着什么；每条轴必须有具体化支撑

### 2.3 三轴极性图（第 3 章「两条功能轴」）
- 三行：态度轴（内倾四项合计 ↔ 外倾四项合计）/ 感知轴（实感侧 ↔ 直觉侧）/ 判断轴（思考侧 ↔ 情感侧）
- 每行中轴两侧各一条，**长度＝分数（线性映射）**——三条轴的倾斜全部肉眼可见；**禁用位置标记滑轨**（50 附近的偏移量视觉上无信息）
- 条内标分数；条端上方标两极名；行末读数结论（偏内倾 / 偏直觉 / 偏情感）
- 数字由图承载，正文只说倾向（"直觉侧明显长于实感侧"），不罗列数值

### 2.4 排位剖面图（第 3 章「八位置原型」）
- 八条横条按排位（第一至八位）排列，**不按分数排序**——条长＝该位置的功能分数
- 深色＝平时的你（第一至四位），浅色＝阴影里的你（第五至八位，同色淡化 50%）
- 50 分虚线参照；异常位（如第六位全场最高）行末标注
- 一眼读出栈形状：哪里强、哪里凹、哪里尖峰

### 2.5 依恋象限图（第 6 章）
- SVG `viewBox="0 0 300 260"`：横轴"对他人的看法（消极 ←→ 积极）"，纵轴"对自己的看法（消极 ←→ 积极）"
- 四象限标注：安全型（右下）/ 痴迷型（右上）/ 疏离型（左下）/ 恐惧型（左上）
- 推测位置用**虚线圆**表示不确定性；若结论对分数波动敏感，虚线圆跨相邻象限边界
- 恋爱关系与家人关系各占一张小图

### 2.6 类型栈对比图（附录 A）
- 两个候选类型并排，各画 8 级阶梯：每级一个色块（功能色）标注"位置 学术名"，右侧标实测分 + ✓/≈/✗
- 阴影位（5-8）色块加 `opacity:0.55`

## 3. 报告结构模板

### 3.1 单人报告（来访者终端产品，6000-8500 字；结构含原型章与成长方向章时取上限）

**理论主线：荣格八维是地基，类型只是窄标签。** 全报告围绕四条轴、8 位置原型展开；MBTI 类型仅在第二章作为快速定位出现，并明示其局限。

```
页眉 .meta-header：测评日期 · 报告日期 · 量表来源 · 用户代号
阅读指南 .guide-box（照录 writing-style.md §9.2）
目录 .toc（锚点导航）
各章（第 0 章除外）h2 后加「一句话结论」框 .chapter-key（模板见 writing-style.md §5）

0  一页速览卡 .summary-card
   （最擅长的事 + 三件最不费劲的事 + 两件要留意的事 + 恋爱一句话）
1  你的分数长什么样 + 每种活动是什么
   ［章结论框］
   ［降序条形图（§2.1）——分数模样］
   ［功能速览两列网格：学术名+白描+分数——每个维度的解释］
   （感知/判断大类的定义由网格白描与第 3 章 §3.2 承载，本段不再重复）
2  你最可能是哪种类型（双候选 + 主观置信度 + 置信度说明 + 「类型只是名字」固定说明；🔶；附录 A 打分对照表）
   深度要求：每个候选写清"匹配什么 / 解释不了什么 / 需要什么额外假设"；偏离只述现象、不编归因
3  按荣格理论，你的分数在说什么（核心章；🔶；声明理论模型无实证常模）——四个小节：
   ［章结论框＋本章三句话摘要框］
   ［3.1 态度：内倾 vs 外倾（能量方向）］
   ［3.2 两条功能轴：感知轴/判断轴的倒向与含义＋三轴极性图（§2.3）；数字由图承载，正文说倾向与场景；各配一个假设场景］
   ［3.3 意识、阴影与八位置原型：补偿原则＋排位剖面图（§2.4）＋白话框架＋排位表＋如实呈现含异常位］
   ［3.4 核心张力 1-2 条，完整段落展开］

附录A（.appendix .appendix-tech）可选阅读：类型是怎么推出来的（8 位置 ✓/≈/✗ 打分对照表 + 位置参考表）
附录B（.appendix）这份报告的局限（照录 §9.3 + 结论依据构成统计）
附录C（.appendix）你可能想问的（.faq-item × 4-6 条）
```

### 3.2 双人报告（来访者终端产品）

```
页眉 .meta-header（含双方数据来源 + 双方代号）
伦理声明 .guide-box（照录 couple-dynamics.md §6.2，去除咨询师字样）
目录 .toc

1  你们各自是怎样的人（双栏卡片，纯八维结构）
2  你们在这 8 件事上的合拍程度（每维度：评分条 + 分析 + 📋 具体场景）
3  这段关系自带的天赋（3-5 项）
4  总体来看，你们的关系长什么样（8 条评分条汇总 + 综合评估）
5  这段关系可能会怎样发展（四阶段推演，不含时间，含场景 + 阶段三逻辑检验）
6  你们最容易在哪几件事上卡住（4+ 冲突，含场景对话 + 频次/破坏性/可解性标签）
7  需要留意的几个风险（3-5 个，含升级路径 + 预警信号）
8  具体可以怎么做（5 类方法，含成功对话示例 + 适用条件）
9  结语（大白话：零术语、零代码、零类型标签）

附录：这份报告的局限（照录 §9.3 + 伦理声明重申）
```

## 4. 输出规范

### 4.1 文件命名与保存
- 单人：`mbti_<用户代号>.html` + `mbti_<用户代号>.json`
- 双人：`mbti_<代号A>_<代号B>.html` + `mbti_<代号A>.json` + `mbti_<代号B>.json`（两份单人次 JSON）
- 版本冲突（代号重复）时按 `input-parsing.md` §3 问 -v2/覆盖；v2 命名 `mbti_<代号>-v2.html/.json`
- 用代号不用真名，保护来访者隐私；**日期不进文件名**，只出现在报告页眉 `.meta-header`
- 保存路径：**默认 `/c/Users/elliot/Desktop/relations/MBTI/`**；用户另行指定时从其指定
- 得分 JSON 的 schema 与字段规则见 `input-parsing.md` §4

### 4.2 必须标注的声明
- 阅读指南（报告开头，照录 writing-style.md §9.2）
- 报告末尾："本报告基于认知功能测评数据的理论分析，不构成临床诊断。"
- 依恋/成长环境章末：照录谦卑段落（§9.1）
- 双人报告开头：照录伦理声明（couple-dynamics.md §6.2）

### 4.3 交付前验证（强制）
1. 运行 lint：`python3 scripts/lint_report.py <报告文件>`，全部 PASS
2. JSON 校验：得分 JSON 可解析、`scores` 8 键齐全且顺序为 `Ne,Ni,Fe,Fi,Te,Ti,Se,Si`、与报告中的分数一致
3. 浏览器打开检查：功能速览网格/象限图/表格渲染正常、速览卡完整、目录锚点可跳转、打印预览无组件断裂
4. 数一遍 ✅🔶⚪ 实际数量，与附录 B 统计一致
5. 全部通过才允许交付
