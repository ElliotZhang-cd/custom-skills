# 分析模板

本文件提供认知闭环各环节的详细模板。Agent 按需加载，不必一次性全部填充。关键原则：**先检查适用性，再填充内容**。

## Contents

- [认知闭环追踪清单](#认知闭环追踪清单)
- [环节 1：界定（系统论）](#环节-1界定系统论)
- [环节 2：感知（信息论）](#环节-2感知信息论)
- [环节 3：调节（一阶控制 + 二阶控制/元认知）](#环节-3调节一阶控制--二阶控制元认知)
- [环节 4：互动（博弈论）](#环节-4互动博弈论)
- [环节 5：涌现（自组织理论）](#环节-5涌现自组织理论)
- [环节 6：跃迁（突变论）](#环节-6跃迁突变论)
- [环节 7：反思（元认知检查点 2）](#环节-7反思元认知检查点-2)
- [输出格式模板](#输出格式模板)
- [干预建议格式（含置信度声明）](#干预建议格式含置信度声明)
- [质量检查清单（输出前自验）](#质量检查清单输出前自验)

---

## 认知闭环追踪清单

```
□ 界定（系统论）：边界是否清晰？若否，询问用户。
□ 感知（信息论）：数据是否足够？若 C < H，标记不可量化。
□ 调节（一阶控制）：延迟是否可接受？若否，标记失控。
□ 互动（博弈论）：是否存在策略互依？若否，跳过 → 降级为统计描述。
□ 涌现（自组织）：三条件是否满足？若否，跳过 → 秩序不会自发涌现。
□ 跃迁（突变论）：是否有势函数？若否，跳过 → 改用统计物理。
□ 反思（元认知）：目标/模型/规则是否需要修正？若否，输出结论。
□ 迭代：若边界/目标改变，回到"界定"。
```

---

## 环节 1：界定（系统论）

```
System boundaries:
- Inside: [核心元素列表]
- Outside: [外部环境]

Network topology: [centralized / distributed / small-world / scale-free / hybrid]
- 关键连接模式：[描述主要信息流/控制流]

Hierarchical levels:
- Micro: [微观层级描述]
- Meso: [中观层级描述]
- Macro: [宏观层级描述]

Emergent properties: [整体具备而部分不具备的性质]
```

**边界不清晰时的处理**：
> 停止分析，向用户提出澄清问题："系统的核心边界应包含 X 还是 Y？"

---

## 环节 2：感知（信息论）

### 适用性检查
```
□ 可观测数据是否存在？
□ 噪音水平是否低于信道容量？
```

### 信息层
```
What is observed: [传感器/数据来源]
Uncertainty level: entropy H = [high / medium / low]
Signal quality: SNR | channel overload [yes / no]
Information value: mutual information I = [high / medium / low]
```

### 数据不足时的处理
> 声明："信息噪音超过信道容量，以下分析基于有限数据，置信度降低为 [low/medium]。"

---

## 环节 3：调节（一阶控制 + 二阶控制/元认知）

### 一阶控制
```
Target state: [具体可测目标 + 单位]
Current state: [实际测量值 + 单位]
Error signal: e = [target - actual]
Feedback type: [negative / positive / mixed]
Loop delay: [总延迟: sense→decide→act]
```

### 延迟过大时的处理
> 声明："控制延迟超过系统响应时间，一阶控制失效。转向博弈论或自组织分析。"

### 二阶控制（元认知检查点 1）
```
Goal appropriateness: [valid / needs revision + reason]
Model accuracy: [predicts well / deviation X%]
Strategy effectiveness: [working / failing + evidence]
Rule upgrade required: [yes / no + proposed change]
```

---

## 环节 4：互动（博弈论）

### 适用性检查
```
□ 是否存在 ≥2 个自主决策者？
□ 决策者之间是否存在策略互依？（一方的最优选择取决于另一方的选择）
□ 偏好是否可传递？
```

### 若适用
```
Players: [A, B, C...]
Objectives:
- A seeks: [goal]
- B seeks: [goal]

Strategy sets:
- A can: [S1, S2, S3...]
- B can: [S1, S2, S3...]

Payoff structure: [zero-sum / non-zero-sum / prisoner's dilemma / coordination]

Simplified payoff matrix (2×2):
           B-S1      B-S2
A-S1      (a,b)     (c,d)
A-S2      (e,f)     (g,h)

Nash equilibrium: [strategy combination]
Equilibrium stability: [stable / unstable / knife-edge + reason]
Repeated interaction: [yes / no → cooperation viable: yes / no]
Feedback to system: [how game outcomes affect control loops]
```

### 若不适用
> 声明："博弈论不适用：[具体原因]。降级为统计描述/行为观测。"

---

## 环节 5：涌现（自组织理论）

### 适用性检查（三条件）
```
□ Openness: continuous energy/information inflow [sufficient / insufficient]
□ Far-from-equilibrium: system in non-steady state [yes / no]
□ Nonlinear coupling: subsystem interactions amplify fluctuations [yes / no]
```

### 若三条件均满足
```
Order parameter(s): [描述集体秩序的宏观变量]

Self-organization timeline:
t0 (fluctuation): [small random perturbation]
t1 (amplification): [positive feedback mechanism activates]
t2 (competition): [multiple patterns compete for dominance]
t3 (enslaving): [winning pattern enslaves subsystems]
t4 (stabilization): [self-sustaining structure emerges]

Current stage: [t0 / t1 / t2 / t3 / t4]
Dominant mechanism: [specific positive feedback loop]
```

### 若条件不满足
> 声明："自组织条件不满足：[具体缺失条件]。秩序不会自发涌现，跳过此环节。"

---

## 环节 6：跃迁（突变论）

### 适用性检查
```
□ 系统是否可用势函数近似刻画？
□ 控制变量是否 ≤ 4 个？
□ 噪音是否未淹没突变信号？
```

### 若适用
```
□ Potential function exists: [yes / no]
□ Multiple stable states: [yes / no | count if yes]
□ Control parameters: [list 1-4 key variables]
□ Approaching criticality: [far / medium / near]

Early warning signals:
□ Critical slowing down: [yes / no + evidence]
□ Rising variance: [yes / no + evidence]
□ Increasing autocorrelation: [yes / no + evidence]
□ Flickering: [yes / no + evidence]

Critical parameter value: [estimated at X ± uncertainty]
Current parameter value: [measured at Y]
Safety margin: [Y - X] or [X / Y ratio]
Time to criticality: [estimate if approaching]

Risk level: 🟢 Green / 🟡 Yellow / 🟠 Orange / 🔴 Red

Post-transition states:
1. [New stable state A] (probability: high / medium / low | description)
2. [New stable state B] (probability: high / medium / low | description)

Reversibility: [yes / difficult / impossible]
Hysteresis: [yes / no]
```

### 若不适用
> 声明："突变论不适用：[具体原因]。改用统计物理/趋势外推描述临界现象。"

---

## 环节 7：反思（元认知检查点 2）

```
□ 步骤 1 的边界是否仍然合理？
□ 步骤 2 的感知是否足够支撑结论？
□ 步骤 3 的目标是否需要修正？
□ 跳过的理论是否确实不适用？
□ 是否需要回到步骤 1 重新界定？
```

若边界/目标/规则发生改变：
> 声明："元认知触发迭代：回到步骤 1，重新界定系统边界为 [新边界]。"

---

## 输出格式模板

```markdown
## [系统名称] 完整分析

### 执行摘要
[3-5 句：系统类型、当前阶段、关键发现、主要建议方向、风险等级]
[若处于混沌/临界区域，必须声明：以下预测为概率性而非确定性]

---

### 1. 系统边界与结构
[界定环节输出]

---

### 2. 信息与控制架构
[感知 + 调节环节输出]
[若信息不足：声明数据限制]
[若控制失效：声明转向其他分析]

---

### 3. 战略博弈分析
[若适用：互动环节输出]
[若跳过："博弈论不适用：[原因]。降级为统计描述。"]

---

### 4. 自组织动力学
[若适用：涌现环节输出]
[若跳过："自组织条件不满足：[原因]。秩序不会自发涌现。"]

---

### 5. 临界性与突变风险
[若适用：跃迁环节输出]
[若跳过："突变论不适用：[原因]。改用统计物理描述。"]

---

### 6. 综合建议
[时间尺度分层 + 反馈回路 + 干预建议 + 监控体系]

---

### 7. 局限性与不确定性
[假设 + 数据缺口 + 预测置信度 + 框架局限]
```

---

## 干预建议格式（含置信度声明）

每项干预必须附带：

```
🎯 High leverage / ⚙️ Medium leverage / 🔧 Low leverage:
Intervention: [具体动作]
Current problem: [问题描述]
Proposed change: [具体方案]
Expected outcome direction: [定性/概率性描述 + 时间尺度]
Confidence level: [high / medium / low]
Basis for confidence: [推理依据]
Risk: [潜在副作用]
```

**强制声明**：
> 若系统处于混沌区域或临界点附近："本预测为概率性方向判断，非精确数值预测。混沌动力学使长期精确预测不可能。"

---

## 质量检查清单（输出前自验）

```
□ 每个被应用的理论均满足其前提条件
□ 每个被跳过的理论均明确说明原因
□ ≥2 条反馈回路，含方向(+/-)与时间常数
□ ≥3 项可测指标，含当前值+预警阈值+检查频率
□ 所有机制已标注时间尺度
□ 干预已按杠杆排序，且附带置信度声明
□ 不确定性与假设已明确陈述
□ 若涉及混沌/临界区域，已声明预测的或然性
□ 元认知检查已完成（无未质疑的假设）
```
