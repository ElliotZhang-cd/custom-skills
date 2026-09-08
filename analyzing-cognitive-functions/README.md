# analyzing-cognitive-functions

荣格八维（认知功能）人格分析与恋爱适配——把来访者用本地测试页产出的 8 项功能分数，解读成一份来访者可直接阅读的 HTML 报告、一份可复用的得分 JSON，并在对话中向咨询师输出【咨询师备注】。

## Structure

```text
analyzing-cognitive-functions/
├── SKILL.md
├── README.md
├── references/
├── scripts/
├── examples/
├── docs/
└── evals/
```

- `SKILL.md` — 入口：Goal / Workflow（Phase 0–4）/ Success criteria / Stop rules
- `references/input-parsing.md` — 两种输入格式解析、归一化、代号规则、得分 JSON schema
- `references/scoring-algorithm.md` — 轴结构分析与类型推断算法（含输入质量检查）
- `references/couple-report.md` — 双人（恋人）报告规则（JS 数据驱动版）
- `references/writing-style.md` — 语言规范（读者画像 / 比喻收缩 / 四条轴 / 固定文本块）
- `references/html-templates.md` — 单人报告结构/视觉件规格（hero + 01–07 章）与双人 JS 数据驱动版（§5）
- `scripts/lint_report.py` — 交付前 lint（单人口径 35 项 / 双人口径专项）
- `examples/mbti_sample.html`、`mbti_sampleA_sampleB.html` — 视觉事实源基线样例
- `docs/2026-09-07-couple-report-design.md` — 双人报告设计记录与复现要点
- `evals/evals.json` — 期望行为用例

## Usage

1. 将本目录放入运行时的 skills 目录。
2. 来访者用本地测试页作答，把结果页的「复制分数」文本或「导出结果 JSON」+ 用户代号发给模型。
3. 模型按 `SKILL.md` 的 Workflow 输出：`mbti_<代号>.html` + `mbti_<代号>.json`（默认保存到用户桌面 `~/Desktop/MBTI/`，用户另行指定时从其指定）+ 对话内【咨询师备注】。

**测试数据来源**：本地测试页 `~/Desktop/relations/data/8function_interactive.html`（70 题交互计分，百分制 0-100）；题库与计分公式见同目录 `soulstation_8function_70.json`。

## Verification

```bash
python scripts/lint_report.py <报告文件.html>
python scripts/lint_report.py examples/mbti_sample.html   # 基线回归，必须 PASS
```

