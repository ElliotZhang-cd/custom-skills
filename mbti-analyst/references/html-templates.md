# HTML 输出模板

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
八个功能的颜色分配为常量，不可修改。在双人报告中新增 --p1-color 和 --p2-color。

### 1.2 基础排版
- 字体：`"Noto Serif SC", "Source Han Serif SC", "Songti SC", Georgia, serif`
- 行高：`1.85`
- 最大宽度：单人 860px，双人 900px
- 响应式：`@media (max-width: 640px)` 或 `700px`

### 1.3 核心组件类

| 类名 | 用途 | CSS 关键属性 |
|------|------|-------------|
| `.tier-1` ~ `.tier-4` | 梯度层级展示 | 不同背景色 + 左边框颜色对应层级 |
| `.bar-container` / `.bar-track` / `.bar-fill` | 柱状图 | `display:flex; height:22px; border-radius:4px; overflow:hidden` |
| `.callout` | 强调框 | `background:#fff; border:1px solid var(--border); border-radius:8px; box-shadow` |
| `.scene-box` | 场景对话框 | `border:1px solid #e0e0dc; border-radius:6px; padding:16px 20px` |
| `.warn-box` | 风险警告框 | `border-left:3px solid #c0392b; background:#fef5f5` |
| `.phase-box` | 阶段推演框 | `border-left:3px solid var(--accent); background:#fafaf8` |
| `.dual-col` | 双栏布局 | `display:grid; grid-template-columns: 1fr 1fr; gap:24px` |
| `.dialogue` | 对话文本 | `padding-left:16px; border-left:2px solid #e0e0dc` |
| `.stack-box` | 功能栈标签 | `display:inline-block; padding:3px 10px; border-radius:3px; font-weight:700; color:#fff` |
| `.meter-bar` / `.meter-track` / `.meter-fill` | 适配性评分条 | `display:flex; height:20px; .meter-fill 必须 display:block; min-width:4px` |
| `.conflict-header` | 冲突统计标签 | `display:flex; gap:16px; flex-wrap:wrap; font-size:0.9em` |
| `.match-yes` / `.match-no` / `.match-ok` | 类型匹配标记 | 绿 ✓ / 红 ✗ / 橙 ≈ |
| `.p1-tag` / `.p2-tag` | 双人报告的人物标签 | 紫色/绿色 inline-block 标签 |

## 2. 柱状图实现（关键——常见 bug 修复）

### 2.1 单人报告（功能分数条）
```html
<div class="bar-container">
  <span class="bar-label" style="color:var(--fi)">Fi</span>
  <span class="bar-track">
    <span class="bar-fill fi-fill" style="width:67.9%">67.86</span>
  </span>
  <span class="bar-score">67.86</span>
</div>
```
**CSS 关键**：`.bar-fill` 的 `style="width:XX%"` 直接使用分数值作为百分比（即 `width` = 分数%），原点 0，上限 100。分数均为百分制，无需额外换算。`display:block` 或 inline-block 确保宽度生效。

### 2.2 双人报告（适配性评分条）——需要特别小心
```html
<div class="meter-bar">
  <span class="meter-label">精神共鸣</span>
  <span class="meter-track">
    <span class="meter-fill fill-high" style="width:80%"></span>
  </span>
  <span class="meter-score">8/10</span>
</div>
```
**CSS 关键修复**：
```css
.meter-fill { display:block; height:20px; border-radius:4px; min-width:4px; }
```
- `.meter-fill` 必须 `display:block`（`<span>` 默认 inline 无法渲染 width/height）
- 必须设置 `min-width` 防止低分条完全不可见
- `.meter-track` 已经 `overflow:hidden`

## 3. 报告结构模板

### 3.1 单人报告（7+1 章）
1. 原始数据与梯度分层（含柱状图）
2. MBTI 类型推断（含两个候选类型的匹配表）
3. 人格画像（核心动力 / 情感运作 / 思维风格 / 直觉通道 / 物理接口）
4. 优势与短板（双栏对照）
5. 成长环境推断（分功能讨论 + 综合环境画像）
6. 依恋类型推断（伴侣关系 / 父母关系 + 总结 callout）
7. 成长建议（按最弱功能优先级排序）
8. （可选追加）现代心理学框架再分析——大五 / SDT / Gross / 依恋维度 / McAdams

### 3.2 双人报告（8 章）
1. 双方认知功能核心结构特征（双栏卡片 + 结构性结论列表）
2. 八维度适配性分析（每维度含场景示例）
3. 综合适配性评估（评分条 + 详细综合评估 callout）
4. 恋爱过程推演（四阶段，不含时间，含场景 + 逻辑检验）
5. 典型恋爱冲突（含场景对话 + 统计标签）
6. 典型恋爱风险（含升级场景示例）
7. 解决办法（含具体对话和步骤）
8. 结语（大白话，无术语）

## 4. 输出规范

### 4.1 文件命名
- 单人：`cognitive_analysis.html`（或带编号）
- 双人：`couple_compatibility.html`
- 保存路径：优先用户指定路径，默认桌面

### 4.2 必须标注的声明
- 报告末尾：`本报告基于认知功能测评数据的理论分析，不构成临床诊断。`
- 所有依恋推断后：标注"推测"或"理论推断"
- 所有成长环境推断前：`此为基于功能分数的概率性重建，非确定性结论`
