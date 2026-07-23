# HTML 输出模板

所有报告 = 来访者直接阅读的终端产品，默认保存到 **Windows 桌面**（WSL 路径 `/mnt/c/Users/elliot/Desktop/`）。语言规范见 writing-style.md。

## Contents
- §1 CSS 基础体系（变量 / 排版 / 组件类 / 打印样式）
- §2 图表与布局（柱状图 / 功能速览网格 / 感知轴×判断轴直角坐标系 / 大五剖面图 / 依恋象限图 / 类型栈对比图）
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
| `.summary-card` | 一页速览卡 | `background:#fff; border:2px solid var(--accent); border-radius:10px; padding:22px 26px` |
| `.ev-tag` | 证据标签基类 | `display:inline-block; font-size:0.72em; padding:2px 8px; border-radius:3px; vertical-align:middle; margin-left:6px` |
| `.ev-research` / `.ev-theory` / `.ev-hypothesis` | ✅绿 / 🔶橙 / ⚪灰 | 背景 #e8f5e9 字 #2e7d32 / 背景 #fff3e0 字 #e65100 / 背景 #f0f0ee 字 #757575 |
| `.toc` | 锚点目录 | `background:#fff; border:1px solid var(--border); border-radius:8px; padding:16px 22px; font-size:0.9em` |
| `.appendix` | 附录区块 | `border-top:2px dashed var(--border); margin-top:48px; padding-top:24px` |
| `.faq-item` | FAQ 条目 | `margin-bottom:18px` |
| `.tier-1` ~ `.tier-4` | 梯度层级展示 | 不同背景色 + 左边框颜色对应层级 |
| `.bar-container` / `.bar-track` / `.bar-fill` | 柱状图 | `display:flex; height:22px; border-radius:4px; overflow:hidden` |
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

## 2. 图表与布局（全部内联 SVG，无外部依赖，打印安全）

### 2.1 柱状图（功能分数条，第 1 章唯一图表）
```html
<div class="bar-container">
  <span class="bar-label" style="color:var(--fi)">内倾情感</span>
  <span class="bar-track">
    <span class="bar-fill fi-fill" style="width:64.95%">64.95</span>
  </span>
  <span class="bar-score">64.95</span>
</div>
```
**CSS 关键**：`.bar-fill` 的 `style="width:XX%"` 直接使用分数值作为百分比。标签用学术名。

### 2.2 功能速览两列网格（第 1 章，替代原先的长段落）
- 用 `.fn-grid` 把八个功能排成两列卡片
- 每张卡片：左侧 4px 色条（功能色）+ 学术名 + 一句白描 + 右侧迷你分数
- 好处：一眼能对应哪个分数对应哪个功能，不用上下滚动找

### 2.3 感知轴 × 判断轴直角坐标系（第 1 章，必配）
- `viewBox="0 0 420 380"`，绘图区 x=60..360, y=40..340，中心 (210,190)
- 横轴 = 感知轴：左端"实感 S (Si+Se总分)"，右端"直觉 N (Ni+Ne总分)"（端标签含分数）
- 纵轴 = 判断轴：下端"思考 T (Ti+Te总分)"，上端"情感 F (Fi+Fe总分)"（端标签含分数）
- 中心画十字虚线 + 小圆点标"均衡"
- **均衡区**：r=40 圆形区域（淡灰色填充 + 虚线边），表示 ~5% 以内的偏好阈值，落在区内视为基本均衡，落在区外表示有明确偏好
- **不画象限标注**、不画虚线不确定圆、不写底部说明文字——避免文字打架
- 坐标计算：x偏移比 = (N-S)/(N+S)，y偏移比 = (F-T)/(F+T)；**死区+平方根映射**：|偏移比| < 5% → 圆点居中（均衡区内）；|偏移比| ≥ 5% → √((|偏移比|-5%)/95%) × 180，方向取 sign(偏移比)。x = 210 + x偏移，y = 190 - y偏移（SVG y向下）。死区让真正均衡的轴不会显示虚假偏好，平方根让中等偏好清晰可见（如 13.6% → 约 54px，明显在均衡区外）
- 来访者位置用实心圆点（r=10, 红色#e74c3c, 白边）+ 中心到圆点虚线（强调偏离）+ 白色背景标签框（"你的位置 / 偏直觉 57% · 判断均衡"），标签框防重叠

### 2.3 大五剖面图（第 4 章）
- 四维度各一条连续标尺：SVG 或 HTML 实现，长条左端"低"右端"高"
- 来访者位置用圆点（●）标记；居中倾向的点放中段，注明"倾向不明显"

### 2.4 依恋象限图（第 7 章）
- SVG `viewBox="0 0 300 260"`：横轴"对他人的看法（消极 ←→ 积极）"，纵轴"对自己的看法（消极 ←→ 积极）"
- 四象限标注：安全型（右下）/ 痴迷型（右上）/ 疏离型（左下）/ 恐惧型（左上）
- 推测位置用**虚线圆**表示不确定性；若结论对分数波动敏感，虚线圆跨相邻象限边界
- 恋爱关系与家人关系各占一张小图

### 2.5 类型栈对比图（附录 A）
- 两个候选类型并排，各画 8 级阶梯：每级一个色块（功能色）标注"位置 学术名"，右侧标实测分 + ✓/≈/✗
- 阴影位（5-8）色块加 `opacity:0.55`

## 3. 报告结构模板

### 3.1 单人报告（来访者终端产品，7000-9000 字）

```
页眉 .meta-header：测评日期 · 报告日期 · 量表来源 · 来访者编号
阅读指南 .guide-box（照录 writing-style.md §9.2）
目录 .toc（锚点导航）

0  一页速览卡 .summary-card
   （最擅长的事 + 三个最自然的事 + 两个需要注意的地方 + 依恋一句话）
1  你的分数长什么样
   ［柱状图］
    ［功能速览两列网格：学术名+白描+迷你分数］
    ［三个梯队框］
    ［感知轴 × 判断轴直角坐标系（SVG）］
    ［结构性发现 callout（含核心张力预告）］
   深度要求：每条发现必须有具体化支撑
2  你最可能是哪种类型（双候选 + 主观置信度 + 置信度说明；🔶）
   深度要求：每个候选写清"匹配什么 / 解释不了什么 / 需要什么额外假设"
3  你的性格画像（第一套框架；🔶）
   深度要求：以 1-2 个核心张力为主线展开；
   含核心动力 / 情感运作 / 思维与决策 / 压力下的你；
   至少一处场景级描写；零工程隐喻
4  你的大五人格画像（第二套框架；四维度，✅）
   ［大五剖面图］每维度：程度 + 白描 + 具体化支撑
5  交叉验证：两套理论怎么看同一个人（收敛处 + 分歧处）
6  你的优势与成长空间（双栏）
7  你的亲密关系模式（⚪；恋爱 vs 家人分开说）
   ［依恋象限图］必须含"误解全过程"场景分解；
   章末照录谦卑段落 §9.1
8  成长环境的可能模样（⚪；多重假设并列；章末照录谦卑段落 §9.1）
9  给你的具体建议
   每条 = 现状 + 理解（为什么会有这个模式）+ 可以试着做（含频次/场景）
   禁止：工程隐喻、"咨询师"字样、"会谈方向"

附录A（.appendix .appendix-tech）可选阅读：类型是怎么推出来的
附录B（.appendix）这份报告的局限（照录 §9.3 + 结论依据构成统计）
附录C（.appendix）你可能想问的（.faq-item × 4-6 条）
```

### 3.2 双人报告（来访者终端产品）

```
页眉 .meta-header（含双方数据来源）
伦理声明 .guide-box（照录 couple-dynamics.md §6.2，去除咨询师字样）
目录 .toc

1  你们各自是怎样的人（双栏卡片 + 每人大五快照行：仅四维度）
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
- 单人：`report_YYYYMMDD_来访者编号.html`
- 双人：`couple_report_YYYYMMDD_来访者编号.html`
- 用编号不用真名，保护来访者隐私
- 保存路径：**默认 Windows 桌面 `/mnt/c/Users/elliot/Desktop/`**；用户另行指定时从其指定

### 4.2 必须标注的声明
- 阅读指南（报告开头，照录 writing-style.md §9.2）
- 报告末尾："本报告基于认知功能测评数据的理论分析，不构成临床诊断。"
- 依恋/成长环境章末：照录谦卑段落（§9.1）
- 双人报告开头：照录伦理声明（couple-dynamics.md §6.2）

### 4.3 交付前验证（强制）
1. 运行 lint：`python3 scripts/lint_report.py <报告文件>`，全部 PASS
2. 浏览器打开检查：柱状图可见、剖面图/象限图/类型栈图渲染正常、速览卡完整、目录锚点可跳转、打印预览无组件断裂
3. 数一遍 ✅🔶⚪ 实际数量，与附录 B 统计一致
4. 全部通过才允许交付
