# SKILL.md Authoring Specification

## Frontmatter

### name

- Gerund structure.
- Lowercase letters, numbers, hyphens only.
- Max 64 characters.
- No XML tags.
- No reserved words `anthropic` or `claude`.

### description

`description` is loaded into the model's context on **every** turn, for **every**
installed skill. It is an ad slot, not a permission slip. Its only job: let the
model decide *load / don't load*. The body does the explaining.

Budget (enforced by `scripts/check-skill.py`):

| Field | Target | Hard fail |
| --- | --- | --- |
| sentences | 2 | > 3 |
| characters | 200 | > 280 |
| trigger signals | 2-3 | — |

Shape:

```text
<Capability: what class of work, what artifact.> Use when <2-3 representative signals>.
```

- Sentence 1 = capability boundary: the *class* of work and the artifact it
  produces. Name the class, not its members.
- Sentence 2 = trigger: 2-3 signals, concrete enough to match on.
- Third person.
- Platform limit is 1024 characters. That is a legality ceiling, never a target.

Rules:

- **Never enumerate features, formats, or actions.** `This includes …`,
  `Triggers include: …`, `Actions: …` and file-format lists are the top cause of
  unusable descriptions. If a skill genuinely covers many formats, say
  "spreadsheet files", not `.xlsx, .xlsm, .xltx, .csv, .tsv`.
- **Never put exclusions in the description.** "Not for X" costs characters on
  every turn and answers a question the model can settle after loading. Put it
  in the body under `Constraints` / out-of-scope.
- Do not summarize the workflow. No step narration.
- Capability first, trigger last. A description that opens with "Use when" fails
  the check.
- Write it **after** the body, from the finished scope. Writing frontmatter
  before the scope exists is why descriptions bloat: the author pre-loads every
  possibility rather than compressing a decision already made.

Good:

```yaml
description: Reviews pull requests for correctness, test coverage, and risky changes. Use when the user asks to review a PR, check a diff, or prepare merge feedback.
```

Bad — 950 characters of inventory, all of it re-checkable after load:

```yaml
description: Use this skill any time a spreadsheet file is the primary input or output. This means any task where the user wants to: open, read, edit, or fix an existing .xlsx, .xlsm, .xltx, .csv, or .tsv file (e.g., adding columns, computing formulas, formatting, charting, cleaning messy data); create a new spreadsheet from scratch ... Triggers include ...
```

The same content, compressed:

```yaml
description: Creates, edits, and analyzes spreadsheet files. Use when a workbook is the input or the deliverable, or when tabular data must be cleaned or converted.
```

## Body

Minimal core:

- Goal
- Workflow
- Success criteria
- Stop rules

Optional:

- Context / Input
- Constraints
- Output Format
- Verification
- Gotchas

Everything cut from the description belongs here: format support, exclusions,
edge-case handling, per-input branches.

## Directory structure

```text
skill-name/
├── SKILL.md
├── README.md
├── references/
├── templates/
├── examples/
└── scripts/
```

## Rules

- Keep SKILL.md concise.
- Use forward slashes.
- Link only files that exist.
- Avoid deep reference chains.
- Avoid Windows paths.
- Avoid redundant rules.

## Verification

Run the mechanical check before calling a skill done:

```bash
python scripts/check-skill.py path/to/skill-dir      # Windows
python3 scripts/check-skill.py path/to/skill-dir     # WSL
```

Exit 0 required. Each warning must be fixed or justified; a surviving warning
needs a reason in the body, not silence.

What is fatal and what is not:

| Finding | Default | `--strict` |
| --- | --- | --- |
| description over budget, no trigger, trigger-first, feature inventory, narration | error | error |
| exclusions in description (`not for`, `不适用`, …) | error | error |
| `name` invalid, reserved word, too long | error | error |
| linked file missing, backslash or Windows path | error | error |
| body missing `Goal` / `Workflow` / `Success criteria` / `Stop rules` | warning | error |
| Chinese enumeration (`包括：`, `例如：`) in description, non-gerund name | warning | warning |

Section names are house style. A skill written as `Overview` / `流程` / `边界` is
not broken, so the default run reports it without failing; a skill generated
*from this template* should still use the canonical names, which is what
`--strict` is for. Description budget violations are always errors — that is the
failure this checker exists for, and it never becomes advisory.

