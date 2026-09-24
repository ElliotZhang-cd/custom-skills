#!/usr/bin/env python3
"""BFI-2 分数计算：原始分 → z / 百分位 / 档位 / 轨道刻度（供模板渲染）

这是「模型算好再注入」的执行器，也是 lint 复算的依据。z 分由本脚本用
skill 内置常模（references/bfi2_norms_cn.json，Zhang et al. 2022 Table 1）计算；
外部输入里带的任何 z/等级/M/SD 一律忽略。

用法：
  python scripts/compute_scores.py --export <bfi2_results.json> [--norm cn_college]
  python scripts/compute_scores.py --scores <simple_scores.json> [--norm cn_college]
  python scripts/compute_scores.py --couple <A.json> <B.json> [--norm cn_college]
  两种输入任选其一；--norm 默认 cn_college。--couple 输出 A/B 统计 + Δz +
  选桥/共鸣复算（口径与双人模板 HTML 的 JS 规则严格一致，供 Phase 0 回显与 lint 复算）。

输入 A：平台导出 JSON（计分平台固定输出，含 scores 字段）
  含 scores.raw（负性情绪方向）与 scores.stability（情绪稳定性方向）两份副本，
  每条形如 {"label":..., "score":...}，第4域 facets 始终本义方向。
  → 自动取 scores.stability.domains / .facets（direction_convention 已声明稳定性方向）。

输入 B：扁平分数（手工整理的表）
  {
    "negative_emotionality": 3.25,        # 或 "emotional_stability": 2.75，脚本自动识别方向
    "extraversion": 2.42, "agreeableness": 4.0, "conscientiousness": 3.0, "open_mindedness": 4.0,
    "facets": {"sociability": 2.25, ... 15 项英文键 或 社交/果断/... 15 项中文 label ...}
  }
  第4域也接受中文键："情绪稳定性"（稳定性方向）/"负性情绪"（负性方向），其余四域接受中文域名。

输出（JSON → stdout 或 --out 文件）：
{
  "norm_key": "cn_college",
  "domains": { "<domain_key>": {"label","score","z","pct","band"}, ... },
  "facets":  { "<facet_key>":  {"label","score","z","pct","band","tick_pct"}, ... }
}

换算规则（scoring-interpretation.md §1.2/§1.3、html-templates 新版）：
- z = (score − M) / SD，四舍五入 2 位（判档/展示口径一致）
- 第4域按「情绪稳定性」方向：M′ = 6 − M(负性情绪)，z 用稳定性方向 score 对 M′ 算；
  score 用 6 − raw 得稳定性方向分（两法等价）
- 焦虑/抑郁/易变（anxiety/depression/emotional_volatility）恒为本义方向（高=更敏感），不翻转
- pct = round(Φ(z) × 100)，band 五档与扁平/矛盾/双人阈值见 references/thresholds.json（单一真相源）
- tick_pct = M/5×100（子维度轨道上人群平均位置的百分比刻度）
"""

import argparse
import json
import math
import sys
from pathlib import Path

# 静默失效阈值的唯一真相源（档位切分、扁平/矛盾/极端判定、双人 Δz）——
# 本脚本与 lint_report.py 都从这里读，不得各自硬编码一份。
THRESHOLDS_PATH = Path(__file__).resolve().parent.parent / "references" / "thresholds.json"
TH = json.loads(THRESHOLDS_PATH.read_text(encoding="utf-8"))

# 域常模键（与 bfi2_norms_cn.json.domains 一致）
DOMAIN_LABELS = {"extraversion": "外向性", "agreeableness": "宜人性",
                 "conscientiousness": "尽责性", "negative_emotionality": "情绪稳定性",
                 "open_mindedness": "开放性"}
# 稳定性方向展示时第4域用 emotional_stability 作 key（对齐平台导出 stability.domains）
STAB_KEY = "emotional_stability"

# 中文 label → 英文 facet key（输入 B 允许中文）
FACET_LABEL_TO_KEY = {
    "社交": "sociability", "果断": "assertiveness", "活力": "energy_level",
    "同情": "compassion", "谦恭": "respectfulness", "信任": "trust",
    "条理": "organization", "效率": "productiveness", "负责": "responsibility",
    "焦虑": "anxiety", "抑郁": "depression", "易变": "emotional_volatility",
    "好奇": "intellectual_curiosity", "审美": "aesthetic_sensitivity", "想象": "creative_imagination",
}
FACET_KEYS = list(FACET_LABEL_TO_KEY.values())


def phi(z: float) -> float:
    """标准正态累计分布（Abramowitz–Stegun 26.2.19，误差 <1e-7）。"""
    t = 1 / (1 + 0.2316419 * abs(z))
    d = 0.3989423 * math.exp(-z * z / 2)
    p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))))
    p = 1 - p
    return 1 - p if z < 0 else p


def band_of(pct: int) -> str:
    """五档判定。切分点与档名来自 thresholds.json（单一真相源）。"""
    cuts, labels = TH["bands"]["cuts"], TH["bands"]["labels"]
    for cut, label in zip(cuts, labels):
        if pct < cut:
            return label
    return labels[-1]


def stats_for(score_stab_dir: float, M: float, SD: float):
    """按稳定性方向 score 与已翻好的 M 算 z/pct/band。score/M 必须同方向。"""
    z = round((score_stab_dir - M) / SD, 2)
    pct = round(phi(z) * 100)
    return z, pct, band_of(pct)


def load_norm(norms_all: dict, norm_key: str):
    if norm_key not in norms_all:
        sys.exit(f"ERROR: 常模 '{norm_key}' 不存在，可选：{list(norms_all)}")
    return norms_all[norm_key]


def parse_export(data: dict) -> dict:
    """平台导出 JSON → {domain_key: score, 'facets': {facet_key: score}}（第4域取稳定性方向）。"""
    if "scores" not in data or not isinstance(data["scores"], dict):
        sys.exit("ERROR: 导出缺 scores 字段（应为 {raw, stability}）")
    block = data["scores"].get("stability")
    if not block:
        sys.exit("ERROR: 导出缺 scores.stability（若只有 raw，请确认后改用 --scores 输入并标注方向）")
    out = {"facets": {}}
    for k, v in block.get("domains", {}).items():
        score = v["score"] if isinstance(v, dict) else v
        # stability.domains 第4域 key 应为 emotional_stability，映射回 negative_emotionality 常模
        norm_key = "negative_emotionality" if k in ("emotional_stability", "negative_emotionality") else k
        out[norm_key] = {"score": score, "stab_dir": True}
    for k, v in block.get("facets", {}).items():
        score = v["score"] if isinstance(v, dict) else v
        out["facets"][k] = score
    return out


def parse_flat(data: dict) -> dict:
    """扁平分数（手工表）→ 同结构。自动识别第4域方向（英文键或中文标签均可）。"""
    out = {"facets": {}}
    if "negative_emotionality" in data:
        out["negative_emotionality"] = {"score": data["negative_emotionality"], "stab_dir": False}
    elif "emotional_stability" in data:
        out["negative_emotionality"] = {"score": data["emotional_stability"], "stab_dir": True}
    elif "负性情绪" in data:
        out["negative_emotionality"] = {"score": data["负性情绪"], "stab_dir": False}
    elif "情绪稳定性" in data:
        out["negative_emotionality"] = {"score": data["情绪稳定性"], "stab_dir": True}
    else:
        sys.exit("ERROR: 缺第4域（negative_emotionality / emotional_stability / 负性情绪 / 情绪稳定性）")
    for zh, en in [("外向性", "extraversion"), ("宜人性", "agreeableness"),
                   ("尽责性", "conscientiousness"), ("开放性", "open_mindedness")]:
        if en in data:
            out[en] = {"score": data[en], "stab_dir": True}
        elif zh in data:
            out[en] = {"score": data[zh], "stab_dir": True}
    raw_facets = data.get("facets", {})
    for k, v in raw_facets.items():
        fk = k if k in FACET_KEYS else FACET_LABEL_TO_KEY.get(k)
        if fk is None:
            print(f"WARN: 未知子维度 '{k}'，跳过", file=sys.stderr)
            continue
        out["facets"][fk] = v["score"] if isinstance(v, dict) else v
    return out


def compute(parsed: dict, norm: dict) -> dict:
    dom_M = norm["domains"]
    dom_out = {}
    order = ["extraversion", "agreeableness", "conscientiousness", "negative_emotionality", "open_mindedness"]
    for k in order:
        if k not in parsed:
            sys.exit(f"ERROR: 缺维度 '{k}'")
        score = parsed[k]["score"]
        stab = parsed[k]["stab_dir"]
        M = dom_M[k]["M"]; SD = dom_M[k]["SD"]
        if k == "negative_emotionality":
            # 常模存的是负性情绪方向；统一翻到稳定性方向计算
            M_stab = 6 - M
            score_stab = score if stab else 6 - score
            disp_key = STAB_KEY
        else:
            M_stab = M
            score_stab = score
            disp_key = k
        z, pct, band = stats_for(round(score_stab, 2), M_stab, SD)
        dom_out[disp_key] = {
            "label": DOMAIN_LABELS[k],
            "score": round(score_stab, 2),
            "z": z, "pct": pct, "band": band,
        }

    fac_M = norm["facets"]
    fac_out = {}
    for fk in FACET_KEYS:
        if fk not in parsed["facets"]:
            sys.exit(f"ERROR: 缺子维度 '{fk}'")
        score = parsed["facets"][fk]
        M = fac_M[fk]["M"]; SD = fac_M[fk]["SD"]
        z, pct, band = stats_for(round(score, 2), M, SD)
        label = next((zl for zl, ek in FACET_LABEL_TO_KEY.items() if ek == fk), fk)
        fac_out[fk] = {
            "label": label,
            "score": round(score, 2),
            "z": z, "pct": pct, "band": band,
            "tick_pct": round(M / 5 * 100, 1),
        }
    return {"norm_key": None, "domains": dom_out, "facets": fac_out}


def couple_select(res_a: dict, res_b: dict, norm: dict) -> dict:
    """双人选桥/共鸣复算（与模板 HTML 的 JS 规则逐行同构，用于 Phase 0 回显与 lint 复算）。

    数值口径：HTML 的 normalize() 不四舍五入 z——pct/band/Δz 全用全精度 z，
    展示时才 toFixed(2)。本函数镜像该口径：**阈值与排序用全精度 Δz，输出 dz 才四舍五入到 2 位**
    （与单人的"round 后再算"有意不同，两侧各自与其渲染器严格一致）。
    """
    order = list(FACET_LABEL_TO_KEY.items())  # [(中文, facet key)]，顺序 = HTML facet 序
    pairs = []
    for zl, fk in order:
        a = res_a["facets"][fk]; b = res_b["facets"][fk]
        fn = norm["facets"][fk]
        za_full = (a["score"] - fn["M"]) / fn["SD"]
        zb_full = (b["score"] - fn["M"]) / fn["SD"]
        band_a = band_of(round(phi(za_full) * 100))
        band_b = band_of(round(phi(zb_full) * 100))
        dz_full = abs(za_full - zb_full)
        pairs.append({"name": zl, "a": a["score"], "b": b["score"],
                      "za": round(za_full, 2), "zb": round(zb_full, 2),
                      "bandA": band_a, "bandB": band_b,
                      "dz": round(dz_full, 2), "dz_full": dz_full})
    cp = TH["couple"]
    ranked = sorted(pairs, key=lambda x: -x["dz_full"])
    # 下限 0：不硬凑，空集合由模板渲染「同频声明」空态
    bridges = [x for x in ranked if x["dz_full"] >= cp["bridge_dz_min"]][:cp["bridge_max_count"]]
    resonance = sorted([x for x in pairs
                        if x["dz_full"] <= cp["resonance_dz_max"] and x["bandA"] == x["bandB"]],
                       key=lambda x: x["dz_full"])[:cp["resonance_max_count"]]
    return {"pairs": pairs,
            "bridges": [{"name": x["name"], "dz": x["dz"]} for x in bridges],
            "resonance": [{"name": x["name"], "dz": x["dz"]} for x in resonance]}


def load_person_data(path: Path, norm: dict):
    """单人输入（export 或扁平）→ parsed → compute。供 --couple 复用。"""
    data = json.loads(path.read_text(encoding="utf-8"))
    parsed = parse_export(data) if ("scores" in data) else parse_flat(data)
    return compute(parsed, norm)


def main():
    ap = argparse.ArgumentParser(description="BFI-2 原始分 → z/百分位/档位；--couple 输出双人统计")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--export", help="平台导出 JSON（含 scores.stability，自动取稳定性方向）")
    src.add_argument("--scores", help="扁平分数 JSON（固定文本表先转此格式；自动识别第4域方向）")
    src.add_argument("--couple", nargs=2, metavar=("A.json", "B.json"),
                     help="双人两份分数文件（export 或扁平均可），输出 A/B 统计 + Δz + 选桥/共鸣（复算口径同模板 HTML）")
    ap.add_argument("--norm", default="cn_college",
                    choices=["cn_college", "cn_employee", "cn_adolescent"])
    ap.add_argument("--out", help="输出文件路径（默认 stdout）")
    args = ap.parse_args()

    norms_path = Path(__file__).parent.parent / "references" / "bfi2_norms_cn.json"
    norms_all = json.loads(norms_path.read_text(encoding="utf-8"))["norms"]
    norm = load_norm(norms_all, args.norm)

    if args.couple:
        fa, fb = (Path(x) for x in args.couple)
        res_a = load_person_data(fa, norm)
        res_b = load_person_data(fb, norm)
        result = {"mode": "couple", "norm_key": args.norm,
                  "a": res_a, "b": res_b,
                  **couple_select(res_a, res_b, norm)}
    else:
        src_path = Path(args.export or args.scores)
        data = json.loads(src_path.read_text(encoding="utf-8"))
        parsed = parse_export(data) if args.export else parse_flat(data)
        result = compute(parsed, norm)
        result["norm_key"] = args.norm

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"WROTE {args.out}", file=sys.stderr)
    print(text)


if __name__ == "__main__":
    main()
