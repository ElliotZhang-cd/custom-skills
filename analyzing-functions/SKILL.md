---
name: analyzing-functions
description: 解读荣格八维 / MBTI 八功能分数，判定类型并为单人产出人格 HTML 报告、为情侣双方产出关系动力 HTML 报告；不覆盖职业适配、年龄推断，以及理论范围之外的婚恋适配裁决。当用户以八维测试的"复制分数"文本、导出数据 JSON 或口头报数给出分数（一组分数 → 单人，两组 → 双人）并要求解读、判型或生成报告时使用。
---

# analyzing-functions：八维分数 → 人格分析报告

## Goal

产出一份易懂的基于荣格《心理类型》与八功能-原型模型的分析报告，让没有心理学基础的读者也能直观形象的理解。

## Context / Input

### 理论地基与单一出处分层（权威地图）

每个事实只有一个家：机制 → theory-spec / couple-theory-spec；写法与固定文案 → copy-rules；图形几何 → 两卷 visual-spec；token↔markup 契约 → 两份模板头部注释；流程与数据绑定 → workflow-single / workflow-couple；判型可执行编码 → typing-procedure。转述纪律：转述层只做绑定，机制一律写"见 §x.x"，不复述。

- `references/theory-spec.md` —— 单人模式**唯一理论来源**。论断必须能指回具体条目；它没覆盖的，一律"理论未覆盖，不作推断"。
- `references/couple-theory-spec.md` —— 双人模式**唯一理论来源**：上游引用 theory-spec，不重定义分数→类型/堆叠/置信度推导；双人机制的"是什么、为什么"唯一出处是它。
- `references/stacks.json` —— 判定数据（16 型堆叠、毕比原型名、轴配对规则 axis_rule、昆克 grip/loop 文案、功能色两表）。
- `references/copy-rules.md` —— 语气、写法、禁区与固定文案；生成文案前必读。
- `references/glossary.md` —— 术语表（含 `_Avoid_` 反例）。
- `references/workflow-single.md` / `references/workflow-couple.md` —— 单人 / 双人的流程与数据绑定（章节骨架、逐章绑定表）。
- `references/typing-procedure.md` —— 判型可执行编码（两模式共用，第 2 步 / D2 调用）。
- `references/qa-checklist.md` —— 交付前核对清单（单人 / 双人）。
- `references/typing-regression.md` —— 判型回归用例集（改动判型规则后逐例对账）。

### 按需加载（渐进式披露）

本文件只承担**路由与两模式共用规则**；上列文件按需读取，**不要一次性全读**：

- 一组分数（单人）：workflow-single → theory-spec → copy-rules → single-visual-spec → stacks.json。
- 两组分数（双人）：workflow-couple → couple-theory-spec → copy-rules → couple-visual-spec → stacks.json（设计代币与 theory-spec 判型节按需取用）。
- 判型时取 typing-procedure，写文案时取 copy-rules，画图时取对应 visual-spec，交付前取 qa-checklist。

### 输入形态

- Tab 分隔文本（固定顺序 Se Si Ne Ni Te Ti Fe Fi）。
- 导出 JSON（优先 `scoresExact`）。
- 口头报数（顺序不明必须确认，不得猜）。

## Workflow

严格按序：先做第 0 步模式判定，再按模式从 references 取用详细流程。

### 第 0 步：模式判定

- 同一请求出现**两组**八维分数 → 双人模式（见 `references/workflow-couple.md`）。
- 一组分数 → 单人模式（第 1–4 步）。
- 两组分数但用户明确只要单人解读 → 按用户指示分别走单人流程，不产出双人报告。
- 形态或意图不明（口头报数未分人、缺一方、"分析我们俩"但没给全分数）→ 停止并确认，不得猜。

### 后续流程（细则见 references/）

- **单人** → `references/workflow-single.md`：第 1 步校验 → 第 2 步判型 → 第 3 步逐章写作（7 章绑定表）→ 第 4 步填充模板。
- **双人** → `references/workflow-couple.md`：D1 输入校验 → D2 单人推导与层级决定 → D3 写栈校验 + 六透镜 → D4 组装 7 节报告。
- **判型算法**（两模式共用，第 2 步 / D2 调用）→ `references/typing-procedure.md`。
- **交付前核对** → `references/qa-checklist.md`。

## Output Format

- 单人：默认输出目录 `~/Desktop/MBTI/reports/`（用户可指定别处）；文件名 `报告_<首选类型>_<YYYYMMDD>.html`（正斜杠、用户目录相对；目录不存在则创建）
- 双人：默认输出目录同上；文件名 `报告_关系_<称谓A>×<称谓B>_<YYYYMMDD>.html`，无称谓输入时用各自首选类型 `报告_关系_<类型A>×<类型B>_<日期>.html`。目录不存在则创建。

## Success criteria

- 单人：读者能直观理解自己哪个功能在主导、八功能分化情况、压力下的表现、未来发展方向。
- 双人：读者能直观理解双方如何吸引、共同语言与摩擦点、冲突的典型表现与各自的磨合方向。
- 两模式共同：报告自包含（无外部请求）、结构与固定文案严格合规则、每句实质论断可指回 theory-spec / couple spec。

## Stop rules

- 口头报数且顺序不明 → 停止并确认，不得猜。
- 单分超出 0–121.8 → 停止并询问；单人总分偏差 > 20 → 拒绝生成，要求重新提供。双人模式容差更严：任一方八项之和 |Σ−406| > 0.05 或有超界值 → 停止并报告输入异常，不得继续（couple-theory-spec §1.1——双人要做跨人结构比较，对 ipsative 假设依赖更重；单人的 ±5/±20 不适用于双人）。
- 内容超出理论覆盖（职业适配、年龄推断等）→ 一律回应"理论未覆盖，不作推断"；婚恋适配裁决（"合不合适""该不该继续"）双人模式同样禁止（couple-theory-spec 根本立场）——双人报告只回答动力机制与功课。
- 转述层（本文件 / copy-rules / visual-spec / 模板注释）与 theory-spec / couple spec 冲突 → 停止并报告用户，**不在运行中修改任何 skill 文件**。
