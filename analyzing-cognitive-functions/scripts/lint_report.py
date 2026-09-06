#!/usr/bin/env python3
"""lint_report.py — 校验 analyzing-cognitive-functions 生成的报告 HTML 是否符合规范。

用法: python scripts/lint_report.py <报告文件.html>
退出码: 0 = 全部通过; 1 = 存在 FAIL; 2 = 文件/参数错误

2026-09-07 版（用户批复落地）：
- 单人报告 = hero 新基线（docs/2026-09-07-reference-content-plan.md）：
  hero（kicker + 定位句 + lede 固定句 + 雷达）→ 01 总览（关键词总表 + 柱状图 + 候选类型表）
  → 02 四组对照（对照总表 + 天平图×4 + 强端·代价表 + 双弱福利·代价表 + 场景块）
  → 03 优势表 → 04 盲区表 → 05 亲密关系（rel 定义列表 + 兼容表 + 三句句式）
  → 06 建议表 → 07 边界声明 + 附录得分明细 + footer。
  检查：结构件计数 / 固定句 / 比喻收缩禁词（记账系·暗房系·租客系·机械系统系·昵称层）/
  卡框与旧件回流 = FAIL / @page A4 + 噪点 + 680px + @media print。
  裸功能代码在单人正文解禁（彩色代码 = 身份）；证据标签退出正文。
- 双人报告 = 2026-09-06 冻结基线：单人结构件自动跳过；走双人口径——
  裸代码禁令 + 证据标签 + 章节头 =8 + pull =8 + fit-fill ≥16 + 非预测承诺 + 伦理声明。
2026-09-06 及更早的修订史见文件头存档（git 历史与 docs/）。
"""
import re
import sys
from pathlib import Path

FUNCTION_CODES = ["Fi", "Ni", "Fe", "Ti", "Te", "Ne", "Se", "Si"]

# 正文禁用词（单人 + 双人都查；appendix-tech 内不查 Beebe 术语）
FORBIDDEN_BODY = ["劣势功能", "主导功能", "Fi-Ni loop", "Fi-Ni Loop", "阴影功能",
                  "结构性情感失语", "病态", "缺陷",
                  # 已弃用的比喻命名（价值罗盘 2026-09-07 解禁；罗盘/自我罗盘允许）
                  "情绪天线", "逻辑拆解器", "效率引擎",
                  "长线望远镜", "可能性喷泉", "安全基地", "当下雷达",
                  # 比喻收缩禁用系（writing-style §4.1，2026-09-07）
                  "税", "电费", "脚手架", "基建", "欠费", "货币", "预支",
                  "显影", "底片", "暗房",
                  "租客", "物业费", "拖欠",
                  "引擎", "变速箱", "漏电", "锚点", "托管", "反刍",
                  # 昵称层（2026-09-07 废弃；「跨阵营翻译官」为优势表定稿标题，豁免）
                  "显影机", "万花筒", "守档人", "推土机", "建模师",
                  "可能性雷达", "氛围翻译", "推进器", "在场感", "经验存档",
                  # 工程/IT/系统类（writing-style.md §4.5）
                  "系统", "架构", "机制", "流程", "输入", "输出", "通道", "带宽", "负载",
                  "算法", "迭代", "反馈", "模块", "组件", "审查", "监控", "容器", "支架",
                  "空转", "宕机", "重启", "调试", "程序", "数据库", "接口", "回路", "闭环",
                  "触发器", "运算", "处理器", "默认设置", "双核", "双引擎",
                  # 心理学术语（R7 术语零容忍的兜底，见 writing-style.md §6；
                  # 「自洽」2026-09-07 解禁——目标读者画像下的日常语汇）
                  "认知功能", "心理功能", "感觉功能", "判断功能", "功能栈", "功能结构",
                  "意识位置", "叙事", "价值标准", "价值判断", "内在安抚",
                  "感官体验", "感官投入", "收拢",
                  # 报告正文禁止的外部关系导向
                  "咨询师", "会谈", "咨询中",
                  # 统计措辞（"不是统计概率"在扫描前豁免，见 main 中的替换）
                  "显著", "证实", "证明", "概率"]
# 任何位置都禁止（含附录；谦卑段落已取消 2026-09-06）
FORBIDDEN_GLOBAL = ["你就是太", "你一定会", "你肯定会", "神经质", "情绪稳定性", "必然",
                    "以你的经历为准"]
# 全模式禁用的已取消视觉件（红线：勿生成）
FORBIDDEN_CSS = ["prog-bar", "first-letter"]
# 单人模式已废弃件（回流 = FAIL；html-templates.md §2.7）
FORBIDDEN_LEGACY_SINGLE = [
    "summary-card", "epigraph", "chapter-head", 'class="pull"',
    "fnchart", "fn-fill", "axis-block", "axis-fill", "combo-card",
    "type-cards", "type-card", "meta-header", "guide-box", "stack-table",
    "chart-box", 'class="card"', 'class="grid2"', "ov-grid", "procon",
    'id="toc"', 'class="toc"', "meter-bar", "meter-fill",
]
# 单人固定句（照录 writing-style §9；needle 用标点无关的稳定子串）
SINGLE_REQUIRED = [
    ("hero lede 固定句", "提供对意识运作机理的深层内在解释力"),
    ("01 章末标签句", "别把任何标签当身份证"),
    ("02 章引言（冠名修正 + 天平读法）", "荣格学派的类型学"),
    ("02 章引言（天平读法）", "每组像一架小天平"),
    ("04 章引言", "要比别人多花力气"),
    ("07 边界声明", "不是判决书"),
    ("footer 临床句", "不构成临床诊断"),
    ("05 三句句式", "三句值得直接背下来的句式"),
]
REL_KEYS = ["你给出的", "你索取的", "你的摩擦点", "关系里的你"]


def strip_regions(html: str, patterns) -> str:
    for pat in patterns:
        html = re.sub(pat, " ", html, flags=re.DOTALL | re.IGNORECASE)
    return html


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: python scripts/lint_report.py <报告文件.html>")
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

    # 双人报告判定（09-06 冻结基线口径）
    is_couple = "p1-tag" in html or "这段关系可能会怎样发展" in html

    # 检查区 = 去掉 <style>、双人灰色括注 .fn-code、可选阅读附录 .appendix-tech
    body = strip_regions(html, [
        r"<style.*?</style>",
        r"<span[^>]*class=\"[^\"]*fn-code[^\"]*\"[^>]*>.*?</span>",
        r"<section[^>]*class=\"[^\"]*appendix-tech[^\"]*\"[^>]*>.*?</section>",
        r"<div[^>]*class=\"[^\"]*appendix-tech[^\"]*\"[^>]*>.*?</div>",
    ])
    text = re.sub(r"<[^>]+>", " ", body)
    # 豁免置信度固定说明（照录块，子串稳定）：其中的"不是统计概率"是否定用法
    text = text.replace("不是统计概率", "非统计判断")
    # 豁免 04 章 h2 否定用法（照录参考正文「不是缺陷，是成本」）
    text = text.replace("不是缺陷", "并非不足")

    # 1. 禁用词
    bad_words = [w for w in FORBIDDEN_BODY if w in text]
    bad_global = [w for w in FORBIDDEN_GLOBAL if w in html]
    check("无禁用词（正文）", not bad_words, "出现: " + ", ".join(bad_words))
    check("无禁用词（全局）", not bad_global, "出现: " + ", ".join(bad_global))
    check("已取消视觉件未回流", not any(c in html for c in FORBIDDEN_CSS),
          "出现: " + ", ".join([c for c in FORBIDDEN_CSS if c in html]))

    # 2. 双人报告专项（09-06 冻结基线）
    if is_couple:
        # 裸功能代码禁令保留给双人口径（09-06 纪律）
        bare = []
        for code in FUNCTION_CODES:
            for m in re.finditer(rf"(?<![A-Za-z一-鿿]){code}(?![A-Za-z一-鿿])", text):
                line = text[: m.start()].count("\n") + 1
                bare.append(f"{code}(第{line}行)")
        check("双人报告：正文无裸功能代码", not bare, "出现: " + ", ".join(bare[:8]))
        check("双人报告：非预测承诺存在", "不是对你们关系的预测" in html,
              "未找到固定句「不是对你们关系的预测」（couple-dynamics.md §3.4）")
        check("双人报告：伦理声明存在", "不是对这段关系的判决" in html,
              "未找到固定句「不是对这段关系的判决」（couple-dynamics.md §6.2）")
        n_head = len(re.findall(r'class="[^"]*chapter-head', html))
        n_pull = len(re.findall(r'class="pull"', html))
        n_fitfill = len(re.findall(r'class="[^"]*fit-fill', html))
        check("双人报告：章节头 = 8（01–08）", n_head == 8, f"实际 {n_head}")
        check("双人报告：拉引文 = 8（第 1–8 章每章一条）", n_pull == 8, f"实际 {n_pull}")
        check("双人报告：评分条行 ≥16（.fit-fill，8 维度 × 双方）", n_fitfill >= 16, f"实际 {n_fitfill}")
        check("双人报告：阅读指南存在", "怎么读这份报告" in html, "未找到「怎么读这份报告」")
        check("双人报告：使用证据标签(ev-tag)", bool(re.search(r"ev-(research|theory|hypothesis)", html)))

    # 3. 单人结构件（hero 新基线）
    if not is_couple:
        check("hero：kicker 存在", 'class="kicker"' in html)
        check("hero：定位句 h1 存在", "<h1" in html)
        check("hero：lede 存在", 'class="lede"' in html)
        check("hero：雷达图容器", 'class="radar-box"' in html and "<svg" in html)
        check("柱状图：柱 ≥8（<rect）", len(re.findall(r"<rect", html)) >= 8,
              f"实际 {len(re.findall(r'<rect', html))}")
        n_beam = len(re.findall(r'class="beam"', html))
        check("天平图 = 4", n_beam == 4, f"实际 {n_beam}")
        n_duo = len(re.findall(r'class="duo-t"', html))
        check("强端·代价表 = 4（.duo-t）", n_duo == 4, f"实际 {n_duo}")
        check("关键词总表", "<th>关键词</th>" in html and "功能 · 分数 · 排名" in html)
        check("对照总表", "<th>对照</th>" in html)
        check("优势表", "<th>优势</th>" in html)
        check("盲区表三列头", "<th>盲区</th>" in html and "真实成本" in html and "可以怎么做" in html)
        check("建议表", "<th>方向</th>" in html)
        check("候选类型表", "最接近的类型" in html)
        missing_rel = [k for k in REL_KEYS if k not in html]
        check("rel 定义列表四键", not missing_rel, "缺少: " + ", ".join(missing_rel))
        n_compat = len(re.findall(r"<td><strong>与", html))
        check("兼容表 ≥4 行", n_compat >= 4, f"实际 {n_compat}")
        n_sec = len(re.findall(r'class="sec-num"', html))
        check("章节 sec-num = 7（01–07）", n_sec == 7, f"实际 {n_sec}")
        missing_ids = [i for i in range(1, 8) if f'id="s{i}"' not in html]
        check("锚点 id s1–s7", not missing_ids, "缺少: " + ", ".join(missing_ids))
        for name, needle in SINGLE_REQUIRED:
            check(f"固定句: {name}", needle in html, f"未找到「{needle}」")
        check("footer meta 行（报告日期）", 'class="meta-line"' in html and "报告日期" in html)
        # 已废弃件回流 = FAIL
        legacy = [k for k in FORBIDDEN_LEGACY_SINGLE if k in html]
        check("单人已废弃件未回流（卡框/速览卡/pull/旧图件等）", not legacy,
              "出现: " + ", ".join(legacy[:8]))

    # 4. meter-fill CSS（仅当报告含评分条时检查，双人组件向后兼容）
    if "meter-bar" in html or "meter-fill" in html:
        m = re.search(r"\.meter-fill\s*\{([^}]*)\}", html)
        css = m.group(1) if m else ""
        ok = m is not None and "display:block" in css.replace(" ", "") and "min-width" in css
        check("meter-fill CSS 修复(display:block + min-width)", ok,
              "缺少 .meter-fill{display:block; min-width:...}")

    # 5. 打印样式
    check("存在 @media print", "@media print" in html)

    # 6. A 纸感样式
    check("存在 @page A4", bool(re.search(r"@page[^{]*\{[^}]*size:\s*A4", html)))
    print_zone = ""
    if "@media print" in html:
        start = html.find("@media print")
        print_zone = html[start: html.find("</style>", start)]
    check("纸纹背景存在（屏幕端 feTurbulence 噪点）", "feTurbulence" in html)
    check("纸纹不打印（print 块去背景图）",
          "background-image" in print_zone and "none" in print_zone)
    check("正文列宽 680px", bool(re.search(r"body\s*\{[^}]*max-width:\s*680px", html)))

    print()
    if failures:
        print(f"共 {len(failures)} 项未通过，请修复后重新 lint。")
        return 1
    print("全部检查通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
