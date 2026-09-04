#!/usr/bin/env python3
"""BFI-2 报告 HTML 质量检查

检查项：
- 禁用词（工程/IT/系统类词汇、裸英文）
- 固定文本块缺失
- 图表容器完整性
- 维度 z 分一致性（雷达图/正文/仪表条 同维度不得矛盾）
- meter-fill CSS 要求
- 局限声明存在性
"""

import sys
import re
import os

FORBIDDEN_WORDS = [
    "系统", "架构", "机制", "流程", "输入", "输出", "通道", "带宽", "负载",
    "算法", "迭代", "反馈", "模块", "组件", "审查", "监控", "容器", "支架",
    "空转", "宕机", "重启", "调试", "程序", "数据库", "接口", "回路", "闭环",
    "触发器", "运算", "处理器", "默认设置", "双核", "双引擎",
    "情绪温度计", "信任基石", "效率引擎", "稳定性指标",
    "神经质", "负性情绪",
    # 心理学术语（R8 术语零容忍兜底，见 writing-style.md §6）
    "认知功能", "心理功能", "感觉功能", "判断功能", "功能栈", "功能结构",
    "意识位置", "在场感", "叙事", "价值标准", "价值判断", "内在安抚",
    "自洽", "感官体验", "感官投入", "收拢",
    "获取和消耗能量", "目标导向行为",
    "咨询师", "会谈", "咨询中",  # R6: 全文档禁止（§9.3 固定块不再含此词）
]

REQUIRED_BLOCKS = [
    ("阅读指南", "怎么读这份报告"),
    ("局限声明", "不构成临床诊断"),
    ("谦卑段", "这一部分的内容全部来自分数的理论推测"),  # writing-style.md §9.1
]

REQUIRED_CONTAINERS = [
    ("meta-header", "页眉"),
    ("guide-box", "阅读指南"),
    ("toc", "目录"),
    ("summary-card", "速览卡"),
    ("chart-box", "图表容器"),
    ("bar-container", "仪表条"),
    ("facet-grid", "子维度网格"),
    ("riasec-badge", "RIASEC 代码标签"),
    ("ev-tag", "证据标签"),
]

# BFI-2 五个维度的合法报告称谓（writing-style.md §2 唯一合法称呼）
DOMAINS = ["外向性", "宜人性", "尽责性", "情绪稳定性", "开放性"]

# 文件名规范：bfi2_{代号}.html（单人）/ bfi2_{代号A}_{代号B}.html（双人）
# 代号 = 字母数字，可含 -（如 zyh、A001、zyh-v2），不用空格和 _，_ 保留作双人分隔符
FILENAME_RE = re.compile(
    r"^bfi2_[A-Za-z0-9][A-Za-z0-9-]*(?:_[A-Za-z0-9][A-Za-z0-9-]*)?\.html$"
)


def normalize_z(s: str) -> str:
    """统一 z 分字符串：去前导 +、补足两位小数，便于比较。"""
    s = s.strip().lstrip("+")
    if "." in s:
        i, d = s.split(".", 1)
        d = (d + "00")[:2]
        sign = "-" if i.startswith("-") else ""
        i = i.lstrip("-")
        return f"{sign}{i.zfill(1)}.{d}"
    return s


def extract_domain_zs(html: str) -> dict[str, set[str]]:
    """对每个维度名，从四个结构化锚点收集 z 分：
    1) <h3>{dim} ... z = ±X.XX ...</h3> 维度解释小节标题（z 括号后允许证据标签 span）
    2) <!-- {dim}(z=±X.XX): --> SVG 雷达图坐标注释
    3) bar-label>{dim}</span> ... bar-marker>● ±X.XX 仪表条
    4) 雷达 SVG 轴端标签：>维度名</text> 后最近的 z text
    同维度的各处 z 必须一致；不一致即视作 chart/正文/轴端 符号翻转等 bug。
    通用邻近匹配会跨入相邻维度的 z，本结构化匹配只看上述锚点，避免假阳性。
    """
    out: dict[str, set[str]] = {d: set() for d in DOMAINS}
    for d in DOMAINS:
        # 1) 维度小节标题 z（z 括号与 </h3> 之间允许 ev-tag 等 span）
        for m in re.finditer(
            rf"<h3>{re.escape(d)}\s*<span[^>]*>.*?</span>：[^（]*?（z\s*=\s*([+\-]?\d+\.\d{{1,2}})）.*?</h3>",
            html, re.S,
        ):
            out[d].add(normalize_z(m.group(1)))
        # 2) SVG 注释里的雷达 z
        for m in re.finditer(
            rf"<!--\s*{re.escape(d)}\(z\s*=\s*([+\-]?\d+\.\d{{1,2}})\s*\):", html
        ):
            out[d].add(normalize_z(m.group(1)))
        # 3) 仪表条：bar-label 为维度名 → 200 字符内首个 ● ±X.XX
        for m in re.finditer(
            rf'class="bar-label"[^>]*>{re.escape(d)}</span>.{{0,200}}?●\s*([+\-]?\d+\.\d{{1,2}})',
            html, re.S,
        ):
            out[d].add(normalize_z(m.group(1)))
        # 4) 雷达轴端标签：维度名加粗 text 后最近的 z text
        for m in re.finditer(
            rf'<text [^>]*font-weight="700">{re.escape(d)}</text>\s*<text [^>]*>([+\-]?\d+\.\d{{1,2}})</text>',
            html, re.S,
        ):
            out[d].add(normalize_z(m.group(1)))
    return out


def lint(filepath: str) -> list[str]:
    """Run all lint checks. Returns list of FAIL messages (empty = all PASS)."""
    fails: list[str] = []

    if not os.path.isfile(filepath):
        return [f"FAIL: file not found: {filepath}"]

    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # ── 1. Forbidden words ──
    for word in FORBIDDEN_WORDS:
        pattern = re.compile(re.escape(word))
        matches = pattern.findall(html)
        if matches:
            fails.append(f"FAIL: forbidden word '{word}' found ({len(matches)}x)")

    # ── 2. Required fixed text blocks ──
    for label, snippet in REQUIRED_BLOCKS:
        if snippet not in html:
            fails.append(f"FAIL: missing required block '{label}' (expected snippet: '{snippet}')")

    # ── 3. Required containers ──
    for cls, label in REQUIRED_CONTAINERS:
        if f'class="{cls}' not in html and f"class='{cls}" not in html:
            fails.append(f"FAIL: missing required container '{label}' (.{cls})")

    # ── 4. meter-fill display requirement ──
    if "meter-fill" in html:
        block_match = re.search(r'\.meter-fill\s*\{[^}]*\}', html)
        if block_match:
            block = block_match.group(0)
            if "display:block" not in block and "display: block" not in block:
                fails.append("FAIL: .meter-fill must have display:block")
        if "min-width" not in html:
            fails.append("FAIL: .meter-fill should have min-width")

    # ── 5. Disclaimer ──
    if "不构成临床诊断" not in html:
        fails.append("FAIL: missing disclaimer '不构成临床诊断'")

    # ── 6. Basic structure ──
    if "<svg" not in html:
        fails.append("FAIL: no SVG charts found (radar/bar required)")

    # ── 7. 维度 z 分一致性（防 chart/正文 符号翻转） ──
    domain_zs = extract_domain_zs(html)
    for d, vals in domain_zs.items():
        if len(vals) > 1:
            fails.append(
                f"FAIL: 维度 '{d}' 的 z 分在多处不一致: {sorted(vals)}（图表与正文可能符号翻转）"
            )

    # ── 8. 证据标签声明数 vs 实际数一致（writing-style.md §7） ──
    actual_research = len(re.findall(r'class="ev-tag ev-research"', html))
    actual_theory = len(re.findall(r'class="ev-tag ev-theory"', html))
    actual_hypothesis = len(re.findall(r'class="ev-tag ev-hypothesis"', html))
    declared = re.search(
        # 三项统计必须紧邻出现（仅允许数量单位/分隔符/证据 emoji），防止跨段误匹配正文中的相似文字
        r'研究支持\s*×\s*(\d+)\s*处?\s*(?:[·,，|/、；]\s*)?[✅🔶⚪]?\s*理论推断\s*×\s*(\d+)\s*处?\s*(?:[·,，|/、；]\s*)?[🔶⚪]?\s*探索性假设\s*×\s*(\d+)',
        html, re.S
    )
    if declared:
        d_research, d_theory, d_hypothesis = (
            int(declared.group(1)), int(declared.group(2)), int(declared.group(3))
        )
        if d_research != actual_research:
            fails.append(
                f"FAIL: 证据标签数不一致 — ✅研究支持 声明 {d_research} 处，实际 {actual_research} 处"
            )
        if d_theory != actual_theory:
            fails.append(
                f"FAIL: 证据标签数不一致 — 🔶理论推断 声明 {d_theory} 处，实际 {actual_theory} 处"
            )
        if d_hypothesis != actual_hypothesis:
            fails.append(
                f"FAIL: 证据标签数不一致 — ⚪探索性假设 声明 {d_hypothesis} 处，实际 {actual_hypothesis} 处"
            )
    elif actual_research + actual_theory + actual_hypothesis > 0:
        fails.append(
            f"FAIL: 报告含证据标签 ({actual_research}/{actual_theory}/{actual_hypothesis}) "
            f"但未找到'结论依据构成'声明（writing-style.md §7 要求末尾附统计）"
        )

    # ── 9. 章节结构完整性（html-templates.md §3） ──
    basename = os.path.basename(filepath)
    is_couple = len(basename.split("_")) > 2  # bfi2_A_B.html：_ 保留作双人分隔符
    if is_couple:
        if "p1-tag" not in html or "p2-tag" not in html:
            fails.append("FAIL: 双人报告须同时含 .p1-tag 与 .p2-tag 人物标签")
        if "这份报告基于双方的人格测评数据分析" not in html:
            fails.append("FAIL: 双人报告缺少伦理声明（couple-dynamics.md §7 固定块）")
    else:
        for anchor, label in [("s4", "工作中"), ("s5", "压力下的你"),
                              ("s6", "与人相处"), ("s7", "成长建议")]:
            if f'id="{anchor}"' not in html:
                fails.append(
                    f"FAIL: 缺少章节锚点 #{anchor}（{label}，html-templates.md §3.1 "
                    f"要求单人报告含第 4-7 章）"
                )

    # ── 10. 文件命名（bfi2_{代号}.html / bfi2_{代号A}_{代号B}.html）──
    if not FILENAME_RE.match(basename):
        fails.append(
            f"FAIL: 文件名不符合规范 '{basename}'（应为 bfi2_{{代号}}.html 或 bfi2_{{代号A}}_{{代号B}}.html）"
        )

    return fails


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 lint_report.py <report.html>")
        sys.exit(1)

    filepath = sys.argv[1]
    fails = lint(filepath)

    if fails:
        for msg in fails:
            print(msg)
        print(f"\n{len(fails)} check(s) FAILED")
        sys.exit(1)
    else:
        print("PASS: all checks passed")
        sys.exit(0)


if __name__ == "__main__":
    main()