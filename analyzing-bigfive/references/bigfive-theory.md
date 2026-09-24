# 大五人格理论综述与 BFI-2 分析规范（理论基石 spec）

> **读者**：LLM（本 skill 的执行者与维护者）。
> **定位**：本文件是 `analyzing-bigfive` 的**理论根**——回答"为什么这些规则成立"，以及"拿到 BFI-2 分数后，哪些分析在理论上被许可、哪些不被许可"。
> **不是**操作手册的替代：字段、模板、阈值落点、文案素材以 `scoring-interpretation.md`、`interpretation-library.md`、`writing-style.md`、`html-templates.md`、`couple-template.md` 为准。本文件给**判据与边界**，那些文件给**落点与措辞**。
> **分析框架（2 计算层 + 2 生成纪律 + 2 register）在 `SKILL.md`**——它是组织原则，必须住在 agent 必读的文件里，本文不再重复。

## Contents

- §0 本文档的用法与证据分级
- **Part I · 理论综述**
  - §1 五因素模型的来历
  - §2 结构：层级模型（domain → facet → item）
  - §3 五个维度逐一
  - §4 测量学：分数从哪来、能信到什么程度
  - §5 稳定性与可变性
  - §6 来源与跨文化
  - §7 效标关联：能预测什么、预测力多大
  - §8 批评与边界
- **Part II · 输入契约与可分析性**
  - §9 输入契约与计分模型
  - §10 可分析 / 不可分析清单
- **Part III · 理论 → 实现映射与幻觉防线**
  - §11 skill 规则的理论依据对照表
  - §12 常见幻觉与误用（⛔ 清单）
  - §13 参考文献

---

## 0. 本文档的用法与证据分级

### 0.1 为什么需要这份文档

历史教训（见 `docs/analyzing-bigfive-changelog.md` V5、V7）：本管线两次栽在"看起来合理、实际错误"上——一次是外部 AI 伪造的中国常模（40 个 M/SD 在原文零命中），一次是方向语言混用导致 180° 误读。两者的共同根源不是粗心，而是**缺少一个"什么是这个模型能说的、什么不是"的理论判据**。有了判据，模型就能在遇到"这个结论该不该写"时自查，而不是凭语感。

因此本文档承担三件事：

1. 给 LLM 一份**正确且不过时**的大五人格心智模型，减少即兴编造理论；
2. 给"BFI-2 分数能推出什么"一份**白名单 / 黑名单**（§10）；
3. 给 skill 每条规则一个**理论出处**（§11），使规则可追溯、可辩护、不轻易被绕过。

### 0.2 与其他文件的分工

| 层次 | 文件 | 回答的问题 |
|------|------|-----------|
| **Goal + Workflow** | `SKILL.md` | 分析框架、怎么一步步做 |
| **理论根（本文件）** | `bigfive-theory.md` | 为什么这么分析？哪些分析合法？边界在哪？ |
| 判据与规则 | `scoring-interpretation.md` | 方向怎么定、五档怎么切、常模怎么选 |
| 素材与措辞 | `interpretation-library.md`、`writing-style.md` | 落到哪句话、怎么说 |
| 结构落点 | `html-templates.md`、`couple-template.md`、`design-spec.md` | 放进哪一章、哪个字段 |
| 阈值（单一真相源） | `thresholds.json` | 扁平/矛盾/显著/双人的具体数值 |
| 数据与执行 | `bfi2_norms_cn.json`、`compute_scores.py`、`lint_report.py` | 数值怎么算、怎么验 |

**冲突裁决**：本文件与操作文件冲突时，**操作文件优先**（它是本机已定稿的事实源）；但若操作文件的某条与 Part I 的理论陈述直接矛盾，应视为操作文件的 bug 上报修订，而不是按本文件改数值。

### 0.3 证据分级约定（全文通用）

| 标记 | 含义 | 允许的措辞强度 |
|------|------|---------------|
| ✅ | 有明确文献/元分析支持的**群体水平**结论 | 可陈述为通用结论；**仍不得写成"研究证实你如何如何"** |
| ⚪ | 经验规则 / 本管线的工程约定 / 临床共识 | 只能说"通常/倾向于/可能"；不得挂"研究证明" |
| ⛔ | 理论上越界或证据不支持 | 禁止出现在任何产物中 |

**铁律（承自 changelog「铁律 1」）**：本文档的文献引用用于**理论定位**。凡要写进报告或进入计算的**具体数值**，必须来自本仓库已验证文件（`bfi2_norms_cn.json`、`thresholds.json`），不得从本文档的近似区间直接取用。

### 0.4 给 LLM 的三条硬约束

1. **量表边界**：BFI-2 是**自陈特质量表**，测的是"相对稳定的思维、情感、行为倾向"。它**不是**能力测验、不是诊断工具、不是类型测验。
2. **推断衰减**：所有"大五→生活结果"的证据都是**群体水平效应**（多为 |r| ≈ .1–.3）。把它套到**单个个体**上，预测力会衰减到接近噪声。故推演层一律软措辞。
3. **不可逆的错误**：方向错（第 4 域）与常模错（用错人群）是两个"静默 180° 错误"，不报错但结论全反。二者是本管线的最高优先级校验项。

---

# Part I · 理论综述

## 1. 五因素模型的来历

### 1.1 词汇学假设（lexical hypothesis）

现代大五的理论起点是一个经验假设而非先验公理：**人与人之间最重要的、最社会性的差异，最终会被语言编码成词**——因为社群需要这些词来谈论彼此。因此，从词典中系统提取人格描述词并做因素分析，就能逼近人格的"自然分类"。

- Allport & Odbert (1936)：从英语词典提取约 18,000 个人格相关词，分四类（特质、状态、评价、杂项），是最早的系统词表。✅
- Cattell (1943)：对词表做聚类与因素分析，得出 16 个因素（16PF）。✅

### 1.2 从 16 到 5：多次独立复现

关键转折是**"五"被反复独立地找出来**：

- Fiske (1949)：在教师评定数据中首次报告五个可复现的因素。✅
- Tupes & Christal (1961)：在美国空军样本中重复得到同样五个因素，并给出"五因素"的明确表述。✅
- Goldberg (1981, 1990)：在词汇学传统下系统复现，并推广了 **"Big Five"** 这一名称。✅

**方法论要点（LLM 须知）**："五"是**经验收敛**的结果——不同样本、不同词表、不同评定来源（自评/他评）反复得到近似结构。它不是从某个理论演绎出来的公理，因此**"为什么是五不是六/七"在经验层面有争论**（§8.3）。

### 1.3 两大传统的合流

- **词汇学/因素分析传统**：Goldberg、Digman 等，从词表出发。✅
- **问卷/临床传统**：Costa & McCrae 从 NEO 量表（1985 NEO-PI → 1992 NEO-PI-R）出发，独立收敛到同样的五维，并给出 E/N/O 的正式界定与六 facet/域的架构。✅

两条路线合流，使五因素模型在 1990 年代成为人格描述的主导框架（John et al., 2008）。✅

### 1.4 维度的命名之争（直接影响本管线）

同一维度常有多个名字，**名字不同暗示的内涵侧重不同**：

| 维度 | 常见别名 | 差异要点 |
|------|---------|---------|
| 外向性 E | Extraversion / Surgency / Positive Emotionality | 分歧小 |
| 宜人性 A | Agreeableness / Pleasantness / Accommodation | 分歧小 |
| 尽责性 C | Conscientiousness / Constraint / Dependability | 分歧小 |
| **情绪类** | Neuroticism / **Negative Emotionality** / Emotional Stability | 前两者是**负向**命名（高=更敏感）；"情绪稳定性"是**反向**命名（高=更平稳） |
| **开放类** | Openness to Experience / **Intellect** / **Open-Mindedness** / Culture | "Intellect"偏认知能力成分，"Open-Mindedness"偏经验开放与审美 |

**本管线的命名决策（规则见 `scoring-interpretation.md` §1、§1.3）**：

- BFI-2 官方用的就是 **Negative Emotionality**（负性情绪）与 **Open-Mindedness**（开放性）——这是 Soto & John (2017) 的刻意选择，用中性/正向命名降低量表的社会赞许压力。✅
- 报告对第 4 域统一改用**「情绪稳定性」**方向呈现（高=平稳），因为来访者视角下"稳定"是更自然、更少污名的说法；但**焦虑/抑郁/易变三个子维度保持本义方向**（高=更敏感）。
- ⛔ "神经质""负性情绪"不得出现在报告正文。

## 2. 结构：层级模型（domain → facet → item）

### 2.1 三层结构

大五不是"五个扁平分数"，而是**层级**结构：**item（条目）→ facet（子维度/侧面）→ domain（维度）**。这是本管线做"子维度矛盾分析"的全部理论依据。

- Costa & McCrae (1995)：NEO-PI-R 每域 6 个 facet。✅
- DeYoung, Quilty & Peterson (2007)：BFAS，每域 2 个 **aspect**（方面），发现 facet 层有可分离的稳定结构。✅
- Soto & John (2017)：BFI-2，每域 3 个 facet，共 15 个，是本管线所用的架构。✅

### 2.2 BFI-2 的 15 facet（本管线唯一架构）

| 维度（报告用名） | 官方名 | 子维度（报告用名） | 官方名 |
|---|---|---|---|
| 外向性 | Extraversion | 社交 / 果断 / 活力 | Sociability / Assertiveness / Energy Level |
| 宜人性 | Agreeableness | 同情 / 谦恭 / 信任 | Compassion / Respectfulness / Trust |
| 尽责性 | Conscientiousness | 条理 / 效率 / 负责 | Organization / Productiveness / Responsibility |
| 情绪稳定性 | Negative Emotionality（反向呈现） | 焦虑 / 抑郁 / 易变 | Anxiety / Depression / Emotional Volatility |
| 开放性 | Open-Mindedness | 好奇 / 审美 / 想象 | Intellectual Curiosity / Aesthetic Sensitivity / Creative Imagination |

**结构参数**：60 条目 = 15 facet × 4 条目 = 5 domain × 12 条目；每个 facet/domain 的正向题与反向题数量相等（各半）。这是 Soto & John (2017) 的设计特征，用于抑制默认同意倾向（§4.2）。✅

### 2.3 更上位：Big Two / meta-traits

维度之上还有更概括的两因子，理解它有助于解释"为什么某些跨维度组合特别常见"：

- Digman (1997)：五因素之上有两个高阶因子——**Alpha**（宜人性、尽责性、情绪稳定性的正向端）与 **Beta**（外向性、开放性）。✅
- DeYoung 等：对应命名为 **Stability** 与 **Plasticity**，并赋予适应性功能解释。✅

**对本管线的含义**：Alpha/Stability 类组合（如"宜人性高 + 尽责性高"）常表现为"社会化的稳定型"；Beta/Plasticity 类组合（如"外向性高 + 开放性高"）常表现为"探索/扩张型"。⚪ 这可以作为一个**解释性背景**，但**不要写进报告正文**（会引入术语），仅在咨询师备注或内部推理时使用。

### 2.4 facet 的可分离性 —— 矛盾分析的理论根

**核心命题**：domain 分数是 facet 分数的均值，**均值会掩盖内部差异**。一个 domain 分数"居中"的人，其三个 facet 完全可能一个远高、一个远低。

- 理论上：facet 承载的是比 domain 更窄、行为指向更具体的内容，二者的相关是"中等"而非"接近 1"；因此 facet 具有**增量效度**（在控制 domain 后仍能预测特定效标）。✅
- 经验上：Soto & John (2017) 与后续研究均支持 facet 层提供 domain 层之外的区分信息。✅

**因此**：`interpretation-library.md` §2 与 `scoring-interpretation.md` §3 的"同域子维度 z 极差 ≥ 2 时须专门分析"不是装饰性规则，而是**层级模型的直接推论**——只报 domain 等于丢掉一半信息。

## 3. 五个维度逐一

每维度给出：定义 → 三子维度 → 效标关联（带量级）→ 常见误解。
**日常画面与高低分含义见 `interpretation-library.md` §1**（本节不重复，只给理论骨架与证据）。

### 3.1 外向性 Extraversion

- **定义**：从外部世界（他人、活动、刺激）获取与消耗能量的倾向；含社交性、支配/果断、正性情绪与活跃水平。✅
- **子维度**：社交（sociability）、果断（assertiveness）、活力（energy level）。
- **效标**：正性情绪与主观幸福感、社会地位/领导涌现；与外向性正相关（元分析量级多为 |r| ≈ .2–.3）。✅
- **常见误解**：⛔ 把低外向读成"孤僻/有社交问题"。正确读法是"充电方式不同"。

### 3.2 宜人性 Agreeableness

- **定义**：人际取向上的合作、体贴、信任与谦逊程度。✅
- **子维度**：同情（compassion）、谦恭（respectfulness）、信任（trust）。
- **效标**：关系满意度、团队合作、他人评价；与关系质量正相关。⚠️ 另一面：极端高宜人性与"过度让步、被消耗、薪资谈判劣势"相关。⚪
- **常见误解**：⛔ 把低宜人性读成"人品差"；⛔ 把高宜人性读成"没有主见"（须结合果断子维度看）。

### 3.3 尽责性 Conscientiousness

- **定义**：目标导向行为中的自律、条理、可靠与坚持。✅
- **子维度**：条理（organization）、效率（productiveness）、负责（responsibility）。
- **效标**：**大五中对生活结果预测力最稳定的一个**——学业成绩、工作绩效、健康行为、寿命均相关（元分析 |r| 多为 .1–.3，学业与绩效约 .2 上下）。✅
- **常见误解**：⛔ 把低尽责读成"懒/不靠谱"；正确读法是"驱动方式不同"。

### 3.4 情绪稳定性 Emotional Stability（= 负性情绪的反向）

- **定义**：体验焦虑、抑郁、易怒与情绪波动的倾向。**本管线以反向呈现**：得分高 = 情绪平稳。✅
- **子维度**：焦虑、抑郁、易变（**保持本义方向：高 = 更敏感**）。
- **效标**：**大五中对主观幸福感与心理健康预测力最强的维度**（与生活满意度负相关、量级常为各维度中最大）。✅
- **常见误解**：⛔ 把低稳定性读成"情绪有问题/不稳定"；本管线统一措辞为"对压力接收得更清楚/更灵敏"（`writing-style.md` §8）。⛔ 把高焦虑/高抑郁子维度读成"有焦虑症/抑郁症倾向"——**量表不是诊断**（§8.5）。

### 3.5 开放性 Open-Mindedness

- **定义**：对观念、审美、想象与新经验的接受与欣赏程度。✅
- **子维度**：好奇（intellectual curiosity）、审美（aesthetic sensitivity）、想象（creative imagination）。
- **效标**：创造性表现、政治/价值取向偏自由、教育与艺术参与；预测力较分散、量级偏小。✅
- **常见误解**：⛔ 把开放性等同于智力/聪明（相关但不等同）；⛔ 把低开放读成"没文化/保守落后"——中性描述是"偏好熟悉与实际"。

## 4. 测量学：分数从哪来、能信到什么程度

### 4.1 自陈量表与李克特计分

BFI-2 用 5 点李克特（1 非常不同意 … 5 非常同意）。维度分 = 相关条目（反向题转换后）的**算术平均**，落在 1–5。这是**等距假设下的近似连续量**，用于比较与求 z 是标准做法。✅

### 4.2 反向题与默认同意倾向（acquiescence）

- **默认同意倾向**：有些人倾向于对所有陈述都说"同意"，这会系统性抬高其所有分数。✅
- **反向题**：以否定措辞表述的条目（如"比较懒""缺乏条理"），计分时按 `6 − 原始分` 转换。其作用是抵消默认同意倾向、并打断固定作答模式。✅
- **代价**：反向题需要额外的语义转换（"不同意'我很懒'"= 我很勤快），**阅读负担更高**。Zhang et al. (2022) 在中国四样本中发现：**反向题与部分 facet 在高学历被试中功能更好，在低学历被试中交叉载荷升高、主载荷下降**；物质滥用临床样本中尤甚。✅

**对本管线的含义（规则见 `scoring-interpretation.md` §4.4）**：
- 低学历/高风险/监督性施测的来访者 → **只做维度层解释，子维度解释需谨慎**；
- 建模反向题因子/默认同意因子能显著改善拟合，说明"默认同意"是真实存在的干扰源——**不要把子维度的细小差异当作实质发现**。⚪

### 4.3 信度

- **内部一致性（Cronbach's α）**：BFI-2 英文版 domain α ≈ .83–.91，facet α 平均偏低（约 .66–.87 区间）。✅
- **中国版实测**（Zhang et al., 2022）：大学生/在职成人 **domain α ≈ .83–.90，facet α ≈ .66–.85**；青少年样本 facet α 偏低（如求知欲 .39、谦恭 .47）。✅ ← **此为本管线常模文件所依据的已验证数值**
- **重测信度**：3 个月间隔，青少年样本 domain 约 .70–.80。✅

**含义**：domain 层可靠度高，适合逐人解释；**facet 层可靠度随样本下降**，青少年尤其如此 → 青少年来访者以维度层为主（`scoring-interpretation.md` §4.1）。

### 4.4 效度

- **结构效度**：五因素 + 15 facet 的层级结构在多种语言与文化下可复现。中美因子载荷模型一致性系数 **0.87–0.97**（Zhang et al., 2022）。✅
- **收敛/区分效度**：中文 BFI-2 与其他大五量表对应维度相关 **0.87–0.94**。✅
- **效标效度**：domain 层对多类生活结果有稳定关联（§7）。✅

### 4.5 常模与 z 分：相对位置的含义

- **原始分本身不可直接解读**："尽责性 3.3" 说明不了什么，除非知道"同群体平均是多少"。✅
- **常模（norms）**：参照群体的 M 与 SD。**z = (原始分 − M) / SD**，表示"偏离群体均值多少个标准差"；**百分位 pct = Φ(z)×100**，表示"低于你的人数比例"。✅
- **常模选择决定结论**：同一原始分在不同常模下 z 可以差很多。中国样本 SD 系统性小于美国样本（作答更保守、更少选极端项），故"±1 SD"在两套常模下的含义并不等值。✅ ⚪
- **本管线纪律**：常模为**内置单一数据源**（`bfi2_norms_cn.json`），输入自带的 z/等级/M/SD **一律忽略**（可能来自其他常模或工具）。

### 4.6 单次测量的误差

分数 = 真分数 + 误差。误差来源至少四类：条目抽样、当天状态（心情/疲劳）、作答风格（默认同意/极端）、情境（施测方式）。✅

**含义**：**单次测量的边界差异不应被过度解读**。这正是本管线设"阈值边界敏感项"（pct 靠近档位切分点时在咨询师备注中标注）的原因——它是测量误差在工程上的诚实表达。⚪

## 5. 稳定性与可变性

### 5.1 rank-order 稳定性 vs mean-level 变化

两个必须区分的概念：

- **rank-order 稳定性**（个体在群体中的排序是否稳定）：随年龄上升，儿童期偏低，成年后升高（成年中期可到 .7 上下）。✅
- **mean-level 变化**（群体平均分是否随年龄移动）：存在系统趋势——**成熟原则（maturity principle）**：随年龄增长，宜人性与尽责性平均升高、情绪稳定性升高（负性情绪降低）。✅（Roberts et al., 2006；Bleidorn et al., 2019）

**含义**：特质**既稳定又可变**。"稳定"指排序，"可变"指水平。故报告应说"当前快照"，而非"终身判决"。

### 5.2 特质是密度分布，不是固定行为

- Fleeson (2001)：个体的状态（states）围绕其特质均值形成**密度分布**——特质是分布的均值，不是每次行为都等于均值。✅
- Mischel & Shoda (1995)：**if-then 情境签名**——同一个人在"被批评"与"被表扬"情境下可以判若两人。✅
- Mischel (1968) 的情境主义批评：单次行为的跨情境一致性远低于直觉。✅

**含义**：⛔ 不得写"你一定会……"；✅ 应写"在……情况下，你倾向于……"。这是 `writing-style.md` R3（推测标记）的理论依据。

### 5.3 可改变性

- 人格特质在成年期仍可改变，且**有意干预可产生小而持久的变化**（数周干预可带来约 0.2 SD 量级的移动，随干预强度与持续时间增长）。✅ ⚪
- 生活角色转换（新工作、稳定伴侣关系）与特质变化相关。✅

**含义**：成长建议章的"可试的小动作"框架在理论上是站得住的——它对应"小步、可持续、可退回"的干预逻辑。但**不得承诺改变量或时间表**（个体差异极大）。

### 5.4 对解读的含义（三条）

1. 分数是**当前快照**，不是本性标签；
2. 分数是**分布均值**，不是行为承诺；
3. 分数**可被有意影响**，故"成长"章不是安慰话术。

## 6. 来源与跨文化

### 6.1 行为遗传学：约 40–50% 遗传度

- 双生子研究一致显示：大五各维度的遗传度约 **40–50%**，非共享环境贡献独特方差，共享环境贡献很小。✅（Polderman et al., 2015；Vukasović & Bratko, 2015）
- **关键限定**：遗传度是**群体统计量**，不是个体命运。⛔ 不得表述为"你天生如此/改不了"。遗传度也随环境变异范围变化。

### 6.2 文化普遍性与参照群体效应

- 五因素结构在多数文化中可复现（McCrae & Costa 等跨文化研究）。✅
- **参照群体效应（reference group effect）**：自陈量表要求被试在内心选一个参照群体来定位自己；不同文化的参照群体不同，导致**跨文化的均值比较方向与大小都不确定**。✅（Heine et al., 2002）
- 相关现象：**国家刻板印象与实测人格的对应很弱**（Terracciano et al., 2005）——即"某国人更外向"这类说法通常缺乏实测支持。✅

**含义**：**不做跨文化的绝对高低判断**。本管线的常模层只回答"相对**所选定人群**的位置"，并在报告 01 章注明常模人群、提示可切换常模重算（`scoring-interpretation.md` §4.2）。

### 6.3 中国样本的特殊性（本管线直接相关）

| 现象 | 证据 | 工程后果 |
|------|------|---------|
| 作答更保守，SD 系统性小于美国样本 | 中国两样本 SD ≈ 0.66–0.70 vs 美国 0.75–0.88 ✅ | 中国常模下 z 的"±1"边界含义与美常模不同；判档以中国常模为准 |
| 反向题对低学历被试更困难 | Zhang et al. (2022) ✅ | 低学历来访者降为维度层解释 |
| 监督性/纸笔施测偏差（尽责性易高估、情绪敏感性易低估） | 物质滥用样本表现 ✅ | 若数据来自此类施测，须在咨询师备注中降权 |
| 便利样本、非全国代表、无分性别/年龄段常模 | `bfi2_norms_cn.json` metadata ✅ | 报告须声明样本局限 |

**社会赞许性**：自陈量表普遍受社会赞许影响，中国样本中更需留意（尤其在受监督施测时）。✅ 本管线以"全维度同向 |z|>1 → 备注警告社会赞许性"作为工程化的检测手段。⚪

## 7. 效标关联：能预测什么、预测力多大

### 7.1 总原则：真实但适度

Roberts et al. (2007) 的核心结论：人格特质对重要生活结果的预测力**与社经地位、认知能力处于同一量级**。✅

但必须同时记住量级：**多数效标关联 |r| ≈ .1–.3**（即解释方差约 1%–9%）。✅

**因此**：
- ✅ 可以说"这个特质与这类结果**在群体层面**有关联"；
- ⛔ 不能说"你的分数**决定了**你会怎样"；
- ⛔ 不能从群体 r 反推个体概率（个体预测力远低于群体 r 暗示的水平）。

### 7.2 分领域证据（均为群体水平）

| 领域 | 主要相关维度 | 方向 | 量级 |
|------|------------|------|------|
| 学业成绩 | 尽责性（最强）、开放性 | 正 | \|r\| ≈ .2 上下 ✅ |
| 工作绩效 | 尽责性（最强）、情绪稳定性 | 正 | \|r\| ≈ .2–.3 ✅ |
| 主观幸福感/生活满意度 | 情绪稳定性（最强，负向）、外向性、尽责性 | 情绪敏感负、外/尽正 | 情绪类 \|r\| 可达 .3–.4 ✅ |
| 心理健康/躯体健康 | 情绪稳定性、尽责性 | 稳定/尽责为正 | 小到中等 ✅ |
| 关系满意度 | 宜人性、情绪稳定性、低神经质 | — | 小到中等 ✅ |
| 死亡率/寿命 | 尽责性 | 正（尽责者更长寿） | 小 ✅ |
| 创造性表现 | 开放性 | 正 | 小到中等 ✅ |

（来源：Strickhouser et al., 2017；Jokela et al., 2013；Anglim et al., 2020；Poropat, 2009；Judge et al., 1999；Ozer & Benet-Martínez, 2006 等；数值为量级近似，**取用须回原文**。）

### 7.3 增量效度与 facet

- facet 在控制 domain 后仍有增量效度（能预测 domain 预测不到的特定效标）。✅ → 支持本管线做子维度层分析。
- 但**增量通常不大**，且随样本衰减。⚪ → 支持"不硬凑组合卡"的数量诚实原则。

### 7.4 自评 vs 他评

- Vazire (2010) 的 **SOKA 模型**：自评在他评不可见的**内部经验**（如焦虑、想法）上更准；他评在**外部可见、评价性**的特质上更准（如智力、吸引力、支配性）。✅
- **含义**：BFI-2 自陈在"焦虑/抑郁/想象"等内部特质上有信息优势，在"果断/活力/条理"等外部可见特质上可能有盲区。⚪ → 这是报告在敏感子维度（尤其情绪类）措辞谨慎、并在咨询师备注提示"会谈核实"的理论依据。

## 8. 批评与边界

### 8.1 描述性框架，非解释性理论

大五是**描述性分类学**（"有哪些差异"），不是**因果解释**（"为什么会有这些差异"）。✅
**含义**：⛔ 不得把"因为你有高 X 特质"当作行为的原因解释；只能表述为"与……一致的倾向"。

### 8.2 不是类型学

大五是**连续维度**，不存在"你属于某一型"。✅
**含义**：⛔ 禁止 MBTI 式的四字母/类型标签；⛔ 禁止"你是典型的 X 型人格"。封面 chips（`interpretation-library.md` §6）是**画像白描**，不是类型判定——它必须随分数连续变化，不得退化为固定类型名。

### 8.3 维度数目的争论

- **HEXACO**（Ashton & Lee, 2007）：在五因素之外识别出独立的第六因素 **Honesty-Humility**（诚实-谦逊），主张六因素更完整。✅
- 其他方案（如 3 因素 Eysenck、7 因素等）也存在。✅
**含义**：五因素不是"唯一正确"，而是**当前最主流、且有 BFI-2 这种成熟工具**的方案。本管线**不引入第六因素**，但宜人性/谦恭相关的解读可借鉴 HEXACO 对"诚实-谦逊"的强调。⚪

### 8.4 自陈偏差与 WEIRD 偏差

- 自陈受社会赞许、自我认识盲区、作答风格影响（§4.2、§7.4）。✅
- 大量证据来自 WEIRD 人群；非 WEIRD 的验证长期不足（这正是 Zhang et al., 2022 的动机）。✅
**含义**：报告须声明"自陈量表 + 便利样本"的双重局限（模板固定块已覆盖）。

### 8.5 ⛔ 明确不能做的（与 `SKILL.md` Out of scope 对应）

| 不能做 | 理由 |
|--------|------|
| 心理诊断（焦虑症/抑郁症/人格障碍） | 特质量表不是诊断工具；高焦虑子维度 ≠ 焦虑障碍 |
| 治疗建议 | 超出本 skill 目的；情绪困扰只走模板固定求助 callout |
| 高利害决策（招聘/选拔/晋升） | 个体预测力不足 + 伦理风险 |
| 职业决策结论 | 无职业常模、无本地效标数据；只能在对话中给"倾向参考" |
| 双人匹配分 / "合不合"判断 | 无匹配常模、无本地效标；且无证据支持"人格匹配度"的预测效力 |
| 预测具体行为/事件 | 群体效应量 ≠ 个体预测（§7.1） |
| 跨文化绝对高低判断 | 参照群体效应（§6.2） |

---

# Part II · 输入契约与可分析性

## 9. 输入契约与计分模型

### 9.1 输入形态

- **来源**：来访者在 `bfi2_interactive.html`（或等价计分平台）完成 60 题作答，页面「复制分数」输出 **20 行制表符分隔的原始分**（5 维度 + 15 子维度，1–5 刻度）；或导出 JSON（含 `scores.stability` 与 `scores.raw`）。
- **本 skill 只收原始分**（可附年龄、关系背景）。
- 输入中若带 z / 等级 / M / SD 列 → **一律忽略**（§4.5）。

### 9.2 计分链（唯一执行器：`scripts/compute_scores.py`）

```
原始分(1–5)  →  [反向题: 6 − x]  →  条目均值 = score  →  z = (score − M)/SD  →  pct = Φ(z)×100  →  band  →  tick
                 (§4.2)             (§4.1)               (§4.5)                (§4.5)            (thresholds.json)
```

**禁止手算**：所有派生值必须来自脚本输出，lint 复算比对（`SKILL.md` Stop rules「数值不手算」）。

### 9.3 方向约定（理论理由见 §1.4；**规则权威在 `scoring-interpretation.md` §1.2/§1.3**）

| 层 | 方向 | 理由 |
|----|------|------|
| 第 4 域（维度层） | **情绪稳定性**（高 = 平稳） | 来访者视角更自然、少污名；对应 `6 − 负性情绪分`，`M' = 6 − M`，z 取反 |
| 焦虑/抑郁/易变（子维度层） | **本义**（高 = 更敏感） | 三者的日常语义就是"越敏感"；翻转会造成"焦虑高 = 情绪好"的荒谬读法 |

**这是本管线最高优先级的校验项**：方向错 = 雷达/游标/正文 180° 反转，且不报错（历史案例见 changelog V7）。

### 9.4 常模选择

内置三套中国常模（Zhang et al., 2022 Table 1），按来访者身份就近选择；**在读身份优先于年龄**；青少年常模仅维度层稳妥。规则见 `scoring-interpretation.md` §4.1。

## 10. 可分析 / 不可分析清单

> 分析框架（2 计算层 L1/L2 + 2 生成纪律 L3/L4 + 2 register）见 `SKILL.md`。本节是**逐项白名单 / 黑名单**。

### 10.1 ✅ 可以分析（在给定边界内）

| # | 可分析项 | 层次 | 措辞强度 |
|---|---------|------|---------|
| 1 | 各条目相对常模人群的位置（z/pct/档） | L1 | 可陈述（带常模声明） |
| 2 | 个体的内部相对强弱格局（最突出/最靠后） | L2 | 可陈述 |
| 3 | 同域子维度的不一致（矛盾维度） | L2 | 可陈述（须点名极差） |
| 4 | 跨条目组合的优势与代价 | L3 | "可能/倾向于" |
| 5 | 敏感子维度的方向性描述 | L1/L2 | 换向措辞（"接收得更清楚"） |
| 6 | 情境化的行为倾向画面 | L4 | "可能/常常/容易" |
| 7 | 可试的成长小动作（不承诺效果） | L4 | "可以试试" |
| 8 | 双人差异的翻译与协商选项 | L5 | 对称、双面 |

### 10.2 ⛔ 不可以分析（无论用户怎么问）

| # | 不可分析项 | 理由 |
|---|-----------|------|
| 1 | 心理诊断 / 障碍判断 | §8.5 |
| 2 | 类型标签（"你是 X 型"） | §8.2 |
| 3 | 具体行为的预测 / 事件概率 | §7.1、§5.2 |
| 4 | 能力 / 智力判断 | §3.5、§8.1 |
| 5 | 高利害决策建议 | §8.5 |
| 6 | 职业决策结论 | §8.5 |
| 7 | 双人匹配分 / 关系判决 | §8.5 |
| 8 | 跨文化绝对高低判断 | §6.2 |
| 9 | 分数与价值挂钩（"好/差"） | §8.1、`writing-style.md` §8 |
| 10 | 编造机制解释（"因为你的 X 神经回路…"） | §8.1；`SKILL.md` Stop rules「原理字段来源」 |
| 11 | 引用未经核验的具体数值/文献 | 铁律 1（§0.3） |

---

# Part III · 理论 → 实现映射与幻觉防线

## 11. skill 规则的理论依据对照表

供 LLM 在被质疑或想绕过规则时查阅——**每条规则都有理论根，不是任意约定**。

| skill 规则 | 理论依据 | 出处 |
|-----------|---------|------|
| 第 4 域统一「情绪稳定性」方向 | 命名与内涵差异；来访者视角少污名 | §1.4 |
| 焦虑/抑郁/易变保持本义不翻转 | 翻转会造成"焦虑高=情绪好"的荒谬读法 | §1.4、§9.3 |
| 必须做子维度层分析（矛盾分析） | facet 可分离性；domain 均值掩盖差异 | §2.4 |
| 双层解读（常模层 + 自比层） | L1 与 L2 是正交的两把尺子 | §4.5、`SKILL.md` 框架节 |
| 五档切分 + 档位标签必须与 pct 一致 | 常模定位是 L1 的唯一合法输出形式 | §4.5 |
| 不硬凑组合卡（数量由分布决定） | facet 增量效度有限；组合效应随样本衰减 | §7.3 |
| 一律软措辞（可能/倾向于） | 特质是密度分布 + if-then 情境性 | §5.2 |
| 不写"研究证实你如何" | 效标关联是群体效应量，非个体预测 | §7.1 |
| 情绪敏感用"接收得更清楚" | 自陈在内部特质上有信息优势但非诊断 | §7.4、§8.5 |
| 阈值边界项在备注中标注 | 单次测量的误差边界 | §4.6 |
| 扁平剖面走降级策略 | 剖面平本身就是信息；不硬找张力 | §7.3、`interpretation-library.md` §7 |
| 青少年/低学历降为维度层 | facet 信度随样本下降；反向题难度 | §4.2、§4.3、§6.3 |
| 不做诊断/高利害/职业结论 | 描述性框架 + 个体预测力不足 | §8.1、§8.5 |
| 双人不评匹配分 | 人格相似度缺乏可靠预测效力的证据 | §8.5 |
| 不做跨文化绝对判断 | 参照群体效应 | §6.2 |
| 常模内置、输入自带 z 一律忽略 | 常模选择决定结论；外部值不可核验 | §4.5、铁律 1 |
| 成长建议"可试、可退回"、不承诺效果 | 干预可产生小而持久变化，个体差异大 | §5.3 |

## 12. 常见幻觉与误用（⛔ 清单）

历史与本管线最易犯的错误，逐条列出以供自查：

1. **编造常模**：把外部来源的 M/SD 直接入库。→ 必须对回原文页码/表号（changelog V5 教训）。
2. **方向混用**：同一数字同时用"焦虑高"和"稳定性低"两套语言。→ 一套语言（§9.3）。
3. **静默翻转**：收到负性方向输入不确认就翻转。→ 必须先回显确认。
4. **诊断化**：把高焦虑/高抑郁子维度读成"有焦虑/抑郁倾向"。→ 量表不是诊断（§8.5）。
5. **类型化**：把画像 chips 写成固定类型名（"你是 INTJ 式的人"）。→ 连续维度，非类型（§8.2）。
6. **群体效应量个体化**：用"尽责性预测学业成绩"推出"你成绩会好"。→ 个体预测力不足（§7.1）。
7. **伪引用**：写"研究证实你的 X 导致 Y"。→ 只能陈述通用结论，且不指向个体（§7.1）。
8. **编造机制**：即兴编造"因为你的 X 神经机制…"。→ 机制句只允许库内既有原理句（`SKILL.md` Stop rules）。
9. **数值手算/手填**：绕过 `compute_scores.py`。→ lint 复算即 FAIL。
10. **跨文化绝对判断**：写"你在中国人中偏高"。→ 参照群体效应（§6.2）。
11. **价值挂钩**：把"得分靠后"写成"这方面比较差"。→ 分数与价值脱钩（`writing-style.md` §8）。
12. **照搬样例**：句式复用但措辞未变。→ R7。
13. **阈值凭记忆**：不查 `thresholds.json` 就按印象写"|z| 超过 0.5 算扁平"。→ 阈值单一真相源，写错不报错。

## 13. 参考文献

> 用于理论定位。**具体数值取用须回原文**（铁律 1）。本管线已验证的数据源为 `bfi2_norms_cn.json`（Zhang et al., 2022 Table 1）与 `thresholds.json`。

**量表与结构**
- Soto, C. J., & John, O. P. (2017). The next Big Five Inventory (BFI-2): Developing and assessing a hierarchical model with 15 facets to enhance bandwidth, fidelity, and predictive power. *Journal of Personality and Social Psychology, 113*(2), 117–143.
- Zhang, B., Li, Y. M., Li, J., Luo, J., Ye, Y., Yin, L., Chen, Z., Soto, C. J., & John, O. P. (2022). The Big Five Inventory-2 in China: A comprehensive psychometric evaluation in four diverse samples. *Assessment, 29*(6), 1262–1284.
- Costa, P. T., & McCrae, R. R. (1992). *Revised NEO Personality Inventory (NEO-PI-R) and NEO Five-Factor Inventory (NEO-FFI) professional manual.* PAR.
- DeYoung, C. G., Quilty, L. C., & Peterson, J. B. (2007). Between facets and domains: 10 aspects of the Big Five. *Journal of Personality and Social Psychology, 93*(5), 880–896.
- John, O. P., Naumann, L. P., & Soto, C. J. (2008). Paradigm shift to the integrative Big Five trait taxonomy. In *Handbook of personality: Theory and research* (3rd ed.).

**历史与词汇学**
- Allport, G. W., & Odbert, H. S. (1936). Trait-names: A psycho-lexical study. *Psychological Monographs, 47*(1).
- Cattell, R. B. (1943). The description of personality: Basic traits resolved into clusters. *Journal of Abnormal and Social Psychology, 38*(4), 476–506.
- Fiske, D. W. (1949). Consistency of the factorial structures of personality ratings from different sources. *Journal of Abnormal and Social Psychology, 44*(3), 329–344.
- Tupes, E. C., & Christal, R. E. (1961). Recurrent personality factors based on trait ratings. *USAF ASD Technical Report*.
- Goldberg, L. R. (1990). An alternative "description of personality": The Big-Five factor structure. *Journal of Personality and Social Psychology, 59*(6), 1216–1229.

**高阶结构与批评**
- Digman, J. M. (1997). Higher-order factors of the Big Five. *Journal of Personality and Social Psychology, 73*(6), 1246–1256.
- Ashton, M. C., & Lee, K. (2007). Empirical, theoretical, and practical advantages of the HEXACO model of personality structure. *Personality and Social Psychology Review, 11*(2), 150–166.
- Mischel, W. (1968). *Personality and assessment.* Wiley.

**稳定性与可变性**
- Roberts, B. W., Walton, K. E., & Viechtbauer, W. (2006). Patterns of mean-level change in personality traits across the life course. *Psychological Bulletin, 132*(1), 1–25.
- Bleidorn, W., et al. (2019). Personality maturation around the world. *Psychological Science, 30*(4).
- Fleeson, W. (2001). Toward a structure- and process-integrated view of personality: Traits as density distributions of states. *Journal of Personality and Social Psychology, 80*(6), 1011–1027.
- Mischel, W., & Shoda, Y. (1995). A cognitive-affective system theory of personality. *Psychological Review, 102*(2), 246–268.

**遗传与环境**
- Polderman, T. J. C., et al. (2015). Meta-analysis of the heritability of human traits based on fifty years of twin studies. *Nature Genetics, 47*(7), 702–709.
- Vukasović, T., & Bratko, D. (2015). Heritability of personality: A meta-analysis of behavior genetic studies. *Psychological Bulletin, 141*(4), 769–785.

**效标关联**
- Roberts, B. W., Kuncel, N. R., Shiner, R., Caspi, A., & Goldberg, L. R. (2007). The power of personality: The comparative validity of personality traits, socioeconomic status, and cognitive ability for predicting important life outcomes. *Perspectives on Psychological Science, 2*(4), 313–345.
- Ozer, D. J., & Benet-Martínez, V. (2006). Personality and the prediction of consequential outcomes. *Annual Review of Psychology, 57*, 401–421.
- Poropat, A. E. (2009). A meta-analysis of the five-factor model of personality and academic performance. *Psychological Bulletin, 135*(2), 322–338.
- Judge, T. A., Higgins, C. A., Thoresen, C. J., & Barrick, M. R. (1999). The Big Five personality traits, general mental ability, and career success. *Personnel Psychology, 52*(3), 621–652.
- Strickhouser, J. E., Zell, E., & Krizan, Z. (2017). Does personality predict health and well-being? A metasynthesis. *Health Psychology, 36*(8), 797–810.
- Jokela, M., et al. (2013). Personality and all-cause mortality. *Psychological Science, 24*(11), 2153–2160.
- Anglim, J., et al. (2020). Predicting psychological and subjective well-being from personality: A meta-analysis. *Psychological Bulletin, 146*(4), 279–323.

**跨文化与自评偏差**
- Heine, S. J., Lehman, D. R., Peng, K., & Greenholtz, J. (2002). What's wrong with cross-cultural comparisons of subjective Likert scales? The reference-group effect. *Journal of Personality and Social Psychology, 82*(6), 903–918.
- Terracciano, A., et al. (2005). National character does not reflect mean personality trait levels in 49 cultures. *Science, 310*(5745), 96–100.
- Vazire, S. (2010). Who knows what about a person? The self–other knowledge asymmetry (SOKA) model. *Journal of Personality and Social Psychology, 98*(2), 281–300.
- McCrae, R. R., & Costa, P. T. (1997). Personality trait structure as a human universal. *American Psychologist, 52*(5), 509–516.
