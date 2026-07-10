---
name: mbti-analyst
description: Use when the user provides Jungian 8-function cognitive scores (荣格八维), MBTI test results, or asks about 人格分析 / 认知功能 / 依恋类型 / 恋爱适配 / 八维分析 / 荣格分析. Also trigger on data from soulstation.club/8function. Chinese keywords: 八维, MBTI, 荣格, 人格分析, 依恋, 恋爱适配, 认知功能, 适配性, 荣格八维.
---

# MbtiAnalyst — 认知功能人格分析与恋爱适配

## Overview

This skill performs Jungian cognitive function analysis based on 8-function test scores. For a single subject, it produces a full personality analysis report. For two subjects, it additionally produces a romantic compatibility analysis. All output is formatted as styled HTML documents.

**Test data source**: `https://soulstation.club/8function/do70`

**Input**: 8 cognitive function scores (Fi, Ni, Fe, Ti, Te, Ne, Se, Si). May be accompanied by age, gender, relationship context, or self-reported MBTI/attachment type.

**Output**: One or more HTML reports saved to the user's specified path (default: Desktop).

## Workflow

### Phase 0: Input Parsing

Extract from user input:
- 8 function scores (required). If scores are embedded in a paragraph, extract each function-score pair.
- **Default score order**: If the user provides scores without labeling which score corresponds to which function (e.g., raw comma-separated numbers or a screenshot), assume the default order is: **Se, Si, Ne, Ni, Te, Ti, Fe, Fi**. This matches the output format of `soulstation.club/8function/do70` and similar Chinese 8-function tests. Always confirm with the user if the order is ambiguous.
- Number of subjects (1 or 2 sets of scores)
- Age, gender, relationship duration (optional)
- Self-reported MBTI type (optional — will be independently inferred regardless)
- Self-reported attachment style (optional — takes precedence over inference if specified)
- Output path (optional — default to desktop: `/mnt/c/Users/elliot/Desktop/` on WSL, or ask user)

### Phase 1: Single-Subject Core Analysis

For each subject, perform:

**Step 1 — Gradient Tiering**
- Sort 8 functions by score descending. Compute Δ between adjacent scores.
- Apply Δ thresholds: Δ≤3 → co-equal; Δ 3-5 → approximate; Δ>8 → tier boundary.
- Group into T1–T4 tiers. See `references/scoring-algorithm.md` §1.

**Step 2 — MBTI Type Inference**
- Match observed function rank-order against the 16 standard stacks.
- Check shadow function distribution (Beebe positions 5-8) for anomalies.
- Rank candidates by parsimony (fewest additional assumptions required).
- Output: top 2 types with probability percentages + supporting rationale + acknowledged difficulties.
- See `references/scoring-algorithm.md` §2 for full matrix.

**Step 3 — Attachment Style Inference**
- From Fe/Fi gap, Si level, and Ni-Fi loop presence, infer attachment dimensions (anxiety × avoidance).
- Identify relationship-domain specificity (romantic partner vs. parents/family) — this is mandatory, not optional.
- If user has specified actual attachment behavior, adopt user's specification and use function analysis only for explanation.
- See `references/attachment-inference.md` for full mapping rules.

### Phase 2: Single-Subject Report Generation

Generate one HTML file per subject containing these 7 mandatory chapters:

1. **原始数据与梯度分层** — bar chart + tier boxes + key structural findings
2. **MBTI类型推断** — two-type comparison with match tables, Occam's razor argument, final diagnostic callout
3. **人格画像** — core psychodynamic, emotional duality, thinking style, intuition channels, physical-world interface
4. **优势与短板** — dual-column layout
5. **成长环境推断** — per-function environmental hypotheses + integrated portrait (always preceded by disclaimer)
6. **依恋类型推断** — romantic vs. parental domain analysis, with Bartholomew quadrant positioning
7. **成长建议** — prioritized by weakest function, concrete steps

Optional 8th chapter (add only if user explicitly requests or data supports it):
8. **现代心理学框架再分析** — Big Five mapping, SDT basic needs, Gross emotion regulation, modern attachment dimensions, McAdams narrative identity

### Phase 3: Couple Compatibility Analysis (only when 2 subjects)

Generate a separate HTML file containing:

1. **双方核心结构特征** — dual-column cards with key parameters + structural conclusions
2. **八维度适配性分析** — each dimension with score, analysis, and at least one concrete 📋 scene with dialogue
3. **综合适配性评估** — 8-bar meter chart + detailed integrated assessment callout
4. **恋爱过程推演** — 4 phases WITHOUT time information, each with scene examples and a logic validity check at Phase 3
5. **典型恋爱冲突** — 4+ conflicts, each with: function collision title, frequency/destructiveness/solvability tags, 📋 dialogue scene, functional analysis
6. **典型恋爱风险** — 3-5 risks, each with: risk level, mechanism, escalation scene (early→mid→late), warning signs
7. **解决办法** — 5 categories of solutions, each with: goal, steps, dialogue example showing successful execution
8. **结语** — plain language (NO jargon, NO function abbreviations, NO type labels), rewritten so anyone can understand

See `references/couple-dynamics.md` for dimension definitions, scoring rubrics, and templates.

### Phase 4: User Feedback Integration

After presenting reports, actively invite:
- Challenges to type inference (e.g., "could this be ENTP instead?") — re-evaluate and adjust probabilities
- Clarification of attachment behavior — if user provides specific romantic/family patterns, update report
- Requests for format/style changes in HTML output

## Mandatory Constraints

### Style
- Academic, objective tone. Fair and impartial. No reassurance language ("you should feel good about...").
- All inferences labeled as inferences. No presentation of theoretical deduction as established fact.

### Score Handling
- Similar scores (Δ≤3) treated as co-equal. Small gaps (Δ<5) treated as approximate.
- Focus on gradient tiers and structural breaks (Δ>8), not absolute rankings.
- Never claim a single score is "superior" based on 1-2 point differences.

### Type Inference
- Always provide TWO most likely types with probability percentages.
- Always acknowledge uncertainty and alternative hypotheses.
- Never present a single type as definitive unless function-stack match is near-perfect.

### Attachment Inference
- Always distinguish romantic partner vs. parent/family domains.
- Mark all attachment inferences as "推测" (theoretical inference) unless confirmed by user.
- Include disclaimer: "需结合 ECR-R 或 AAI 进行正式评估" for attachment conclusions.

### HTML Output
- Must use inline CSS with the color variable system defined in `references/html-templates.md`.
- Bar charts must use `display:block` + `min-width:4px` on `.meter-fill` elements.
- Must be responsive (mobile-friendly).
- Must end with disclaimer: "本报告基于认知功能测评数据的理论分析，不构成临床诊断。"

### Couple Reports
- All conflicts and scenes must annotate cognitive function roots.
- Scene dialogues must be specific — who said what, not abstract descriptions.
- Phase 3 (pattern crystallization) must include a logic validity check.
- Conclusion (结语) must be in plain language — zero jargon, zero function codes, zero type labels.

## References

- `references/scoring-algorithm.md` — Gradient tiering rules, MBTI stack matrices, Beebe archetype positions, common deviation patterns
- `references/attachment-inference.md` — Cognitive-function-to-attachment mapping, domain-specificity rules, inference boundaries
- `references/couple-dynamics.md` — Eight-dimension definitions, scoring rubrics, phase/conflict/risk/solution templates
- `references/html-templates.md` — CSS variable system, component classes, bar chart implementation, report structure templates

## Examples

- `examples/cognitive_analysis.html` — Single-subject analysis (Subject 1: INFJ, Fi 67.86/Ni 65.54/Fe 53.94/Ti 50.46/Te 47.56/Ne 41.86/Se 41.76/Si 37.11)
- `examples/cognitive_analysis_2.html` — Single-subject analysis (Subject 2: INTP/ENTP, Ti 64.95/Ne 62.06/Fi 58.00/Te 56.26/Ni 54.52/Si 46.40/Se 34.79/Fe 29.00)
- `examples/couple_compatibility.html` — Couple compatibility analysis (Subject 1 + Subject 2, 5-month relationship)
