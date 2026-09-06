# cognitive-functions 视觉与语言改造 实施计划

> **For agentic workers:** 本计划按任务派发子代理执行（Agent tool，每任务一个新子代理），执行者先读 `docs/2026-09-06-reskin-design.md`（spec，唯一设计事实源）。步骤用 checkbox（`- [ ]`）跟踪。
> **版本管理替代**：本目录非 git 仓库——Task 1 的备份目录充当回退点，不执行 git commit。

**Goal:** 把 analyzing-cognitive-functions 的报告视觉与语言对齐 bigfive 已定稿的 A 纸感书卷系（视觉）+ writing-style §10（语言），规则文件/lint/基线样例同步落地，最后用真实分数（qqc）首秀验收。

**Architecture:** 纯规则层改造——不改输入解析、计分算法、双人动力学规则与得分 JSON；`html-templates.md`（视觉）与 `writing-style.md`（语言）为两大改写主体，`lint_report.py` 与 `examples/mbti_sample.html` 是防回退的两件套（lint 升级 ↔ 样例回归互证），SKILL.md 与 attachment-inference.md 做联动小改。

**Tech Stack:** Markdown 规则文件、Python 3 标准库（lint）、无依赖内联 SVG/CSS（报告 HTML）、Git Bash 环境。

**参照文件（执行者必读，路径均为绝对路径）：**
- Spec：`C:\Users\elliot\.zcode\skills\analyzing-cognitive-functions\docs\2026-09-06-reskin-design.md`
- 视觉逐字源：`C:\Users\elliot\.zcode\skills\analyzing-bigfive\examples\bfi2_sample.html`（`<style>` 块）
- 设计系统：`C:\Users\elliot\.zcode\skills\analyzing-bigfive\references\html-templates.md`
- 语言规则源：`C:\Users\elliot\.zcode\skills\analyzing-bigfive\references\writing-style.md` §10

---

### Task 1: 备份现有文件（回退点）

**Files:**
- Create: `examples/backup-2026-09-06/`（复制 6 个文件进去）

- [ ] **Step 1: 建备份目录并复制**

```bash
cd "C:\Users\elliot\.zcode\skills\analyzing-cognitive-functions" && mkdir -p examples/backup-2026-09-06 && cp SKILL.md references/html-templates.md references/writing-style.md references/attachment-inference.md scripts/lint_report.py examples/backup-2026-09-06/
```

- [ ] **Step 2: 验证**

Run: `ls examples/backup-2026-09-06`
Expected: 6 个文件（SKILL.md、html-templates.md、writing-style.md、attachment-inference.md、lint_report.py——5 个文件；若把 `__pycache__` 排除后不足 5 个则重拷）。

---

### Task 2: 升级 lint_report.py（先于样例，TDD：新检查先写，Task 6 让它变绿）

**Files:**
- Modify: `scripts/lint_report.py`（整文件替换为下述源码）

- [ ] **Step 1: 用以下完整源码覆盖 `scripts/lint_report.py`**

```python
#!/usr/bin/env python3
"""lint_report.py — 校验 analyzing-cognitive-functions 生成的报告 HTML 是否符合规范。

用法: python3 scripts/lint_report.py <报告文件.html>
退出码: 0 = 全部通过; 1 = 存在 FAIL; 2 = 文件/参数错误

检查项: 正文裸功能代码 / 禁用词（含统计措辞）/ 固定文本块 / 证据标签 /
A 纸感样式（@page A4、纸纹不打印、正文 680px、已取消视觉件不回流）/
结构件（chapter-head、pull 锐评、epigraph 题记、combo-card、定位条）/
速览卡 / 打印样式 / 双人报告专项（非预测承诺 + 伦理声明；双人跳过单人口径计数）
2026-09-06 视觉改造：移除谦卑段落必查（已取消，原句列入禁用词）。
"""
import re
import sys
from pathlib import Path

FUNCTION_CODES = ["Fi", "Ni", "Fe", "Ti", "Te", "Ne", "Se", "Si"]

# 正文禁用词（可选阅读附录 .appendix-tech 内不检查 Beebe 术语，其余全局检查）
FORBIDDEN_BODY = ["劣势功能", "主导功能", "Fi-Ni loop", "Fi-Ni Loop", "阴影功能",
                  "结构性情感失语", "病态", "缺陷",
                  # 已弃用的比喻命名
                  "价值罗盘", "情绪天线", "逻辑拆解器", "效率引擎",
                  "长线望远镜", "可能性喷泉", "安全基地", "当下雷达",
                  # 工程/IT/系统类（writing-style.md §4.5）
                  "系统", "架构", "机制", "流程", "输入", "输出", "通道", "带宽", "负载",
                  "算法", "迭代", "反馈", "模块", "组件", "审查", "监控", "容器", "支架",
                  "空转", "宕机", "重启", "调试", "程序", "数据库", "接口", "回路", "闭环",
                  "触发器", "运算", "处理器", "默认设置", "双核", "双引擎",
                  # 心理学术语（R7 术语零容忍的兜底，见 writing-style.md §6）
                  "认知功能", "心理功能", "感觉功能", "判断功能", "功能栈", "功能结构",
                  "意识位置", "在场感", "叙事", "价值标准", "价值判断", "内在安抚",
                  "自洽", "感官体验", "感官投入", "收拢",
                  # 报告正文禁止的外部关系导向
                  "咨询师", "会谈", "咨询中",
                  # 统计措辞（"不是统计概率"在扫描前豁免，见 main 中的替换）
                  "显著", "证实", "证明", "概率"]
# 任何位置都禁止（含附录；神经质为整体不涉及；谦卑段落已取消 2026-09-06）
FORBIDDEN_GLOBAL = ["你就是太", "你一定会", "你肯定会", "神经质", "情绪稳定性", "必然",
                    "以你的经历为准"]
# 已取消的视觉件（红线：勿生成）
FORBIDDEN_CSS = ["prog-bar", "first-letter"]

REQUIRED_BLOCKS = {
    "阅读指南": "怎么读这份报告",
    "局限声明": "不构成临床诊断",
}


def strip_regions(html: str, patterns) -> str:
    for pat in patterns:
        html = re.sub(pat, " ", html, flags=re.DOTALL | re.IGNORECASE)
    return html


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: python3 lint_report.py <报告文件.html>")
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"错误: 文件不存在: {path}")
        return 2
    try:
        html = path.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        print(f"错误: 无法读取文件: {e}")
        return 2

    failures = []

    def check(name, ok, detail=""):
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}" + (f" — {detail}" if detail and not ok else ""))
        if not ok:
            failures.append(name)

    # 双人报告判定（3b 与结构件口径共用）
    is_couple = "p1-tag" in html or "这段关系可能会怎样发展" in html

    # 检查区 = 去掉 <style>、灰色括注 .fn-code、可选阅读附录 .appendix-tech
    body = strip_regions(html, [
        r"<style.*?</style>",
        r"<span[^>]*class=\"[^\"]*fn-code[^\"]*\"[^>]*>.*?</span>",
        r"<section[^>]*class=\"[^\"]*appendix-tech[^\"]*\"[^>]*>.*?</section>",
        r"<div[^>]*class=\"[^\"]*appendix-tech[^\"]*\"[^>]*>.*?</div>",
    ])
    text = re.sub(r"<[^>]+>", " ", body)
    # 豁免置信度固定说明（照录块，子串稳定）：其中的"不是统计概率"是否定用法
    text = text.replace("不是统计概率", "非统计判断")

    # 1. 正文裸功能代码
    bare = []
    for code in FUNCTION_CODES:
        for m in re.finditer(rf"(?<![A-Za-z一-鿿]){code}(?![A-Za-z一-鿿])", text):
            line = text[: m.start()].count("\n") + 1
            bare.append(f"{code}(第{line}行)")
    check("正文无裸功能代码", not bare, "出现: " + ", ".join(bare[:8]))

    # 2. 禁用词
    bad_words = [w for w in FORBIDDEN_BODY if w in text]
    bad_global = [w for w in FORBIDDEN_GLOBAL if w in html]
    check("无禁用词（正文）", not bad_words, "出现: " + ", ".join(bad_words))
    check("无禁用词（全局）", not bad_global, "出现: " + ", ".join(bad_global))
    check("已取消视觉件未回流", not any(c in html for c in FORBIDDEN_CSS),
          "出现: " + ", ".join([c for c in FORBIDDEN_CSS if c in html]))

    # 3. 固定文本块（谦卑段落已取消，不再必查）
    for name, needle in REQUIRED_BLOCKS.items():
        check(f"固定文本块存在: {name}", needle in html, f"未找到关键句「{needle}」")

    # 3b. 双人报告专项
    if is_couple:
        check("双人报告：非预测承诺存在", "不是对你们关系的预测" in html,
              "未找到固定句「不是对你们关系的预测」（couple-dynamics.md §3.4）")
        check("双人报告：伦理声明存在", "不是对这段关系的判决" in html,
              "未找到固定句「不是对这段关系的判决」（couple-dynamics.md §6.2）")

    # 4. 证据标签至少使用一次
    check("使用证据标签(ev-tag)", bool(re.search(r"ev-(research|theory|hypothesis)", html)))

    # 5. meter-fill CSS（仅当报告含评分条时检查，双人组件向后兼容）
    if "meter-bar" in html or "meter-fill" in html:
        m = re.search(r"\.meter-fill\s*\{([^}]*)\}", html)
        css = m.group(1) if m else ""
        ok = m is not None and "display:block" in css.replace(" ", "") and "min-width" in css
        check("meter-fill CSS 修复(display:block + min-width)", ok,
              "缺少 .meter-fill{display:block; min-width:...}")

    # 6. 速览卡
    check("存在一页速览卡(summary-card)", "summary-card" in html)

    # 7. 打印样式
    check("存在 @media print", "@media print" in html)

    # 8. A 纸感样式（2026-09-06 改造新增）
    check("存在 @page A4", bool(re.search(r"@page[^{]*\{[^}]*size:\s*A4", html)))
    print_zone = ""
    if "@media print" in html:
        start = html.find("@media print")
        print_zone = html[start: html.find("</style>", start)]
    check("纸纹背景存在（屏幕端 feTurbulence 噪点）", "feTurbulence" in html)
    check("纸纹不打印（print 块去背景图）",
          "background-image" in print_zone and "none" in print_zone)
    check("正文列宽 680px", bool(re.search(r"body\s*\{[^}]*max-width:\s*680px", html)))

    # 9. 结构件（单人口径；双人报告本轮只继承 CSS 底，跳过计数）
    if not is_couple:
        n_head = len(re.findall(r'class="[^"]*chapter-head', html))
        n_pull = len(re.findall(r'class="pull"', html))
        n_track = len(re.findall(r'class="[^"]*bar-track', html))
        check("章节头 ≥10（00–09）", n_head >= 10, f"实际 {n_head}")
        check("拉引文 = 9（第 1–9 章每章一条）", n_pull == 9, f"实际 {n_pull}")
        check("定位条 ≥8 行(.bar-track)", n_track >= 8, f"实际 {n_track}")
        check("速览卡题记存在(.epigraph)", "epigraph" in html)
        check("组合卡存在(.combo-card)", "combo-card" in html)

    print()
    if failures:
        print(f"共 {len(failures)} 项未通过，请修复后重新 lint。")
        return 1
    print("全部检查通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: 语法自检**

Run: `python3 -c "import ast; ast.parse(open(r'C:\Users\elliot\.zcode\skills\analyzing-cognitive-functions\scripts\lint_report.py', encoding='utf-8').read())" && echo OK`
Expected: `OK`

- [ ] **Step 3: 对旧真实报告跑一次，确认新检查按预期 FAIL（此时规则文件未改、样例未建，属预期红灯）**

Run: `python3 "C:\Users\elliot\.zcode\skills\analyzing-cognitive-functions\scripts\lint_report.py" "C:\Users\elliot\Desktop\relations\MBTI\mbti_qqc.html"`
Expected: 新增的 8 项 A 纸感/结构检查出现 FAIL（@page A4 / 纸纹 / 680px / epigraph / combo-card / chapter-head≥10 / pull=9 / bar-track≥8）；既有项行为与改造前一致。**记录输出**，Task 6/8 要让它变绿。

---

### Task 3: 重写 references/html-templates.md

**Files:**
- Modify: `references/html-templates.md`（整文件重写）
- 逐字源：bigfive `references/html-templates.md`、`examples/bfi2_sample.html` `<style>` 块；数值来源：spec §1–§3

- [ ] **Step 1: 按下表逐节重写（每节先写内容再自查）**

| 新文件章节 | 内容来源 |
|---|---|
| 头部说明 | 仿 bigfive 头部：默认保存路径 `/c/Users/elliot/Desktop/relations/MBTI/`；声明"本版为 2026-09-06 视觉重设计后的模板，唯一视觉事实源 = `examples/mbti_sample.html`，改视觉规则前先看样例" |
| §1.1 CSS 变量 | spec §1.1 代码块逐字（含八功能色常量与双人人物色）；语义色 chip 表 = bigfive §1.1 三色证据标签 + 灰 chip `#F1F1EA/#5F6B76`；写明两条铁律：**不引入红绿档位色**（无常模，红绿=评价，违 R4）、功能色 = 功能身份 |
| §1.2 排版 | bigfive §1.2 逐字适配：字体双栈、正文衬线行高 2.0 两端对齐、680px 正文列、`.wide` 破格 860px、字号刻度、间距刻度、`.fn-code`；移动端断点 640px |
| §1.3 组件类总表 | bigfive §1.3 表格逐字搬运这些类：chapter-head/chapter-sub/meta-header/guide-box/toc/summary-card（边框改 `rgba(31,95,102,.5)`）/chart-box+chart-note/find-card/ev-tag 三色/fn-code/bar-container 全家（**轨道渐变换为 spec §2.1 中性双调**，删除 bar-dash 与 zc-low/mid/high 行，chip 固定灰底）/dim-block 改名说明/facet-grid+facet-card（两列）/facet-flag 删/combo-card 全家/lead/callout/rel-label/scene-box/advice-card/caution-row/appendix 系/faq-card/pull（≤22 字口径）；新增 `.epigraph` 条目（spec §2.7）；**删除**：prog-bar、chapter-key、meter-bar 系、conflict-header、match-yes/no/ok、stack-box、fn-grid 系、dual-col、dialogue（双人组件类移到文末"双人继承块"小节原样保留，注明"本轮不重绘，仅令牌换源"） |
| §1.4 打印样式 | spec §1.2 代码块逐字 |
| §2 视觉件 | 开头写分工纪律（spec §2 引语，题记管照见/定位条管分数/白描卡管解释/极性图管倾斜/剖面图管班底/栈表管核对，一图一职互不复读）；§2.1–2.6 按 spec §2.1–2.6 逐条展开成与 bigfive §2 同密度的规范（含 HTML 实现示例，数值用 Task 6 的样例数据）；§2.7 题记规范 |
| §3 报告结构 | spec §3 逐条：章节 0–9 + 附录 ABC 保持；每章 chapter-head+chapter-sub；pull ×9；combo-card ≥1；三级速读新定义；meta-header 新口径（报告日期 · 用户代号 · 数据来源）；附录结构；字数 6000–8500 |
| §4 输出规范 | 原 §4 保留（命名/路径/JSON 不变），删"依恋/成长环境章末照录谦卑段落"行；§4.3 验证清单更新为新 lint 项 |
| 全文禁写 | 不得出现"谦卑段落照录""chapter-key""进度条""首字下沉"作为要求；§9.1 原文仅可作为"已取消"存档注记 |

- [ ] **Step 2: 自查**：文中不再引用 `--highlight`/`--text`/`bar-fill`/`zc-low`/`bar-dash`（旧件名）；`grep -n "bar-dash\|zc-low\|chapter-key\|highlight" references/html-templates.md` 应无输出（存档注记除外）。

---

### Task 4: 修改 references/writing-style.md

**Files:**
- Modify: `references/writing-style.md`（4 处）

- [ ] **Step 1: §5 深度规范**——删除最后一条"**每章一句话结论框**：各章 h2 后……三级速读"，替换为：

```markdown
- **每章副题与章末锐评**：各章开头 `.chapter-sub` 用一句"这一章回答什么"引导（不写结论句）；章末 `.pull` 锐评一条（规则见 §10.6）。全报告三级速读 = 速览卡（题记 + 三条结论卡）→ 章副题 → 章末锐评
```

- [ ] **Step 2: §8.2**——"依恋、成长环境两章末尾必须附固定谦卑段落（见 §9.1）"替换为：

```markdown
2. 依恋、成长环境两章的推测属性由逐条证据标签承担；章末谦卑段落已取消（2026-09-06，与 bigfive 1206 对齐），勿再生成
```

- [ ] **Step 3: §9.1**——整节替换为存档注记：

```markdown
### 9.1 谦卑段落（已取消，2026-09-06）

原要求依恋章、成长环境章末尾照录本段；应用户要求整体移除（与 bigfive 1206 决策对齐），阅读指南与逐条证据标签已覆盖同样提示——**勿再生成**；lint 已将原句「以你的经历为准」列入禁用词。原文存档：

> 这一部分的内容全部来自分数的理论推测。你的真实经历和感受，只有你自己知道——如果哪里说得不对，以你的经历为准。如果某处内容让你有触动，可以留给自己慢慢消化，也可以和任何你信任的人聊聊。
```

- [ ] **Step 4: 文末新增 §10**（Contents 列表同步加一行）：

```markdown
## 10. 组合卡与标签式结构（2026-09-06 新增，对应 bigfive §10）

1. 跨功能组合结论：必须写成组合卡（模板见 html-templates.md）——先并排给出两个功能的**排位词 + 原始分 + 白描一句**（本 skill 无常模无 z，「档位+z 值」落地为「排位词+原始分」），再用大白话解释组合含义 + 一个典型场景。措辞用"看起来 / 倾向于"；证据标签按立场挂 🔶 或 ⚪，并计入报告末尾证据统计。禁裸断言。
2. 排位词一致性：组合卡与速览卡结论中的排位词（最顺手 / 前两位 / 靠后 / 最费力）必须与分数排位一致；禁"低 / 差"式评价词（R4 姊妹条）。
3. 第 6 章标签式结构：亲密关系等用 .rel-label 引导；每块"描述在前、场景在后"，场景写入 .scene-box；场景属推测性质，标 ⚪。
4. 语言密度：目标读者没有心理学基础——组件的读法只允许一行说明（chart-note/图例），正文不得复述组件用法（禁"下面这张表把…摆在一起"式旁白）；结论卡/组合卡给过的结论，正文只写"意味着什么、怎么做"，不重述；一处结论只带一个推测标记，禁止叠加免责；正文段 ≤3 句，场景对白除外。
5. 一结论一画面：每个抽象结论后面必须跟一个"比如"级的日常画面（谁在做什么、具体发生了什么），没有画面的结论改写到有画面为止——"晦涩"的根源几乎都是结论裸奔。
6. 锐评式拉引文（.pull，第 1–9 章每章一条，共 9 条）：对本章做 ≤22 字（一行以内）的一句话锐评——言辞犀利、一针见血；必须落在具体行为或数据上，敢下判断；禁对仗金句腔（"稳处省电弱处耗神"式）、禁"不是A而是B"排比堆叠、禁概括到谁都能套；只用本章素材，不引入新结论，不带证据标签；数量由 lint 把关。
7. 去 AI 味基线（全文适用，按 humanizer-zh 清单自查）：禁"这是一个温和的好消息"式概括抒情、禁"愿你……"祝愿腔、禁三段式排比堆叠、"不是A而是B"每段至多一次（全篇 ≤2）、破折号每段至多一个；改完大声读一遍，读着像电台稿就重写。比喻先自问一句：读者能一眼解出来吗？解不出来的比喻宁可不用。
8. 题记（.epigraph，速览卡内，全报告一条）：内容落在前两位功能的组合上，用已教过的白话概念；≤32 字，可断两行；下方挂名行小字把句子挂回功能名（如"——你的前两位：外倾直觉 · 内倾情感（分数见第 1 章）"）；禁对仗金句腔；挂名行的功能名与分数排序一致。
```

- [ ] **Step 5: 自查**：`grep -n "必须附固定谦卑段落\|每章一句话结论框" references/writing-style.md` 应无输出；`grep -n "## 10" references/writing-style.md` 存在。

---

### Task 5: 同步 attachment-inference.md 与 SKILL.md

**Files:**
- Modify: `references/attachment-inference.md`（1 行）
- Modify: `SKILL.md`（4 处）

- [ ] **Step 1: attachment-inference.md §4.1**——删除这一行：

```
- 来访者报告正文中，依恋章末尾必须照录固定谦卑段落（writing-style.md §9.1）
```

- [ ] **Step 2: SKILL.md「Workflow → 关键要求」第一条**，替换为：

```markdown
- 报告第 0 章速览卡 = 题记 + 三条结论卡 + 恋爱一句话，无图表（题记规则 `writing-style.md` §10.8）；报告第 1 章：渐变定位条给「分数模样」，白描卡给每个维度的解释；四条轴的倒向与含义放报告第 3 章，配**三轴极性图**＋假设场景（`html-templates.md` §2.3）
```

- [ ] **Step 3: SKILL.md Phase 2**——"章节结构（11 部分……）视觉件（降序条形图 / 功能速览网格 / 三轴极性图 / 排位剖面图 / 依恋象限图 / 类型栈表）"替换为：

```markdown
- 章节结构（0–9 章与附录，各章 chapter-head + 副题 + 章末锐评拉引文）、视觉件（渐变定位条 / 白描卡 / 题记 / 三轴极性图 / 排位剖面图 / 依恋象限图 / 类型栈表）、组件 CSS、打印样式：严格按 `references/html-templates.md` §1-3（唯一视觉事实源 = `examples/mbti_sample.html`）
```

- [ ] **Step 4: SKILL.md Phase 2 语言行与固定文本块行**——"去 AI 味规则、证据三级标签"后加"§10 组合卡与标签式结构"；"固定文本块（阅读指南/伦理声明/谦卑段落/局限声明）"改为"固定文本块（阅读指南/伦理声明/局限声明）"（谦卑段落已取消）。

- [ ] **Step 5: SKILL.md Phase 3 lint 描述**——"检查：正文裸功能代码、禁用词（含统计措辞）、固定文本块、证据标签、meter-fill CSS、速览卡、打印样式"替换为：

```markdown
   - 检查：正文裸功能代码、禁用词（含统计措辞与已取消的谦卑段落原句）、固定文本块、证据标签、A 纸感样式（@page A4、纸纹不打印、680px）、结构件（chapter-head ≥10、pull =9、epigraph、combo-card、定位条 ≥8）、速览卡、打印样式；双人报告额外检查非预测承诺与伦理声明，并跳过单人口径计数
```

- [ ] **Step 6: 自查**：`grep -n "谦卑" SKILL.md references/attachment-inference.md` 无输出；`grep -n "降序条形图\|功能速览网格" SKILL.md` 无输出。

---

### Task 6: 生成基线样例 examples/mbti_sample.html（lint 变绿 + 唯一视觉事实源）

**Files:**
- Create: `examples/mbti_sample.html`

**合成数据（代号 SAMPLE-01，测评日期 2026-09-01，报告日期 2026-09-06；INFJ 首选 / INTJ 次选，阴影位映射按 Beebe 标准 = Ne/Fi/Te/Si，Si 第 8 位异常偏高——覆盖异常位标注场景）：**

| 功能 | Ne | Ni | Fe | Fi | Te | Ti | Se | Si |
|---|---|---|---|---|---|---|---|---|
| 分 | 55.4 | 82.6 | 74.3 | 41.7 | 33.2 | 61.2 | 38.5 | 68.9 |

- [ ] **Step 1: 按新 html-templates.md §1–3 生成完整单人报告**（结构 0–9 章 + 附录 A/B/C 全齐）。关键锚点：
  - `<style>` = 新令牌 + 组件 CSS（从 bigfive 样例 `<style>` 搬运并按 spec 适配）；`body` 含噪点 data URI、`max-width:680px`
  - 定位条 8 行降序：Ni 82.6（感知 · 对内）/ Fe 74.3（判断 · 对外）/ Si 68.9（感知 · 对内）/ Ti 61.2（判断 · 对内）/ Ne 55.4（感知 · 对外）/ Fi 41.7（判断 · 对内）/ Se 38.5（感知 · 对外）/ Te 33.2（判断 · 对外）；chip = `● 82.6` 式灰底；轨道中性双调；外包 `.wide` + `.bar-legend`
  - 白描卡 ×8 两列，教学序 Ni, Fi, Ti, Te, Fe, Ne, Si, Se，白描句逐字取 writing-style §2 表
  - 题记（.epigraph）：正文「先在心里看清走向，再回头看房间里每个人的脸色。」挂名行「——你的前两位：内倾直觉 · 外倾情感（分数见第 1 章）」
  - find-card ×3：最顺手（Ni+Fe）/ 最费力（Te+Se）/ 注意一件事（Si 异常：第 8 位实测全场第三）
  - 第 3 章：三轴极性图（态度轴内倾 254.4 ↔ 外倾 201.4；感知轴直觉 138.0 ↔ 实感 107.4；判断轴情感 116.0 ↔ 思考 94.4）+ 排位剖面图（1–4 位深色 Ni/Fe/Ti/Se——注意第 4 位 Se 38.5 与 50 虚线的位置、5–8 位浅色 Ne/Fi/Te/Si，Si 行末标「异常：第 8 位实测全场第三」）+ combo-card（内倾直觉 · 第一位 · 82.6 × 外倾感觉 · 第七位 · 38.5 →「看走向的人，容易错过眼前正在发生的事」+ 一个具体场景）
  - 第 6 章依恋：象限图 ×2（恋爱/家人，虚线圆位置按 Si 68.9 + Fe 74.3 推：偏安全侧但标 ⚪ 与边界提示），章末**不放**谦卑段落
  - 第 1–9 章末各一条 `.pull`（≤22 字，落在具体行为/数据，禁对仗金句腔；例：第 1 章「你不是没有主见，是主见都先过一遍道理。」第 3 章「你的眼睛长在走向上，不长在眼前。」——其余由执行者按 §10.6 写）
  - 固定文本块照录：阅读指南（writing-style §9.2）、局限声明（§9.3）、类型只是名字（§2.3）、置信度固定说明（scoring-algorithm §2.5）
  - 附录 B 证据统计行 = 数出来的实际标签数
- [ ] **Step 2: lint**

Run: `python3 "C:\Users\elliot\.zcode\skills\analyzing-cognitive-functions\scripts\lint_report.py" "C:\Users\elliot\.zcode\skills\analyzing-cognitive-functions\examples\mbti_sample.html"`
Expected: `全部检查通过。`（FAIL 逐条修复直到 PASS）

- [ ] **Step 3: 浏览器目检**：本地打开样例，核对——定位条圆点位置与数字互证、剖面图深浅与异常位标注、象限图虚线圆、题记排版、chapter-head 双细线、pull 一行内；打印预览（Ctrl+P）纸纹消失、无组件断裂。

---

### Task 7: lint 双人口径自检

**Files:**
- Create: `examples/_couple_probe.html`（临时探针，验证后删除）

- [ ] **Step 1: 写最小双人探针**——含 `class="p1-tag"`、固定句「不是对你们关系的预测」与「不是对这段关系的判决」、**不含** epigraph/combo-card/chapter-head×10/pull×9，跑 lint。
Run: `python3 scripts/lint_report.py examples/_couple_probe.html`
Expected: 结构件 5 项（chapter-head/pull/bar-track/epigraph/combo-card）**不出现**（跳过），非预测承诺与伦理声明 PASS。

- [ ] **Step 2: 删除探针** `rm examples/_couple_probe.html`。

---

### Task 8: 真实报告首秀验收（mbti_qqc-v2.html）

**Files:**
- Create: `C:\Users\elliot\Desktop\relations\MBTI\mbti_qqc-v2.html`
- 数据：`C:\Users\elliot\Desktop\relations\MBTI\mbti_qqc.json`（Ne 56.26 / Ni 51.72 / Fe 52.2 / Fi 55.6 / Te 45.24 / Ti 49.3 / Se 44.08 / Si 51.62；Ne/Fi 前二）

- [ ] **Step 1: 按 SKILL.md Workflow 全流程**（Phase 0 解析回显→Phase 1 分析→Phase 2 生成）产出报告；类型候选与置信度按 scoring-algorithm §2.3 重算，题记落在 Ne+Fi 组合上，核心张力用 combo-card，pull ×9 逐章落实，正文 6000–8500 字
- [ ] **Step 2: lint PASS** + JSON 分数与报告一致（8 键顺序 Ne,Ni,Fe,Fi,Te,Ti,Se,Si）
- [ ] **Step 3: 渲染成 PNG 并派 judge 子代理验收**——把报告关键屏（速览卡/第 1 章/第 3 章两图/第 6 章象限/章末 pull）截图存 PNG，派一个 judge agent（subagent_type: judge），传入 PNG 路径与验收要点（A 纸感一致性 vs `bfi2_qqc.html`、无进度条/谦卑段落/首字下沉、pull ≤22 字、组合卡有推导）；按 verdict 修复后复验
- [ ] **Step 4: 三方对照**：`mbti_qqc-v2.html` vs 旧 `mbti_qqc.html` vs `bfi2_qqc.html` 并排目测——纸感/章节头/卡片/拉引文风格统一；旧版保留不覆盖
- [ ] **Step 5: 红线抽查**：全篇"不是A而是B" ≤2 处；每条 pull ≤22 字；无"以你的经历为准"；grep `prog-bar|first-letter` 无输出

---

### Task 9: 收尾汇报

- [ ] 向用户汇报：改动文件清单、lint 前后对比、首秀验收结论、与 spec 的任何偏差及理由；停止视觉 companion 服务器（如仍在运行）
