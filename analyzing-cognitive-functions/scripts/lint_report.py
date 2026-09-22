#!/usr/bin/env python3
"""交付前校验：python lint_report.py <report.html>

单人/双人口径自动判定（含 renderBeam / renderHeroRadar / 「双人（恋人）」即双人）。
全部检查 PASS 退出码 0，否则 1。禁用词表与 references/writing-style.md §5 保持同步。
"""

import re
import sys
from pathlib import Path

# 与 writing-style §5 同步的禁用词（机械投影）
FORBIDDEN_WORDS = [
    "优势", "劣势", "优点", "缺点", "强项", "短板", "缺陷",
    "断层", "分数分层",
    "Fi-Ni loop", "内循环",
    "神经质", "情绪稳定性",
    "你就是太", "以你的经历为准",
]

# 旧组件黑名单（回归防御：只在旧版出现过的件名）
FORBIDDEN_LEGACY = [
    "summary-card", "epigraph", "chapter-head", "chapter-sub",
    "fnchart", "axis-fill", "combo-card", "type-cards",
    "fit-fill", "fit-", "person-card", "chip-row",
    "p1-tag", "--p1-color", "meta-header", "ev-tag",
]

SINGLE_REQUIRED = [
    "Jungian Cognitive Functions · 人格坐标报告",
    "荣格八维理论——提供对意识运作机理的深层内在解释力",
    "别把任何标签当身份证",
    "你的盲区：并非不足，是成本",
    "你付出的和你想要的，经常不是同一种东西",
    "对成年人来说，守住你最常用的功能，回报远高于死磕最不常用的那一格",
    "不是能力测评",
    "不是诊断工具",
    "不能预测行为",
    "不能替代亲身验证",
    "类型是理解人的辅助工具，不是人本身",
    "回到自己身上核对",
    "类型是地图，不是领土",
    "压力下的退行形态",
    "附录",
]

COUPLE_REQUIRED = [
    "Jungian Cognitive Functions · 双人（恋人）分析报告",
    "互为触发点",
    "这不是合盘判决书",
    "关系是做出来的，不是算出来的",
    "类型是地图，不是领土",
]


def is_couple(html: str) -> bool:
    return ("renderBeam" in html) or ("renderHeroRadar" in html) or ("双人（恋人）" in html)


def check(html: str) -> list:
    problems = []
    couple = is_couple(html)

    for w in FORBIDDEN_WORDS:
        if w in html:
            problems.append(f"[禁用词] {w}")
    for w in FORBIDDEN_LEGACY:
        if w in html:
            problems.append(f"[旧件] {w}")

    required = COUPLE_REQUIRED if couple else SINGLE_REQUIRED
    for s in required:
        if s not in html:
            problems.append(f"[缺固定句] {s}")

    # 类型判定块：锁格成功或锁不住并列，至少其一
    if not couple and ("最接近的类型" not in html) and ("主导未定" not in html):
        problems.append("[缺结构] 类型判定块（最接近的类型 / 主导未定）")

    if couple:
        sections = re.findall(r'<section id="s([0-5])"', html)
        if sorted(set(sections)) != ["0", "1", "2", "3", "4", "5"]:
            problems.append(f"[结构] 双人章节应为 s0–s5，实得 {sorted(set(sections))}")
    else:
        sections = re.findall(r'<section id="s([1-8])"', html)
        if sorted(set(sections)) != ["1", "2", "3", "4", "5", "6", "7", "8"]:
            problems.append(f"[结构] 单人章节应为 s1–s8，实得 {sorted(set(sections))}")

    if "@media print" not in html:
        problems.append("[缺结构] 打印样式")
    return problems


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python lint_report.py <report.html>")
        return 2
    html = Path(sys.argv[1]).read_text(encoding="utf-8")
    problems = check(html)
    print(f"口径: {'双人' if is_couple(html) else '单人'}")
    if problems:
        print(f"FAIL（{len(problems)} 项）")
        for p in problems:
            print(" -", p)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
