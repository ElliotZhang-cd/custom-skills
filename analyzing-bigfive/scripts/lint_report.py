#!/usr/bin/env python3
"""BFI-2 报告 HTML 质量检查（v3）

两种报告自动分流：
- 新版单人：含 `const REPORT = ` → lint_new_single（schema + 常模复算 z/pct/tick + 档位标签 + 禁词 + 固定结构）
- 新版双人：含 `const COUPLE_CONTENT = ` → lint_new_couple（内嵌分数抽取 + 浏览器端计算契约
  + Δz/选桥/共鸣复算 + 内容 schema + 双人禁词 + 固定结构）
其余文件直接 FAIL：v2 遗留格式已停止支持（2026-09-09 起 lint_old 分支删除）。

双人数值契约（与 templates/couple-report-template.html 的 JS 口径一致）：
模型只填 40 项原始分与文案；z/pct/band/Δz/选桥/共鸣全部由 HTML 浏览器端计算。
z 用全精度参与档与 Δz，展示时 toFixed(2)（与单人「round 后再算」不同，两侧各自与其渲染器严格一致）。
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compute_scores  # noqa: E402  复用 phi/band_of/常模键映射

HERE = os.path.dirname(os.path.abspath(__file__))
NORMS_PATH = os.path.join(HERE, "..", "references", "bfi2_norms_cn.json")
TEMPLATE_PATH = os.path.join(HERE, "..", "templates", "report-template.html")


# ─────────────── 模板一致性（数据块之外不得改动 / 示例文案不得复用）───────────────
# 背景：报告的 CSS 与渲染层是模板的复制品，模型只应替换数据块。此前无任何校验，
# 出现两起真实事故——① 基线样例的雷达 JS 停留在旧公式（无 RADAR_R0），lint 查不出；
# ② 生成的报告逐字沿用模板示例文案（love.h2 / growth.lead / 成长卡 / FAQ），
#    而旧的「未替换模板示例」守卫只在 alias+date+封面文案三项同时命中时才触发，太窄。

def _render_regions(html):
    """报告里必须与模板逐字节一致的两段：`<style>` 块、渲染层（JS 固定部分）。"""
    a, b = html.find("<style>"), html.find("</style>")
    rv = html.rfind("/*", 0, html.find("以下为渲染层"))
    return (html[a:b] if a >= 0 and b > a else ""), (html[rv:] if rv >= 0 else "")


def sample_freetext(rep):
    """数据块里"读者当分析来读"的自由文案（≥12 字），用于检测逐字复用模板示例。
    豁免：partnerTitle（interpretation-library §3.4 规定用语）、partnerCap（功能提示语）、
    tags（格式派生）、meta（常模/方向说明按规范本应一致）。"""
    out = list(rep.get("cover", {}).get("chips", [])) + list(rep.get("cover", {}).get("oneliner", []))
    for d in rep.get("domains", []):
        out.append(d.get("line", ""))
        out += d.get("behaviors", [])
        out += [f.get("line", "") for f in d.get("facets", [])]
    for g in ("strengths", "flaws"):
        for c in rep.get(g, []):
            out += [c.get("title", ""), c.get("body", "")]
    lo = rep.get("love", {})
    out += [lo.get("h2", ""), lo.get("lead", ""), lo.get("partner", "")]
    for k in ("patterns", "pitfalls"):
        out += [x.get("b", "") + x.get("t", "") for x in lo.get(k, [])]
    for p in lo.get("phrases", []):
        out += [p.get("scene", ""), p.get("bad", ""), p.get("good", "")]
    gr = rep.get("growth", {})
    out += [gr.get("h2", ""), gr.get("lead", "")]
    for c in gr.get("cards", []):
        out += [c.get("title", ""), c.get("body", "")]
    for f in rep.get("faq", []):
        out += [f.get("q", ""), f.get("a", "")]
    return [x for x in out if isinstance(x, str) and len(x) >= 12]

# 静默失效阈值（单一真相源 = references/thresholds.json，经 compute_scores 载入）。
# 本文件不得再硬编码这些数值——写错不报错，只会让校验与结论一起走偏。
TH = compute_scores.TH
BAND_ALT = "|".join(TH["bands"]["labels"])          # 档位词正则用（顺序即档序）
FLAT_Z_MAX = TH["single"]["flat_profile_abs_z_max"]
DZ_BRIDGE_MIN = TH["couple"]["bridge_dz_min"]
DZ_RESONANCE_MAX = TH["couple"]["resonance_dz_max"]

# ────────────────────────── 禁词 ──────────────────────────

FORBIDDEN_BASE = [
    "情绪温度计", "信任基石", "效率引擎", "稳定性指标",
    "神经质", "负性情绪",
    "系统", "架构", "机制", "流程", "输入", "输出", "通道", "带宽", "负载",
    "算法", "迭代", "反馈", "模块", "组件", "审查", "监控", "容器", "支架",
    "空转", "宕机", "重启", "调试", "程序", "数据库", "接口", "回路", "闭环",
    "触发器", "运算", "处理器", "默认设置", "双核", "双引擎",
    "认知功能", "心理功能", "感觉功能", "判断功能", "功能栈", "功能结构",
    "意识位置", "在场感", "叙事", "价值标准", "价值判断", "内在安抚",
    "自洽", "感官体验", "感官投入", "收拢",
    "获取和消耗能量", "目标导向行为",
    "咨询师", "会谈", "咨询中",
]
FORBIDDEN_EXCEPTIONS = ["心理咨询师"]
# 双人内容专属禁词（来自内容管线铁律；只扫描模型填写的字符串，模板固定安全文本除外）
FORBIDDEN_COUPLE = ["冷暴力", "你应该", "你总是", "谁对谁错", "匹配分", "伤害", "离开"]

DOMAIN_KEYS = ["es", "ex", "ag", "co", "op"]              # 单人模板显示序
EXPECTED_DOMAIN_META = {                                   # 单人域 key → (固定名称, 固定身份色)
    "es": ("情绪稳定性", "#9A7FB8"), "ex": ("外向性", "#E07A4F"),
    "ag": ("宜人性", "#7C9B6D"), "co": ("尽责性", "#5A7CA6"),
    "op": ("开放性", "#D9A441"),
}
COUPLE_DOM_NAME = {"ex": "外向性", "ag": "宜人性", "co": "尽责性",
                   "es": "情绪稳定性", "op": "开放性"}
COUPLE_DOM_COLOR = {"ex": "var(--e)", "ag": "var(--a)", "co": "var(--c)",
                    "es": "var(--es)", "op": "var(--o)"}
COUPLE_DOM_ORDER = ["ex", "ag", "co", "es", "op"]         # 双人模板 P 序（雷达另轴序）
FACET_NAMES = {
    "es": ["焦虑", "抑郁", "易变"], "ex": ["社交", "果断", "活力"],
    "ag": ["同情", "谦恭", "信任"], "co": ["条理", "效率", "负责"],
    "op": ["好奇", "审美", "想象"],
}
# 双人模板 facet 序（ex,ag,co,es,op 域序）
FACET_ORDER = ["社交", "果断", "活力", "同情", "谦恭", "信任", "条理", "效率",
               "负责", "焦虑", "抑郁", "易变", "好奇", "审美", "想象"]
LABEL_TO_NORMKEY = compute_scores.FACET_LABEL_TO_KEY  # 中文→常模 facet 键


def band_of(pct):
    return compute_scores.band_of(pct)


def phi(z):
    return compute_scores.phi(z)


def find_forbidden(text, extra=()):
    t = text
    for exc in FORBIDDEN_EXCEPTIONS:
        t = t.replace(exc, "〇" * len(exc))
    return [w for w in (FORBIDDEN_BASE + list(extra)) if w in t]


def strings_of(o, acc=None):
    if acc is None:
        acc = []
    if isinstance(o, str):
        acc.append(o)
    elif isinstance(o, list):
        for v in o:
            strings_of(v, acc)
    elif isinstance(o, dict):
        for v in o.values():
            strings_of(v, acc)
    return acc


def _js_const_block(html, decl):
    """返回声明后的平衡花括号内容（JS 字面量 → 可转 JSON），None 表示不存在。"""
    m = re.search(re.escape(decl), html)
    if not m:
        return None
    i = html.find("{", m.end() - 1)
    if i < 0:
        return None
    depth, j = 0, i
    while j < len(html):
        c = html[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    return html[i:j + 1]


def js_to_json(blob):
    """宽松 JS 字面量 → JSON：引号化裸键/单引号串、去尾逗号、`.66`→`0.66`。仅用于数据块（禁注释）。"""
    s = re.sub(r"([{\[,]\s*)([A-Za-z_\u4e00-\u9fff][\w\u4e00-\u9fff]*)\s*:", r'\1"\2":', blob)
    # 单引号字符串 → 双引号（内无单引号转义时安全；数据块按规范不得含引号嵌套）
    s = re.sub(r"'((?:[^'\\]|\\.)*)'", lambda m: '"' + m.group(1).replace('\\"', '"').replace("'", "\\'") + '"', s)
    s = re.sub(r",\s*([}\]])", r"\1", s)
    s = re.sub(r"([:\[,]\s*)(\.\d)", r"\g<1>0\g<2>", s)  # JS 允许 .66，严格 JSON 不允许
    return json.loads(s)


def _check_corr_tag(tag, pct_by_name):
    """校验成长卡标签「对应：<子维度> · <档位>」（可多段用 × 连接）→ 返回错误列表。"""
    body = str(tag)[len("对应："):]
    errs = []
    for term in [x.strip() for x in body.split("×")]:
        m = re.match(r"^([\u4e00-\u9fff]+)\s*·\s*(" + BAND_ALT + r")$", term)
        if not m:
            errs.append(f"格式应为「对应：<子维度> · <档位>」（可多段 × 连接），实际「{term}」")
            continue
        name, band_word = m.group(1), m.group(2)
        if name not in pct_by_name:
            errs.append(f"未知子维度「{name}」")
        elif band_of(pct_by_name[name]) != band_word:
            errs.append(f"{name} 档位应为 {band_of(pct_by_name[name])}（pct {pct_by_name[name]}%），标签写 {band_word}")
    return errs


# ────────────────────────── 新版单人 ──────────────────────────

def lint_new_single(filepath, html):
    fails = []
    blob = _js_const_block(html, "const REPORT = ")
    if blob is None:
        return ["FAIL: 新版报告缺少 `const REPORT =` 数据块"]
    try:
        rep = js_to_json(blob)
    except json.JSONDecodeError as e:
        return [f"FAIL: REPORT 数据块 JSON 解析失败：{e}（数据块内不得写注释）"]

    doms = rep.get("domains")
    if not isinstance(doms, list) or len(doms) != 5:
        fails.append("FAIL: domains 应为 5 个维度")
    else:
        if [d.get("key") for d in doms] != DOMAIN_KEYS:
            fails.append(f"FAIL: 维度顺序应为 es,ex,ag,co,op，实际 {[d.get('key') for d in doms]}")
        for d in doms:
            k = d.get("key")
            for fld in ("name", "color", "score", "z", "pct", "line"):
                if fld not in d:
                    fails.append(f"FAIL: 域 {k} 缺字段 {fld}")
            exp = EXPECTED_DOMAIN_META.get(k)
            if exp:
                if d.get("name") != exp[0]:
                    fails.append(f"FAIL: 域 {k} 名称应为 {exp[0]}，实际 {d.get('name')}")
                if str(d.get("color", "")).upper() != exp[1].upper():
                    fails.append(f"FAIL: 域 {k} 颜色应为 {exp[1]}，实际 {d.get('color')}")
            if not (isinstance(d.get("score"), (int, float)) and 1 <= d["score"] <= 5):
                fails.append(f"FAIL: 域 {k} score 应在 1–5，实际 {d.get('score')!r}")
            if [f.get("name") for f in d.get("facets", [])] != FACET_NAMES.get(k):
                fails.append(f"FAIL: 域 {k} 子维度名/顺序错误")
            for f in d.get("facets", []):
                for fld in ("score", "z", "pct", "tick", "line"):
                    if fld not in f:
                        fails.append(f"FAIL: {k}/{f.get('name')} 缺字段 {fld}")
                if not (isinstance(f.get("score"), (int, float)) and 1 <= f["score"] <= 5):
                    fails.append(f"FAIL: {k}/{f.get('name')} score 应在 1–5，实际 {f.get('score')!r}")
            if len(d.get("behaviors", [])) != 3:
                fails.append(f"FAIL: 域 {k} behaviors 应为 3 条")
            for b in d.get("behaviors", []):
                core = str(b).strip().rstrip("」』”’）)]】》")   # 允许句末引号/括号收尾
                if not core.endswith(("。", "！", "？")):
                    fails.append(f"FAIL: 域 {k} behavior 未以句号结尾：{str(b)[:20]}…")

    cover = rep.get("cover", {})
    if len(cover.get("chips", [])) != 3:
        fails.append("FAIL: 封面标签应为 3 个")
    if not cover.get("oneliner"):
        fails.append("FAIL: 封面缺少一句话")
    # 扁平剖面判定（先于数量检查：全维度 |z|≤FLAT_Z_MAX → strengths/flaws/growth 放宽为 2–5）
    flat = (isinstance(doms, list) and len(doms) == 5
            and all(isinstance(d.get("z"), (int, float)) for d in doms)
            and all(abs(d["z"]) <= FLAT_Z_MAX for d in doms))
    mn = 2 if flat else 3
    for group in ("strengths", "flaws"):
        cards = rep.get(group, [])
        if not (mn <= len(cards) <= 5):
            fails.append(f"FAIL: {group} 卡应为 {mn}–5 张，实际 {len(cards)}")
        for c in cards:
            for fld in ("title", "body", "tags"):
                if fld not in c:
                    fails.append(f"FAIL: {group} 卡缺字段 {fld}")
    love = rep.get("love", {})
    for k, n in (("patterns", 3), ("pitfalls", 3), ("phrases", 3)):
        if len(love.get(k, [])) != n:
            fails.append(f"FAIL: 亲密 {k} 应为 {n} 条")
    for fld in ("h2", "lead", "partnerTitle"):
        if not str(love.get(fld, "")).strip():
            fails.append(f"FAIL: 亲密缺字段 love.{fld}")
    if not love.get("partner"):
        fails.append("FAIL: 亲密缺少「给在意的人的一段话」")
    growth_cards = rep.get("growth", {}).get("cards", [])
    if not (mn <= len(growth_cards) <= 5):
        fails.append(f"FAIL: 成长卡应为 {mn}–5 条，实际 {len(growth_cards)}")
    if not (3 <= len(rep.get("faq", [])) <= 5):
        fails.append(f"FAIL: FAQ 应为 3–5 问，实际 {len(rep.get('faq', []))}")
    meta = rep.get("meta", {})
    if meta.get("alias") in (None, "", "示例"):
        fails.append("FAIL: meta.alias（来访者代号）缺失")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(meta.get("date", ""))):
        fails.append("FAIL: meta.date 应为 YYYY-MM-DD")
    for fld in ("normId", "normLabel", "normDetail", "domain4Note"):
        if not str(meta.get(fld, "")).strip():
            fails.append(f"FAIL: meta.{fld} 缺失（按所选常模填写）")
    demo = rep.get("demoPct")
    if not (isinstance(demo, (int, float)) and 0 <= demo <= 100):
        fails.append(f"FAIL: demoPct 应为 0–100 的数字，实际 {demo!r}")
    es_dom = next((d for d in (doms or []) if d.get("key") == "es"), None)
    if es_dom is not None and not str(es_dom.get("note", "")).strip():
        fails.append("FAIL: es 域缺 note（方向小注）")
    # 模板一致性：数据块之外的 CSS / 渲染层必须与模板逐字节一致；示例文案不得逐字复用
    # （模板自身豁免——它既是源头也是示例；examples 基线已按本规则清理，不豁免）
    if os.path.basename(filepath) != "report-template.html" and os.path.isfile(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, encoding="utf-8") as f:
            tpl_html = f.read()
        for label, i in (("<style> 块", 0), ("渲染层 JS", 1)):
            if _render_regions(html)[i] != _render_regions(tpl_html)[i]:
                fails.append(f"FAIL: 报告的{label}与 templates/report-template.html 不一致——数据块之外不得改动")
        try:
            tpl_rep = js_to_json(_js_const_block(tpl_html, "const REPORT = "))
            dup = sorted(set(sample_freetext(rep)) & set(sample_freetext(tpl_rep)))
            if dup:
                fails.append(f"FAIL: 逐字复用模板示例文案 {len(dup)} 条（数据块须整块替换），例如「{dup[0][:40]}…」")
        except (json.JSONDecodeError, ValueError):
            pass
    # 扁平剖面：全维度 |z| ≤ FLAT_Z_MAX → 必须给降权提示（01 章渲染）
    if flat and not str(meta.get("qualityNote", "")).strip():
        fails.append(f"FAIL: 扁平剖面（全维度 |z|≤{FLAT_Z_MAX}）必须在 meta.qualityNote 写降权提示")

    # 常模复算
    try:
        all_norms = json.load(open(NORMS_PATH, encoding="utf-8"))["norms"]
        norm_key = meta.get("normId", "cn_college")
        if norm_key not in all_norms:
            fails.append(f"FAIL: 常模 {norm_key} 不存在")
        else:
            n = all_norms[norm_key]
            for d in doms or []:
                k = d.get("key")
                if k not in ("es", "ex", "ag", "co", "op"):
                    continue
                nm = n["domains"][{
                    "ex": "extraversion", "ag": "agreeableness", "co": "conscientiousness",
                    "es": "negative_emotionality", "op": "open_mindedness"}[k]]
                M = (6 - nm["M"]) if k == "es" else nm["M"]
                sc = d.get("score")
                if not isinstance(sc, (int, float)):
                    continue  # 缺 score 已在上方 schema 检查报 FAIL，避免此处崩栈
                z = round((sc - M) / nm["SD"], 2)
                pct = round(phi(z) * 100)
                if not isinstance(d.get("z"), (int, float)) or abs(d["z"] - z) > 0.005:
                    fails.append(f"FAIL: 域 {k} z 应为 {z}（常模复算），实际 {d.get('z')}")
                if d.get("pct") != pct:
                    fails.append(f"FAIL: 域 {k} pct 应为 {pct}（常模复算），实际 {d.get('pct')}")
            for d in doms or []:
                for f in d.get("facets", []):
                    fk = LABEL_TO_NORMKEY.get(f.get("name"))
                    if not fk or not isinstance(f.get("score"), (int, float)):
                        continue
                    fn = n["facets"][fk]
                    z = round((f["score"] - fn["M"]) / fn["SD"], 2)
                    pct = round(phi(z) * 100)
                    tick = round(fn["M"] / 5 * 100, 1)
                    if not isinstance(f.get("z"), (int, float)) or abs(f["z"] - z) > 0.005:
                        fails.append(f"FAIL: 子维度 {f['name']} z 应为 {z}，实际 {f.get('z')}")
                    if f.get("pct") != pct:
                        fails.append(f"FAIL: 子维度 {f['name']} pct 应为 {pct}，实际 {f.get('pct')}")
                    if abs(f.get("tick", -1) - tick) > 0.05:
                        fails.append(f"FAIL: 子维度 {f['name']} tick 应为 {tick}，实际 {f.get('tick')}")
    except OSError as e:
        fails.append(f"FAIL: 常模文件读取失败：{e}")

    # 档位标签一致性（未知名称不再静默跳过）
    pct_by_name = {}
    for d in (doms or []):
        if "name" in d and isinstance(d.get("pct"), (int, float)):
            pct_by_name[d["name"]] = d["pct"]
        for f in d.get("facets", []):
            if "name" in f and isinstance(f.get("pct"), (int, float)):
                pct_by_name[f["name"]] = f["pct"]
    if doms:
        for group in ("strengths", "flaws"):
            for c in rep.get(group, []):
                for tag in c.get("tags", []):
                    m = re.match(r"^(.+?) · (" + BAND_ALT + r")$", str(tag))
                    if not m:
                        continue
                    nm, band_word = m.group(1), m.group(2)
                    if nm not in pct_by_name:
                        fails.append(f"FAIL: {group} 标签「{tag}」中的「{nm}」不是已知维度/子维度名")
                    elif band_of(pct_by_name[nm]) != band_word:
                        fails.append(f"FAIL: {group}「{tag}」与实际百分位 {pct_by_name[nm]}%（应为 {band_of(pct_by_name[nm])}）不符")

    # 成长卡「对应：<子维度> · <档位>」格式与档位一致性
    for c in growth_cards:
        corr = [str(t) for t in c.get("tags", []) if str(t).startswith("对应：")]
        if not corr:
            fails.append(f"FAIL: 成长卡「{c.get('title', '?')}」缺「对应：<子维度> · <档位>」标签")
            continue
        for t in corr:
            for e in _check_corr_tag(t, pct_by_name):
                fails.append(f"FAIL: 成长卡「{c.get('title', '?')}」标签「{t}」：{e}")

    # 禁词：REPORT 字符串值 + 静态可见文本
    scan = " ".join(strings_of(rep))
    txt = re.sub(r"<(style|script|noscript)[^>]*>.*?</\1>", " ", html, flags=re.S)
    txt = re.sub(r"<!--.*?-->", " ", txt, flags=re.S)
    txt = re.sub(r"<[^>]+>", " ", txt)
    for w in find_forbidden(scan + " " + txt):
        fails.append(f"FAIL: 禁词 '{w}' 出现在报告可见文本中")

    # 固定结构
    for probe, label in [("什么时候该认真求助", "求助 callout"), ("不构成任何心理诊断", "免责声明"),
                         ("Zhang et al.", "常模出处")]:
        if probe not in html:
            fails.append(f"FAIL: 缺少{label}（'{probe}'）")
    for anchor in ("hero", "ch-read", "ch-five", "ch-strengths", "ch-love", "ch-growth", "ch-faq"):
        if f'id="{anchor}"' not in html:
            fails.append(f"FAIL: 缺少章节锚点 #{anchor}")
    if "beforeprint" not in html:
        fails.append("FAIL: 缺少 beforeprint 打印展开")
    if "@media print" not in html:
        fails.append("FAIL: 缺少打印样式 @media print")

    basename = os.path.basename(filepath)
    if basename not in ("report-template.html", "bfi2_sample.html"):
        if not re.match(r"^bfi2_[A-Za-z0-9][A-Za-z0-9-]*\.html$", basename):
            fails.append(f"FAIL: 文件名不符规范：{basename}（单人应为 bfi2_{{代号}}.html）")
    return fails


# ────────────────────────── 新版双人 ──────────────────────────

def lint_new_couple(filepath, html):
    fails = []
    basename = os.path.basename(filepath)
    is_template = basename == "couple-report-template.html"
    is_sample = basename == "bfi2_sampleA_sampleB.html"

    blob = _js_const_block(html, "const COUPLE_CONTENT = ")
    if blob is None:
        return ["FAIL: 双人报告缺少 `const COUPLE_CONTENT =` 数据块"]
    content_raw = html[html.find("const COUPLE_CONTENT = "):]
    is_null = bool(re.match(r"const COUPLE_CONTENT\s*=\s*null", content_raw))
    C = None
    if not is_null:
        try:
            C = js_to_json(blob)
        except json.JSONDecodeError as e:
            return [f"FAIL: COUPLE_CONTENT 解析失败：{e}（数据块内不得写注释）"]
    elif not (is_template or is_sample):
        fails.append("FAIL: COUPLE_CONTENT 为 null（交付报告必须填充内容数据块）")

    # ---- P 数据（A/B 原始分，模型填写） ----
    pblob = _js_const_block(html, "const P={")
    if pblob is None:
        pblob = _js_const_block(html, "const P = {")
    scores = {}
    if pblob is None:
        fails.append("FAIL: 缺少双人分数块 `const P={a:…,b:…}`")
    else:
        try:
            P = js_to_json(pblob)
            for side in ("a", "b"):
                p = P.get(side) or {}
                doms = p.get("domains", [])
                if [d.get("key") for d in doms] != COUPLE_DOM_ORDER:
                    fails.append(f"FAIL: {side.upper()} 域顺序应为 ex,ag,co,es,op")
                s_map = {}
                for d in doms:
                    if not (1 <= d.get("score", 0) <= 5):
                        fails.append(f"FAIL: {side.upper()}/{d.get('key')} 域分数越界")
                    if not str(d.get("line", "")).strip():
                        fails.append(f"FAIL: {side.upper()}/{d.get('key')} 缺 line 文案")
                    k = d.get("key")
                    if k in COUPLE_DOM_NAME:
                        if d.get("name") != COUPLE_DOM_NAME[k]:
                            fails.append(f"FAIL: {side.upper()}/{k} 域名称应为 {COUPLE_DOM_NAME[k]}，实际 {d.get('name')}")
                        if str(d.get("color", "")).replace(" ", "") != COUPLE_DOM_COLOR[k]:
                            fails.append(f"FAIL: {side.upper()}/{k} 域颜色应为 {COUPLE_DOM_COLOR[k]}，实际 {d.get('color')}")
                    if [f.get("name") for f in d.get("facets", [])] != FACET_NAMES.get(k):
                        fails.append(f"FAIL: {side.upper()}/{d.get('key')} 子维度名/顺序错误")
                    for f in d.get("facets", []):
                        if not (1 <= f.get("score", 0) <= 5):
                            fails.append(f"FAIL: {side.upper()}/{f.get('name')} 分数字越界")
                        s_map[f["name"]] = f["score"]
                scores[side] = s_map
        except json.JSONDecodeError as e:
            fails.append(f"FAIL: P 分数块解析失败：{e}")

    # ---- 浏览器端契约：不得有服务端注入 z / pct ----
    if re.search(r"\b(?:z|pct)\s*:\s*[-+]?\d", html):
        fails.append("FAIL: 双人契约=浏览器端计算：数据区不得注入 z/pct（`z:` / `pct:` 字段不应出现）")

    # ---- NORM 表 vs 内置常模 JSON ----
    all_norms = json.load(open(NORMS_PATH, encoding="utf-8"))["norms"]
    norm_key = (C or {}).get("meta", {}).get("norm", "cn_college")
    nblob = _js_const_block(html, "const NORM={")
    if nblob is None:
        fails.append("FAIL: 缺少 NORM 常模表")
    else:
        if norm_key not in all_norms:
            fails.append(f"FAIL: meta.norm '{norm_key}' 不存在，可选 {list(all_norms)}")
        else:
            try:
                NH = js_to_json(nblob)
                ref = all_norms[norm_key]
                domkey = {"ex": "extraversion", "ag": "agreeableness", "co": "conscientiousness",
                          "es": "negative_emotionality", "op": "open_mindedness"}
                for k in ("ex", "ag", "co", "es", "op"):
                    hM, hSD = NH["domains"][k]["M"], NH["domains"][k]["SD"]
                    rM = ref["domains"][domkey[k]]["M"]
                    expM = round(6 - rM, 2) if k == "es" else rM
                    if abs(hM - expM) > 0.005 or abs(hSD - ref["domains"][domkey[k]]["SD"]) > 0.005:
                        fails.append(f"FAIL: NORM.domains.{k} 与内置常模不一致（期望 M={expM} SD={ref['domains'][domkey[k]]['SD']}）")
                for name in FACET_ORDER:
                    fk = LABEL_TO_NORMKEY[name]
                    if name not in NH["facets"] or fk not in ref["facets"]:
                        fails.append(f"FAIL: NORM.facets.{name} 缺失")
                        continue
                    if abs(NH["facets"][name]["M"] - ref["facets"][fk]["M"]) > 0.005 or \
                       abs(NH["facets"][name]["SD"] - ref["facets"][fk]["SD"]) > 0.005:
                        fails.append(f"FAIL: NORM.facets.{name} 与内置常模不一致")
            except (json.JSONDecodeError, KeyError) as e:
                fails.append(f"FAIL: NORM 表解析/比对失败：{e}")

    # ---- 选桥/共鸣复算（与模板 HTML 规则一致，用 HTML 内 NORM 全精度口径）----
    if scores.get("a") and scores.get("b"):
        try:
            NH = js_to_json(nblob)
            def stat(fk_name, side_scores):
                fn = NH["facets"][fk_name]
                return (side_scores[fk_name] - fn["M"]) / fn["SD"]
            pairs = []
            for name in FACET_ORDER:
                za, zb = stat(name, scores["a"]), stat(name, scores["b"])
                pa, pb = round(phi(za) * 100), round(phi(zb) * 100)
                pairs.append({"name": name, "dz": abs(za - zb), "bandA": band_of(pa), "bandB": band_of(pb)})
            ranked = sorted(pairs, key=lambda x: -x["dz"])
            # 阈值与模板一致，来自 thresholds.json；下限 0，不硬凑
            exp_bridges = [x for x in ranked if x["dz"] >= DZ_BRIDGE_MIN][:TH["couple"]["bridge_max_count"]]
            exp_reso = sorted([x for x in pairs
                               if x["dz"] <= DZ_RESONANCE_MAX and x["bandA"] == x["bandB"]],
                              key=lambda x: x["dz"])[:TH["couple"]["resonance_max_count"]]
            if C:
                got_b = [b.get("facet") for b in C.get("bridges", [])]
                if set(got_b) != {x["name"] for x in exp_bridges}:
                    fails.append(f"FAIL: 桥集合应为 {sorted(x['name'] for x in exp_bridges)}，实际 {sorted(got_b)}")
                got_r = [r.get("name") for r in C.get("resonance", [])]
                if set(got_r) != {x["name"] for x in exp_reso}:
                    fails.append(f"FAIL: 共鸣集合应为 {sorted(x['name'] for x in exp_reso)}，实际 {sorted(got_r)}")
        except Exception as e:
            fails.append(f"FAIL: 选桥复算失败：{e}")

    # ---- 内容 schema 完整性（模板豁免 null；交付文件必须填充） ----
    if C is not None:
        for k in ("cover", "personas", "resonance", "bridges", "scenes", "letters"):
            if k not in C or C.get(k) in (None, ""):
                # bridges 允许为 []（同频无显著差异）；其余空值视为缺失
                fails.append(f"FAIL: COUPLE_CONTENT 缺少 {k}")
        if not (0 <= len(C.get("bridges", [])) <= 6):
            fails.append(f"FAIL: bridges 数量 {len(C.get('bridges',[]))} 超出 0–6")
        if not (0 <= len(C.get("resonance", [])) <= 3):
            fails.append(f"FAIL: resonance 数量 {len(C.get('resonance',[]))} 超出 0–3")
        cv = C.get("cover", {})
        if not (1 <= len(cv.get("chips", [])) <= 3):
            fails.append("FAIL: 双人封面 chips 应为 1–3 个")
        if not str(cv.get("oneliner", "")).strip():
            fails.append("FAIL: 双人封面缺 oneliner")
        ps = C.get("personas", {})
        if not isinstance(ps, dict):
            fails.append("FAIL: personas 应为对象 {a:{…},b:{…}}")
        else:
            for side, alt in (("a", "A"), ("b", "B")):
                key = side if side in ps else (alt if alt in ps else None)
                if key is None:
                    fails.append(f"FAIL: personas 缺 {side}/{alt} 一侧")
                    continue
                for fld in ("defaultReaction", "mostMisread"):
                    if len(str(ps[key].get(fld, "")).strip()) < 6:
                        fails.append(f"FAIL: personas.{key}.{fld} 过短")
        for b in C.get("bridges", []):
            for fld in ("trigger", "aSide", "bSide", "misread", "translate", "pact"):
                if len(str(b.get(fld, "")).strip()) < 6:
                    fails.append(f"FAIL: 桥 {b.get('facet','?')} 字段 {fld} 过短")
        scene_keys = {s.get("key") for s in C.get("scenes", [])}
        for k in ("周末安排", "消息回复", "家务分配", "压力期陪伴"):
            if k not in scene_keys:
                fails.append(f"FAIL: 场景缺少 {k}")
        for s in C.get("scenes", []):
            for fld in ("a", "b", "misread", "translate"):
                if len(str(s.get(fld, "")).strip()) < 6:
                    fails.append(f"FAIL: 场景 {s.get('key','?')} 字段 {fld} 过短")
            if len(s.get("options", [])) < 2:
                fails.append(f"FAIL: 场景 {s.get('key','?')} options 应 ≥2")
        for fld in ("toA", "toB"):
            if len(str(C.get("letters", {}).get(fld, "")).strip()) < 20:
                fails.append(f"FAIL: letters.{fld} 过短")
        mt = C.get("meta", {})
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(mt.get("date", ""))):
            fails.append("FAIL: meta.date 应为 YYYY-MM-DD")
        for fld in ("aliasA", "aliasB"):
            if not str(mt.get(fld, "")).strip():
                fails.append(f"FAIL: meta.{fld}（代号）缺失")

    # ---- 禁词（仅扫描模型填写的字符串，模板固定安全文本除外） ----
    scan_src = []
    if C is not None:
        scan_src += strings_of(C)
    if scores:  # P 数据块里各域 line 文案
        try:
            P = js_to_json(pblob)
            for side in ("a", "b"):
                for d in P.get(side, {}).get("domains", []):
                    scan_src.append(str(d.get("line", "")))
        except Exception:
            pass
    for w in find_forbidden(" ".join(scan_src), FORBIDDEN_COUPLE):
        fails.append(f"FAIL: 禁词 '{w}' 出现在双人内容中")

    # ---- 固定结构 ----
    for probe, label in [("暂停卡", "冲突三卡·暂停"), ("恢复卡", "冲突三卡·恢复"), ("复盘卡", "冲突三卡·复盘"),
                         ("持续羞辱", "边界安全提示"), ("不构成心理诊断", "免责"), ("Zhang et al.", "常模出处"),
                         ("深青实线", "A 图例"), ("赭棕虚线", "B 图例")]:
        if probe not in html:
            fails.append(f"FAIL: 缺少{label}（'{probe}'）")
    for anchor in ("hero", "ch-guide", "ch-a", "ch-b", "ch-resonance", "ch-bridges",
                   "ch-conflict", "ch-scenes", "ch-letters", "ch-growth", "ch-appendix"):
        if f'id="{anchor}"' not in html:
            fails.append(f"FAIL: 缺少章节锚点 #{anchor}")
    if "@media print" not in html or "beforeprint" not in html:
        fails.append("FAIL: 缺少打印样式/beforeprint")

    # ---- 文件名 ----
    if not (is_template or is_sample):
        if not re.match(r"^bfi2_[A-Za-z0-9][A-Za-z0-9-]*_[A-Za-z0-9][A-Za-z0-9-]*\.html$", basename):
            fails.append(f"FAIL: 双人文件名应为 bfi2_{{代号A}}_{{代号B}}.html，实际 {basename}")
    return fails


# ────────────────────────── 旧版（历史双人基线） ──────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python lint_report.py <report.html>")
        sys.exit(1)
    fp = sys.argv[1]
    if not os.path.isfile(fp):
        print(f"FAIL: file not found: {fp}")
        sys.exit(1)
    with open(fp, encoding="utf-8") as f:
        html = f.read()
    if "const REPORT = " in html:
        kind, fails = "新版单人", lint_new_single(fp, html)
    elif "const COUPLE_CONTENT = " in html:
        kind, fails = "新版双人", lint_new_couple(fp, html)
    else:
        print("FAIL: 不是 v3 报告（缺少 `const REPORT = ` 或 `const COUPLE_CONTENT = ` 标记）；v2 遗留格式已停止支持")
        sys.exit(1)
    if fails:
        for msg in fails:
            print(msg)
        print(f"\n{len(fails)} check(s) FAILED（{kind}）")
        sys.exit(1)
    print(f"PASS: all checks passed（{kind}）")
    sys.exit(0)


if __name__ == "__main__":
    main()
