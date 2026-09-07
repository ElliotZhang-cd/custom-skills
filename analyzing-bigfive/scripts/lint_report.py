#!/usr/bin/env python3
"""BFI-2 报告 HTML 质量检查（v3）

三种报告自动分流：
- 新版单人：含 `const REPORT = ` → lint_new_single（schema + 常模复算 z/pct/tick + 档位标签 + 禁词 + 固定结构）
- 新版双人：含 `const COUPLE_CONTENT = ` → lint_new_couple（内嵌分数抽取 + 浏览器端计算契约
  + Δz/选桥/共鸣复算 + 内容 schema + 双人禁词 + 固定结构）
- 旧版（历史文件）：其余 → lint_old（双人过渡期旧版基线；不再维护）

双人数值契约（与 templates/couple-report-template.html 的 JS 口径一致）：
模型只填 40 项原始分与文案；z/pct/band/Δz/选桥/共鸣全部由 HTML 浏览器端计算。
z 用全精度参与档与 Δz，展示时 toFixed(2)（与单人「round 后再算」不同，两侧各自与其渲染器严格一致）。
"""

import json
import os
import re
import sys
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compute_scores  # noqa: E402  复用 phi/band_of/常模键映射

HERE = os.path.dirname(os.path.abspath(__file__))
NORMS_PATH = os.path.join(HERE, "..", "references", "bfi2_norms_cn.json")

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
BANDS = ["远低", "偏低", "中间", "偏高", "远高"]


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
            if [f.get("name") for f in d.get("facets", [])] != FACET_NAMES.get(k):
                fails.append(f"FAIL: 域 {k} 子维度名/顺序错误")
            for f in d.get("facets", []):
                for fld in ("score", "z", "pct", "tick", "line"):
                    if fld not in f:
                        fails.append(f"FAIL: {k}/{f.get('name')} 缺字段 {fld}")
            if len(d.get("behaviors", [])) != 3:
                fails.append(f"FAIL: 域 {k} behaviors 应为 3 条")
            for b in d.get("behaviors", []):
                if not str(b).strip().endswith(("。", "！", "？")):
                    fails.append(f"FAIL: 域 {k} behavior 未以句号结尾：{str(b)[:20]}…")

    cover = rep.get("cover", {})
    if len(cover.get("chips", [])) != 3:
        fails.append("FAIL: 封面标签应为 3 个")
    if not cover.get("oneliner"):
        fails.append("FAIL: 封面缺少一句话")
    for group in ("strengths", "flaws"):
        cards = rep.get(group, [])
        if len(cards) < 2:
            fails.append(f"FAIL: {group} 卡应 ≥2 张")
        for c in cards:
            for fld in ("title", "body", "tags"):
                if fld not in c:
                    fails.append(f"FAIL: {group} 卡缺字段 {fld}")
    love = rep.get("love", {})
    for k, n in (("patterns", 3), ("pitfalls", 3), ("phrases", 3)):
        if len(love.get(k, [])) != n:
            fails.append(f"FAIL: 亲密 {k} 应为 {n} 条")
    if not love.get("partner"):
        fails.append("FAIL: 亲密缺少「给在意的人的一段话」")
    if len(rep.get("growth", {}).get("cards", [])) < 3:
        fails.append("FAIL: 成长卡应 ≥3 条")
    if len(rep.get("faq", [])) < 3:
        fails.append("FAIL: FAQ 应 ≥3 问")
    if rep.get("meta", {}).get("alias") in (None, "", "示例"):
        fails.append("FAIL: meta.alias（来访者代号）缺失")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(rep.get("meta", {}).get("date", ""))):
        fails.append("FAIL: meta.date 应为 YYYY-MM-DD")

    # 常模复算
    try:
        all_norms = json.load(open(NORMS_PATH, encoding="utf-8"))["norms"]
        norm_key = rep["meta"].get("normId", "cn_college")
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
                z = round((d["score"] - M) / nm["SD"], 2)
                pct = round(phi(z) * 100)
                if abs(d["z"] - z) > 0.005:
                    fails.append(f"FAIL: 域 {k} z 应为 {z}（常模复算），实际 {d['z']}")
                if d["pct"] != pct:
                    fails.append(f"FAIL: 域 {k} pct 应为 {pct}（常模复算），实际 {d['pct']}")
            for d in doms or []:
                for f in d.get("facets", []):
                    fk = LABEL_TO_NORMKEY.get(f.get("name"))
                    if not fk:
                        continue
                    fn = n["facets"][fk]
                    z = round((f["score"] - fn["M"]) / fn["SD"], 2)
                    pct = round(phi(z) * 100)
                    tick = round(fn["M"] / 5 * 100, 1)
                    if abs(f["z"] - z) > 0.005:
                        fails.append(f"FAIL: 子维度 {f['name']} z 应为 {z}，实际 {f['z']}")
                    if f["pct"] != pct:
                        fails.append(f"FAIL: 子维度 {f['name']} pct 应为 {pct}，实际 {f['pct']}")
                    if abs(f.get("tick", -1) - tick) > 0.05:
                        fails.append(f"FAIL: 子维度 {f['name']} tick 应为 {tick}，实际 {f.get('tick')}")
    except OSError as e:
        fails.append(f"FAIL: 常模文件读取失败：{e}")

    # 档位标签一致性
    if doms:
        pct_by_name = {}
        for d in doms:
            pct_by_name[d["name"]] = d["pct"]
            for f in d.get("facets", []):
                pct_by_name[f["name"]] = f["pct"]
        for group in ("strengths", "flaws"):
            for c in rep.get(group, []):
                for tag in c.get("tags", []):
                    m = re.match(r"^(.+?) · (远低|偏低|中间|偏高|远高)$", str(tag))
                    if m and m.group(1) in pct_by_name and band_of(pct_by_name[m.group(1)]) != m.group(2):
                        fails.append(f"FAIL: {group}「{tag}」与实际百分位 {pct_by_name[m.group(1)]}%（应为 {band_of(pct_by_name[m.group(1)])}）不符")

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
                    if [f.get("name") for f in d.get("facets", [])] != FACET_NAMES.get(d.get("key")):
                        fails.append(f"FAIL: {side.upper()}/{d.get('key')} 子维度名/顺序错误")
                    for f in d.get("facets", []):
                        if not (1 <= f.get("score", 0) <= 5):
                            fails.append(f"FAIL: {side.upper()}/{f.get('name')} 分数字越界")
                        s_map[f["name"]] = f["score"]
                scores[side] = s_map
        except json.JSONDecodeError as e:
            fails.append(f"FAIL: P 分数块解析失败：{e}")

    # ---- 浏览器端契约：不得有服务端注入 z ----
    if re.search(r"z\s*:\s*[-+]?\d", html):
        fails.append("FAIL: 双人契约=浏览器端计算：P 数据块不得注入 z/pct（z: 字段不应出现在 HTML 数据区）")

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
            exp_bridges = [x for x in ranked if x["dz"] >= 0.7][:6]  # 下限 0：与模板一致，不硬凑
            exp_reso = sorted([x for x in pairs if x["dz"] <= 0.35 and x["bandA"] == x["bandB"]],
                              key=lambda x: x["dz"])[:3]
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
        cv = C.get("cover", {})
        if not (1 <= len(cv.get("chips", [])) <= 3):
            fails.append("FAIL: 双人封面 chips 应为 1–3 个")
        if not str(cv.get("oneliner", "")).strip():
            fails.append("FAIL: 双人封面缺 oneliner")
        ps = C.get("personas", {})
        for side in ("a", "b", "A", "B"):
            if side in ps:
                for fld in ("defaultReaction", "mostMisread"):
                    if len(str(ps[side].get(fld, "")).strip()) < 6:
                        fails.append(f"FAIL: personas.{side}.{fld} 过短")
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
    for anchor in ("hero", "ch-guide", "ch-a", "ch-b", "ch-snapshot", "ch-bridges",
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

def lint_old(filepath, html):
    fails = []
    old_forbidden = [
        "情绪温度计", "信任基石", "效率引擎", "稳定性指标", "神经质", "负性情绪",
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
    for w in old_forbidden:
        if w in html:
            fails.append(f"FAIL(旧): forbidden word '{w}'")
    if "怎么读这份报告" not in html:
        fails.append("FAIL(旧): 缺少阅读指南")
    if "不构成临床诊断" not in html:
        fails.append("FAIL(旧): 缺少局限声明")
    basename = os.path.basename(filepath)
    if len(basename.split("_")) > 2:
        if "p1-tag" not in html or "p2-tag" not in html:
            fails.append("FAIL(旧): 双人报告须含 .p1-tag 与 .p2-tag")
        if "这份报告基于双方的人格测评数据分析" not in html:
            fails.append("FAIL(旧): 双人缺少伦理声明")
        for cls in ("meters-table", "meter", "scard"):
            if cls not in html:
                fails.append(f"FAIL(旧): 双人缺少 .{cls}")
    return fails


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
        kind, fails = "旧版", lint_old(fp, html)
    if fails:
        for msg in fails:
            print(msg)
        print(f"\n{len(fails)} check(s) FAILED（{kind}）")
        sys.exit(1)
    print(f"PASS: all checks passed（{kind}）")
    sys.exit(0)


if __name__ == "__main__":
    main()
